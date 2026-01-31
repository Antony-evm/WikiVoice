"""Wikipedia client for fetching article content."""

from dataclasses import dataclass

import httpx

from app.logging_config import get_logger

logger = get_logger(__name__)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

WIKIPEDIA_HEADERS = {
    "User-Agent": "WikiVoice/1.0 (https://github.com/wikivoice; contact@wikivoice.app) httpx/0.27",
}


@dataclass
class WikipediaSearchResult:
    """A Wikipedia search result with relevance info."""

    title: str
    snippet: str
    word_count: int


@dataclass
class WikipediaSource:
    """A Wikipedia article source used for context."""

    title: str
    extract: str
    url: str


class WikipediaClient:
    """Client for interacting with Wikipedia API."""

    MIN_ARTICLE_WORDS = 500

    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def search_articles(self, query: str, limit: int = 5) -> list[WikipediaSearchResult]:
        """Search Wikipedia for relevant article titles."""
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srprop": "snippet|wordcount",
            "format": "json",
        }
        try:
            response = await self.http_client.get(
                WIKIPEDIA_API_URL, params=params, headers=WIKIPEDIA_HEADERS
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get("query", {}).get("search", []):
                word_count = result.get("wordcount", 0)
                title = result["title"]

                logger.info(f"Wikipedia search result: '{title}' ({word_count} words)")

                if word_count >= self.MIN_ARTICLE_WORDS:
                    results.append(
                        WikipediaSearchResult(
                            title=title,
                            snippet=result.get("snippet", ""),
                            word_count=word_count,
                        )
                    )
                else:
                    logger.debug(f"Filtered out '{title}' - only {word_count} words")

            logger.info(f"Wikipedia search for '{query}' returned {len(results)} valid results")
            return results[:3]
        except Exception:
            logger.exception(f"Wikipedia search failed for query: {query}")
            return []

    async def get_article_extract(self, title: str, sentences: int = 10) -> str | None:
        """Get the extract (summary) of a Wikipedia article."""
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts",
            "exsentences": sentences,
            "explaintext": True,
            "format": "json",
        }
        try:
            response = await self.http_client.get(
                WIKIPEDIA_API_URL, params=params, headers=WIKIPEDIA_HEADERS
            )
            response.raise_for_status()
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                if "extract" in page:
                    return page["extract"]
            return None
        except Exception:
            logger.exception(f"Wikipedia extract fetch failed for '{title}'")
            return None

    async def get_context_for_query(
        self, query: str, max_articles: int = 3
    ) -> tuple[str, list[WikipediaSource]]:
        """Get Wikipedia context for a query."""
        search_results = await self.search_articles(query, limit=10)
        if not search_results:
            logger.warning(f"No Wikipedia results found for query: {query}")
            return "", []

        context_parts = []
        sources = []
        for result in search_results[:max_articles]:
            extract = await self.get_article_extract(result.title)
            if extract:
                context_parts.append(f"## {result.title}\n{extract}")
                url = f"https://en.wikipedia.org/wiki/{result.title.replace(' ', '_')}"
                sources.append(WikipediaSource(title=result.title, extract=extract[:200], url=url))

        return "\n\n".join(context_parts), sources
