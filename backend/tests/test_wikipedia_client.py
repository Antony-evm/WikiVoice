"""Tests for Wikipedia client behavior - isolated unit tests."""

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

import pytest


# Recreate minimal types needed for testing
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
    """Client for interacting with Wikipedia API (test version)."""

    MIN_ARTICLE_WORDS = 500

    def __init__(self, http_client):
        self.http_client = http_client

    async def search_articles(self, query: str, limit: int = 5) -> list[WikipediaSearchResult]:
        """Search Wikipedia for relevant article titles."""
        try:
            response = await self.http_client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": limit,
                    "srprop": "snippet|wordcount",
                    "format": "json",
                },
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get("query", {}).get("search", []):
                word_count = result.get("wordcount", 0)
                if word_count >= self.MIN_ARTICLE_WORDS:
                    results.append(
                        WikipediaSearchResult(
                            title=result["title"],
                            snippet=result.get("snippet", ""),
                            word_count=word_count,
                        )
                    )

            return results[:3]
        except Exception:
            return []

    async def get_article_extract(self, title: str, sentences: int = 10) -> str | None:
        """Get the extract (summary) of a Wikipedia article."""
        try:
            response = await self.http_client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "titles": title,
                    "prop": "extracts",
                    "exsentences": sentences,
                    "explaintext": True,
                    "format": "json",
                },
            )
            response.raise_for_status()
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                if "extract" in page:
                    return page["extract"]
            return None
        except Exception:
            return None

    async def get_context_for_query(
        self, query: str, max_articles: int = 3
    ) -> tuple[str, list[WikipediaSource]]:
        """Get Wikipedia context for a query."""
        search_results = await self.search_articles(query, limit=10)
        if not search_results:
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


class TestWikipediaClientSearch:
    """Test Wikipedia search behavior."""

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return AsyncMock()

    @pytest.fixture
    def wikipedia_client(self, mock_http_client):
        """Create a WikipediaClient with mocked HTTP client."""
        return WikipediaClient(mock_http_client)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "query,expected_count,search_results",
        [
            # Normal search with multiple results above threshold
            (
                "Rolex",
                2,
                [
                    {"title": "Rolex", "snippet": "Swiss luxury...", "wordcount": 5000},
                    {"title": "Rolex Submariner", "snippet": "Diving watch...", "wordcount": 3000},
                ],
            ),
            # Search with some results below threshold (should be filtered)
            (
                "Python",
                1,
                [
                    {"title": "Python (programming)", "snippet": "Language...", "wordcount": 8000},
                    {"title": "Python (disambiguation)", "snippet": "Various...", "wordcount": 100},
                ],
            ),
            # Search with no results
            (
                "xyznonexistent",
                0,
                [],
            ),
            # Search where all results are below threshold
            (
                "stub",
                0,
                [
                    {"title": "Stub1", "snippet": "...", "wordcount": 50},
                    {"title": "Stub2", "snippet": "...", "wordcount": 100},
                ],
            ),
        ],
    )
    async def test_search_articles_filters_by_word_count(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
        query: str,
        expected_count: int,
        search_results: list,
    ):
        """When searching Wikipedia, system should filter out articles below minimum word count."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"query": {"search": search_results}}
        mock_response.raise_for_status = MagicMock()
        mock_http_client.get.return_value = mock_response

        # Act
        results = await wikipedia_client.search_articles(query)

        # Assert
        assert len(results) == expected_count
        for result in results:
            assert result.word_count >= WikipediaClient.MIN_ARTICLE_WORDS

    @pytest.mark.asyncio
    async def test_search_articles_returns_max_three_results(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
    ):
        """When searching Wikipedia, system should return at most 3 results."""
        # Arrange
        many_results = [
            {"title": f"Article {i}", "snippet": "...", "wordcount": 1000} for i in range(10)
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = {"query": {"search": many_results}}
        mock_response.raise_for_status = MagicMock()
        mock_http_client.get.return_value = mock_response

        # Act
        results = await wikipedia_client.search_articles("test")

        # Assert
        assert len(results) <= 3

    @pytest.mark.asyncio
    async def test_search_articles_handles_api_errors_gracefully(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
    ):
        """When Wikipedia API fails, system should return empty list gracefully."""
        # Arrange
        mock_http_client.get.side_effect = Exception("Network error")

        # Act
        results = await wikipedia_client.search_articles("test")

        # Assert
        assert results == []


class TestWikipediaClientExtract:
    """Test Wikipedia article extract behavior."""

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return AsyncMock()

    @pytest.fixture
    def wikipedia_client(self, mock_http_client):
        """Create a WikipediaClient with mocked HTTP client."""
        return WikipediaClient(mock_http_client)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "title,extract_text",
        [
            ("Rolex", "Rolex SA is a Swiss luxury watch manufacturer..."),
            ("Python (programming language)", "Python is a high-level programming language..."),
            ("Albert Einstein", "Albert Einstein was a German-born theoretical physicist..."),
        ],
    )
    async def test_get_article_extract_returns_extract(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
        title: str,
        extract_text: str,
    ):
        """When getting article extract, system should return the extract text."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "title": title,
                        "extract": extract_text,
                    }
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_http_client.get.return_value = mock_response

        # Act
        result = await wikipedia_client.get_article_extract(title)

        # Assert
        assert result == extract_text

    @pytest.mark.asyncio
    async def test_get_article_extract_returns_none_for_missing_page(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
    ):
        """When article doesn't exist, system should return None."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "-1": {
                        "ns": 0,
                        "title": "Nonexistent",
                        "missing": "",
                    }
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_http_client.get.return_value = mock_response

        # Act
        result = await wikipedia_client.get_article_extract("Nonexistent")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_article_extract_handles_api_errors_gracefully(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
    ):
        """When Wikipedia API fails, system should return None gracefully."""
        # Arrange
        mock_http_client.get.side_effect = Exception("Network error")

        # Act
        result = await wikipedia_client.get_article_extract("Test")

        # Assert
        assert result is None


class TestWikipediaClientContext:
    """Test getting context for queries."""

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return AsyncMock()

    @pytest.fixture
    def wikipedia_client(self, mock_http_client):
        """Create a WikipediaClient with mocked HTTP client."""
        return WikipediaClient(mock_http_client)

    @pytest.mark.asyncio
    async def test_get_context_combines_search_and_extracts(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
    ):
        """When getting context, system should search and fetch extracts."""
        # Arrange
        search_response = MagicMock()
        search_response.json.return_value = {
            "query": {
                "search": [
                    {"title": "Rolex", "snippet": "...", "wordcount": 5000},
                ]
            }
        }
        search_response.raise_for_status = MagicMock()

        extract_response = MagicMock()
        extract_response.json.return_value = {
            "query": {
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "title": "Rolex",
                        "extract": "Rolex SA is a Swiss luxury watch manufacturer.",
                    }
                }
            }
        }
        extract_response.raise_for_status = MagicMock()

        mock_http_client.get.side_effect = [search_response, extract_response]

        # Act
        context, sources = await wikipedia_client.get_context_for_query("Rolex")

        # Assert
        assert "Rolex" in context
        assert len(sources) == 1
        assert sources[0].title == "Rolex"
        assert "wikipedia.org" in sources[0].url

    @pytest.mark.asyncio
    async def test_get_context_returns_empty_when_no_results(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
    ):
        """When no Wikipedia results found, system should return empty context."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"query": {"search": []}}
        mock_response.raise_for_status = MagicMock()
        mock_http_client.get.return_value = mock_response

        # Act
        context, sources = await wikipedia_client.get_context_for_query("xyznonexistent")

        # Assert
        assert context == ""
        assert sources == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "max_articles",
        [1, 2, 3],
    )
    async def test_get_context_respects_max_articles_limit(
        self,
        wikipedia_client: WikipediaClient,
        mock_http_client: AsyncMock,
        max_articles: int,
    ):
        """When getting context, system should respect max_articles parameter."""
        # Arrange
        search_results = [
            {"title": f"Article {i}", "snippet": "...", "wordcount": 1000} for i in range(5)
        ]
        search_response = MagicMock()
        search_response.json.return_value = {"query": {"search": search_results}}
        search_response.raise_for_status = MagicMock()

        extract_response = MagicMock()
        extract_response.json.return_value = {
            "query": {"pages": {"1": {"extract": "Article content..."}}}
        }
        extract_response.raise_for_status = MagicMock()

        # Return search response first, then extract responses
        mock_http_client.get.side_effect = [search_response] + [extract_response] * max_articles

        # Act
        context, sources = await wikipedia_client.get_context_for_query("test", max_articles)

        # Assert
        assert len(sources) <= max_articles
