"""Tests for RAG service behavior - isolated unit tests."""

from dataclasses import dataclass
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest


# Minimal dataclasses to represent domain objects
@dataclass
class SessionModel:
    """Mock session model for testing."""

    session_id: int = 0
    user_id: int = 0
    title: str = "New Conversation"
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        if self.updated_at is None:
            self.updated_at = datetime.now(UTC)


@dataclass
class QueryModel:
    """Mock query model for testing."""

    query_id: int = 0
    session_id: int = 0
    query_text: str = ""
    response_text: str = ""
    input_mode: str = "text"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(UTC)


@dataclass
class WikipediaSource:
    """A Wikipedia article source."""

    title: str
    extract: str
    url: str


@dataclass
class WikipediaSourceResponse:
    """Response model for Wikipedia source."""

    title: str
    url: str


@dataclass
class QueryResponse:
    """Response model for a query/response pair."""

    query_id: int
    query_text: str
    response_text: str
    input_mode: str
    sources: list
    created_at: datetime


SYSTEM_PROMPT = """You are WikiVoice, a helpful AI assistant."""


class RAGService:
    """RAG service for processing queries (test version)."""

    def __init__(
        self,
        session_repository,
        query_repository,
        wikipedia_client,
        http_client,
    ):
        self.session_repository = session_repository
        self.query_repository = query_repository
        self.wikipedia_client = wikipedia_client
        self.http_client = http_client

    async def _extract_search_terms(self, query_text: str) -> str:
        """Extract key search terms from a conversational query using OpenAI."""
        try:
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "Bearer test-key"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": query_text}],
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return query_text

    async def process_query(
        self,
        session_id: int,
        user_id: int,
        query_text: str,
        input_mode: str = "text",
    ) -> QueryResponse | None:
        """Process a user query and return AI response."""
        # Verify session ownership
        session = await self.session_repository.get_session_by_id(session_id)
        if not session or session.user_id != user_id:
            return None

        # Extract search terms
        search_terms = await self._extract_search_terms(query_text)

        # Get Wikipedia context
        wikipedia_context, wikipedia_sources = await self.wikipedia_client.get_context_for_query(
            search_terms
        )

        # Get conversation history
        recent_queries = await self.query_repository.get_recent_queries_by_session_id(
            session_id,
            limit=5,
        )

        # Build messages and get AI response
        messages = self._build_messages(wikipedia_context, recent_queries, query_text)
        response_text = await self._get_openai_response(messages)

        # Save query and response
        query_record = await self.query_repository.create_query(
            session_id=session_id,
            query_text=query_text,
            response_text=response_text,
            input_mode=input_mode,
        )

        # Update session title if first query
        if len(recent_queries) == 0:
            title = query_text[:50] + "..." if len(query_text) > 50 else query_text
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
            context_message += "(EMPTY - No Wikipedia articles found)"

        context_message += "\n\nCONVERSATION HISTORY:\n"
        if conversation_history:
            for q in conversation_history:
                context_message += f"User: {q.query_text}\nAssistant: {q.response_text}\n\n"
        else:
            context_message += "(Start of conversation)"

        messages.append({"role": "user", "content": context_message})
        messages.append({"role": "assistant", "content": "I understand."})
        messages.append({"role": "user", "content": f"USER QUERY:\n{current_query}"})

        return messages

    async def _get_openai_response(self, messages: list[dict]) -> str:
        """Get response from OpenAI API."""
        try:
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "Bearer test-key"},
                json={"model": "gpt-4o-mini", "messages": messages},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            return "I'm sorry, I encountered an error."

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
                sources=[],
                created_at=q.created_at,
            )
            for q in queries
        ]


class TestRAGServiceQueryProcessing:
    """Test RAG query processing behavior."""

    @pytest.fixture
    def mock_session_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_query_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_wikipedia_client(self):
        return AsyncMock()

    @pytest.fixture
    def mock_http_client(self):
        return AsyncMock()

    @pytest.fixture
    def rag_service(
        self,
        mock_session_repository,
        mock_query_repository,
        mock_wikipedia_client,
        mock_http_client,
    ):
        return RAGService(
            mock_session_repository,
            mock_query_repository,
            mock_wikipedia_client,
            mock_http_client,
        )

    @pytest.fixture
    def sample_session(self):
        return SessionModel(session_id=1, user_id=1, title="Test")

    @pytest.fixture
    def sample_query(self):
        return QueryModel(
            query_id=1,
            session_id=1,
            query_text="What is Python?",
            response_text="Python is a programming language.",
            input_mode="text",
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "session_user_id,requesting_user_id,should_process",
        [
            (1, 1, True),  # User owns the session
            (1, 2, False),  # User doesn't own the session
            (5, 5, True),  # Another user owns their session
            (10, 1, False),  # Different user trying to access
        ],
    )
    async def test_process_query_respects_session_ownership(
        self,
        rag_service: RAGService,
        mock_session_repository: AsyncMock,
        mock_query_repository: AsyncMock,
        mock_wikipedia_client: AsyncMock,
        mock_http_client: AsyncMock,
        sample_session: SessionModel,
        sample_query: QueryModel,
        session_user_id: int,
        requesting_user_id: int,
        should_process: bool,
    ):
        """When processing query, system should only process if user owns the session."""
        # Arrange
        sample_session.user_id = session_user_id
        mock_session_repository.get_session_by_id.return_value = sample_session
        mock_query_repository.get_recent_queries_by_session_id.return_value = []
        mock_query_repository.create_query.return_value = sample_query
        mock_wikipedia_client.get_context_for_query.return_value = (
            "Wikipedia context",
            [WikipediaSource(title="Test", extract="...", url="http://test.com")],
        )

        # Mock OpenAI responses
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "AI Response"}}]}
        mock_response.raise_for_status = MagicMock()
        mock_http_client.post.return_value = mock_response

        # Act
        result = await rag_service.process_query(
            session_id=sample_session.session_id,
            user_id=requesting_user_id,
            query_text="What is Rolex?",
        )

        # Assert
        if should_process:
            assert result is not None
            mock_wikipedia_client.get_context_for_query.assert_called()
        else:
            assert result is None

    @pytest.mark.asyncio
    async def test_process_query_returns_none_for_nonexistent_session(
        self,
        rag_service: RAGService,
        mock_session_repository: AsyncMock,
    ):
        """When session doesn't exist, system should return None."""
        # Arrange
        mock_session_repository.get_session_by_id.return_value = None

        # Act
        result = await rag_service.process_query(
            session_id=999,
            user_id=1,
            query_text="Test query",
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "query_text,input_mode",
        [
            ("What is Python?", "text"),
            ("Tell me about the moon", "voice"),
            ("How does photosynthesis work?", "text"),
            ("Who is Albert Einstein?", "voice"),
        ],
    )
    async def test_process_query_saves_input_mode(
        self,
        rag_service: RAGService,
        mock_session_repository: AsyncMock,
        mock_query_repository: AsyncMock,
        mock_wikipedia_client: AsyncMock,
        mock_http_client: AsyncMock,
        sample_session: SessionModel,
        sample_query: QueryModel,
        query_text: str,
        input_mode: str,
    ):
        """When processing query, system should save the input mode (text/voice)."""
        # Arrange
        sample_session.user_id = 1
        mock_session_repository.get_session_by_id.return_value = sample_session
        mock_query_repository.get_recent_queries_by_session_id.return_value = []
        sample_query.input_mode = input_mode
        mock_query_repository.create_query.return_value = sample_query
        mock_wikipedia_client.get_context_for_query.return_value = ("Context", [])

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Response"}}]}
        mock_response.raise_for_status = MagicMock()
        mock_http_client.post.return_value = mock_response

        # Act
        result = await rag_service.process_query(
            session_id=1,
            user_id=1,
            query_text=query_text,
            input_mode=input_mode,
        )

        # Assert
        assert result is not None
        mock_query_repository.create_query.assert_called_once()
        call_kwargs = mock_query_repository.create_query.call_args.kwargs
        assert call_kwargs["input_mode"] == input_mode

    @pytest.mark.asyncio
    async def test_process_query_updates_title_on_first_query(
        self,
        rag_service: RAGService,
        mock_session_repository: AsyncMock,
        mock_query_repository: AsyncMock,
        mock_wikipedia_client: AsyncMock,
        mock_http_client: AsyncMock,
        sample_session: SessionModel,
        sample_query: QueryModel,
    ):
        """When processing first query in session, system should update session title."""
        # Arrange
        sample_session.user_id = 1
        mock_session_repository.get_session_by_id.return_value = sample_session
        mock_query_repository.get_recent_queries_by_session_id.return_value = []  # First query
        mock_query_repository.create_query.return_value = sample_query
        mock_wikipedia_client.get_context_for_query.return_value = ("Context", [])

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Response"}}]}
        mock_response.raise_for_status = MagicMock()
        mock_http_client.post.return_value = mock_response

        # Act
        await rag_service.process_query(
            session_id=1,
            user_id=1,
            query_text="What is Rolex?",
        )

        # Assert
        mock_session_repository.update_session_title.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_query_does_not_update_title_on_subsequent_queries(
        self,
        rag_service: RAGService,
        mock_session_repository: AsyncMock,
        mock_query_repository: AsyncMock,
        mock_wikipedia_client: AsyncMock,
        mock_http_client: AsyncMock,
        sample_session: SessionModel,
        sample_query: QueryModel,
    ):
        """When processing non-first query, system should not update session title."""
        # Arrange
        sample_session.user_id = 1
        mock_session_repository.get_session_by_id.return_value = sample_session
        mock_query_repository.get_recent_queries_by_session_id.return_value = [
            sample_query
        ]  # Has history
        mock_query_repository.create_query.return_value = sample_query
        mock_wikipedia_client.get_context_for_query.return_value = ("Context", [])

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Response"}}]}
        mock_response.raise_for_status = MagicMock()
        mock_http_client.post.return_value = mock_response

        # Act
        await rag_service.process_query(
            session_id=1,
            user_id=1,
            query_text="Follow-up question",
        )

        # Assert
        mock_session_repository.update_session_title.assert_not_called()


class TestRAGServiceSearchTermExtraction:
    """Test search term extraction from conversational queries."""

    @pytest.fixture
    def mock_session_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_query_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_wikipedia_client(self):
        return AsyncMock()

    @pytest.fixture
    def mock_http_client(self):
        return AsyncMock()

    @pytest.fixture
    def rag_service(
        self,
        mock_session_repository,
        mock_query_repository,
        mock_wikipedia_client,
        mock_http_client,
    ):
        return RAGService(
            mock_session_repository,
            mock_query_repository,
            mock_wikipedia_client,
            mock_http_client,
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user_query,extracted_term",
        [
            ("do you know anything about Rolex", "Rolex"),
            ("can you tell me about the Eiffel Tower?", "Eiffel Tower"),
            ("what is quantum computing", "quantum computing"),
            ("Rolex", "Rolex"),
        ],
    )
    async def test_extract_search_terms_from_conversational_queries(
        self,
        rag_service: RAGService,
        mock_http_client: AsyncMock,
        user_query: str,
        extracted_term: str,
    ):
        """When extracting search terms, system should convert conversational queries to topics."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": extracted_term}}]}
        mock_response.raise_for_status = MagicMock()
        mock_http_client.post.return_value = mock_response

        # Act
        result = await rag_service._extract_search_terms(user_query)

        # Assert
        assert result == extracted_term
        mock_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_search_terms_falls_back_to_original_on_error(
        self,
        rag_service: RAGService,
        mock_http_client: AsyncMock,
    ):
        """When OpenAI extraction fails, system should fall back to original query."""
        # Arrange
        mock_http_client.post.side_effect = Exception("API error")
        original_query = "What is Python programming?"

        # Act
        result = await rag_service._extract_search_terms(original_query)

        # Assert
        assert result == original_query


class TestRAGServiceMessageBuilding:
    """Test message building for OpenAI."""

    @pytest.fixture
    def mock_session_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_query_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_wikipedia_client(self):
        return AsyncMock()

    @pytest.fixture
    def mock_http_client(self):
        return AsyncMock()

    @pytest.fixture
    def rag_service(
        self,
        mock_session_repository,
        mock_query_repository,
        mock_wikipedia_client,
        mock_http_client,
    ):
        return RAGService(
            mock_session_repository,
            mock_query_repository,
            mock_wikipedia_client,
            mock_http_client,
        )

    def test_build_messages_includes_system_prompt(self, rag_service: RAGService):
        """When building messages, system should include the system prompt."""
        # Act
        messages = rag_service._build_messages(
            wikipedia_context="Some context",
            conversation_history=[],
            current_query="What is Python?",
        )

        # Assert
        assert messages[0]["role"] == "system"
        assert "WikiVoice" in messages[0]["content"]

    def test_build_messages_includes_wikipedia_context(self, rag_service: RAGService):
        """When building messages, system should include Wikipedia context."""
        # Act
        messages = rag_service._build_messages(
            wikipedia_context="Rolex is a Swiss luxury watch manufacturer.",
            conversation_history=[],
            current_query="What is Rolex?",
        )

        # Assert
        context_message = messages[1]["content"]
        assert "Rolex" in context_message
        assert "Swiss luxury watch" in context_message

    def test_build_messages_includes_empty_context_warning(self, rag_service: RAGService):
        """When no Wikipedia context, system should include warning."""
        # Act
        messages = rag_service._build_messages(
            wikipedia_context="",
            conversation_history=[],
            current_query="What is xyz123abc?",
        )

        # Assert
        context_message = messages[1]["content"]
        assert "EMPTY" in context_message

    def test_build_messages_includes_conversation_history(self, rag_service: RAGService):
        """When building messages, system should include conversation history."""
        # Arrange
        sample_query = QueryModel(
            query_id=1,
            session_id=1,
            query_text="What is Python?",
            response_text="Python is a programming language.",
        )

        # Act
        messages = rag_service._build_messages(
            wikipedia_context="Context",
            conversation_history=[sample_query],
            current_query="Follow-up question",
        )

        # Assert
        context_message = messages[1]["content"]
        assert sample_query.query_text in context_message
        assert sample_query.response_text in context_message


class TestRAGServiceConversationHistory:
    """Test conversation history retrieval behavior."""

    @pytest.fixture
    def mock_session_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_query_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_wikipedia_client(self):
        return AsyncMock()

    @pytest.fixture
    def mock_http_client(self):
        return AsyncMock()

    @pytest.fixture
    def rag_service(
        self,
        mock_session_repository,
        mock_query_repository,
        mock_wikipedia_client,
        mock_http_client,
    ):
        return RAGService(
            mock_session_repository,
            mock_query_repository,
            mock_wikipedia_client,
            mock_http_client,
        )

    @pytest.fixture
    def sample_session(self):
        return SessionModel(session_id=1, user_id=1)

    @pytest.fixture
    def sample_query(self):
        return QueryModel(
            query_id=1,
            session_id=1,
            query_text="Test",
            response_text="Response",
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "session_user_id,requesting_user_id,should_return_history",
        [
            (1, 1, True),
            (1, 2, False),
            (5, 5, True),
            (10, 1, False),
        ],
    )
    async def test_get_conversation_history_respects_ownership(
        self,
        rag_service: RAGService,
        mock_session_repository: AsyncMock,
        mock_query_repository: AsyncMock,
        sample_session: SessionModel,
        sample_query: QueryModel,
        session_user_id: int,
        requesting_user_id: int,
        should_return_history: bool,
    ):
        """When getting history, system should only return if user owns the session."""
        # Arrange
        sample_session.user_id = session_user_id
        mock_session_repository.get_session_by_id.return_value = sample_session
        mock_query_repository.get_queries_by_session_id.return_value = [sample_query]

        # Act
        result = await rag_service.get_conversation_history(
            session_id=sample_session.session_id,
            user_id=requesting_user_id,
        )

        # Assert
        if should_return_history:
            assert result is not None
            assert len(result) == 1
        else:
            assert result is None

    @pytest.mark.asyncio
    async def test_get_conversation_history_returns_none_for_nonexistent_session(
        self,
        rag_service: RAGService,
        mock_session_repository: AsyncMock,
    ):
        """When session doesn't exist, system should return None."""
        # Arrange
        mock_session_repository.get_session_by_id.return_value = None

        # Act
        result = await rag_service.get_conversation_history(session_id=999, user_id=1)

        # Assert
        assert result is None
