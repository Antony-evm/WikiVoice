"""RAG service for answering questions using Wikipedia and OpenAI."""

import httpx

from app.config import get_settings
from app.logging_config import get_logger
from domain.responses.query_response import QueryResponse, WikipediaSourceResponse
from infrastructure.query_repository import QueryRepository
from infrastructure.session_repository import SessionRepository
from infrastructure.wikipedia_client import WikipediaClient

logger = get_logger(__name__)

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
TITLE_MAX_LENGTH = 50

SEARCH_EXTRACTION_PROMPT = """Extract the key topic or entity that
 the user wants to learn about from their query.

Rules:
1. Return ONLY the main topic/entity name, nothing else
2. Remove conversational words like "do you know", "tell me about", "what is", etc.
3. Keep proper nouns and brand names exactly as written
4. If the query is already just a topic name, return it as-is
5. For follow-up questions, identify the subject being discussed

Examples:
- "do you know anything about Rolex" → "Rolex"
- "can you tell me about the Eiffel Tower?" → "Eiffel Tower"
- "what is quantum computing" → "quantum computing"
- "I'm curious about Albert Einstein's life" → "Albert Einstein"
- "Rolex" → "Rolex"
- "how does photosynthesis work" → "photosynthesis"
"""

SYSTEM_PROMPT = (
    "You are WikiVoice, a helpful AI assistant that answers questions "
    "using ONLY Wikipedia as your knowledge source.\n\n"
    "CRITICAL RULES:\n"
    "1. You MUST ONLY use information from the provided Wikipedia context\n"
    "2. If no Wikipedia context is provided or it's empty, you MUST say "
    "\"I couldn't find relevant Wikipedia articles for your question. "
    'Please try rephrasing or ask about a different topic."\n'
    "3. NEVER use your internal knowledge to answer questions - "
    "only cite what's in the Wikipedia context\n"
    "4. Keep responses concise but informative - aim for 2-3 paragraphs max\n"
    "5. Always cite which Wikipedia article your information comes from\n"
    "6. Be conversational and friendly since users may be speaking via voice\n\n"
    "You will receive:\n"
    "- WIKIPEDIA CONTEXT: Relevant excerpts from Wikipedia articles "
    "(if empty, decline to answer)\n"
    "- CONVERSATION HISTORY: Previous messages in this conversation\n"
    "- USER QUERY: The current question to answer"
)


class RAGService:
    """RAG service for processing queries with Wikipedia context."""

    def __init__(
        self,
        session_repository: SessionRepository,
        query_repository: QueryRepository,
        wikipedia_client: WikipediaClient,
        http_client: httpx.AsyncClient,
    ):
        self.session_repository = session_repository
        self.query_repository = query_repository
        self.wikipedia_client = wikipedia_client
        self.http_client = http_client
        self.settings = get_settings()

    async def _extract_search_terms(self, query_text: str) -> str:
        """Extract key search terms from a conversational query using OpenAI."""
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SEARCH_EXTRACTION_PROMPT},
                {"role": "user", "content": query_text},
            ],
            "temperature": 0,
            "max_tokens": 50,
        }

        try:
            response = await self.http_client.post(
                OPENAI_CHAT_URL,
                headers=headers,
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            extracted = data["choices"][0]["message"]["content"].strip()
            logger.info(f"Extracted search terms: '{extracted}' from query: '{query_text[:50]}...'")
            return extracted
        except Exception as e:
            logger.warning(f"Search term extraction failed, using original query: {e}")
            return query_text

    async def process_query(
        self,
        session_id: int,
        user_id: int,
        query_text: str,
        input_mode: str = "text",
    ) -> QueryResponse | None:
        """Process a user query and return AI response."""
        session = await self.session_repository.get_session_by_id(session_id)
        if not session or session.user_id != user_id:
            return None

        search_terms = await self._extract_search_terms(query_text)

        wikipedia_context, wikipedia_sources = await self.wikipedia_client.get_context_for_query(
            search_terms
        )

        logger.info(
            f"Wikipedia returned {len(wikipedia_sources)} sources for search terms: "
            f"'{search_terms}'"
        )
        for source in wikipedia_sources:
            logger.info(f"  - {source.title}")

        recent_queries = await self.query_repository.get_recent_queries_by_session_id(
            session_id,
            limit=5,
        )

        messages = self._build_messages(wikipedia_context, recent_queries, query_text)

        response_text = await self._get_openai_response(messages)

        query_record = await self.query_repository.create_query(
            session_id=session_id,
            query_text=query_text,
            response_text=response_text,
            input_mode=input_mode,
        )

        if len(recent_queries) == 0:
            title = (
                query_text[:TITLE_MAX_LENGTH] + "..."
                if len(query_text) > TITLE_MAX_LENGTH
                else query_text
            )
            await self.session_repository.update_session_title(session_id, title)

        sources = []
        if wikipedia_context and wikipedia_sources:
            sources = [WikipediaSourceResponse(title=s.title, url=s.url) for s in wikipedia_sources]

        return QueryResponse(
            query_id=query_record.query_id,
            query_text=query_record.query_text,
            response_text=query_record.response_text,
            input_mode=query_record.input_mode,
            sources=sources,
            created_at=query_record.created_at,
        )

    def _build_messages(
        self,
        wikipedia_context: str,
        conversation_history: list,
        current_query: str,
    ) -> list[dict]:
        """Build the message list for OpenAI API."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        context_message = "WIKIPEDIA CONTEXT:\n"
        if wikipedia_context:
            context_message += wikipedia_context
        else:
            context_message += (
                "(EMPTY - No Wikipedia articles were found. "
                "You must decline to answer and ask the user to rephrase.)"
            )

        context_message += "\n\nCONVERSATION HISTORY:\n"
        if conversation_history:
            for q in conversation_history:
                context_message += f"User: {q.query_text}\nAssistant: {q.response_text}\n\n"
        else:
            context_message += "(This is the start of the conversation)"

        messages.append({"role": "user", "content": context_message})
        messages.append(
            {
                "role": "assistant",
                "content": (
                    "I understand. I'll use the Wikipedia context and "
                    "conversation history to answer questions."
                ),
            }
        )

        messages.append({"role": "user", "content": f"USER QUERY:\n{current_query}"})

        return messages

    async def _get_openai_response(self, messages: list[dict]) -> str:
        """Get response from OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
        }

        try:
            response = await self.http_client.post(
                OPENAI_CHAT_URL,
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.exception(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
            return (
                "I'm sorry, I encountered an error while processing your question. "
                "Please try again."
            )
        except Exception:
            logger.exception("OpenAI request failed")
            return (
                "I'm sorry, I encountered an error while processing your question. "
                "Please try again."
            )

    async def get_conversation_history(
        self,
        session_id: int,
        user_id: int,
    ) -> list[QueryResponse] | None:
        """Get the full conversation history for a session."""
        session = await self.session_repository.get_session_by_id(session_id)
        if not session or session.user_id != user_id:
            return None

        queries = await self.query_repository.get_queries_by_session_id(session_id)
        return [
            QueryResponse(
                query_id=q.query_id,
                query_text=q.query_text,
                response_text=q.response_text,
                input_mode=q.input_mode,
                created_at=q.created_at,
            )
            for q in queries
        ]
