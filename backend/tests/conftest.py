"""Shared pytest fixtures and configuration for backend tests."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def anyio_backend():
    """Use asyncio as the async backend."""
    return "asyncio"


@pytest.fixture
def mock_settings():
    """Create mock settings for tests."""
    settings = MagicMock()
    settings.openai_api_key = "test-openai-key"
    settings.environment = "test"
    settings.stytch_project_id = "test-project-id"
    settings.stytch_secret = "test-secret"
    return settings


@pytest.fixture
def sample_user():
    """Create a sample user model for testing."""
    from models.user_model import UserModel

    user = UserModel()
    user.user_id = 1
    user.email = "test@example.com"
    user.stytch_user_id = "stytch-user-123"
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    user.is_obsolete = False
    return user


@pytest.fixture
def sample_session():
    """Create a sample session model for testing."""
    from models.session_model import SessionModel

    session = SessionModel()
    session.session_id = 1
    session.user_id = 1
    session.title = "Test Conversation"
    session.created_at = datetime.now(UTC)
    session.updated_at = datetime.now(UTC)
    session.is_obsolete = False
    return session


@pytest.fixture
def sample_query():
    """Create a sample query model for testing."""
    from models.query_model import QueryModel

    query = QueryModel()
    query.query_id = 1
    query.session_id = 1
    query.query_text = "What is Python?"
    query.response_text = "Python is a programming language..."
    query.input_mode = "text"
    query.created_at = datetime.now(UTC)
    return query


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_session_repository():
    """Create a mock session repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_query_repository():
    """Create a mock query repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for external API calls."""
    client = AsyncMock()
    return client


@pytest.fixture
def mock_wikipedia_client():
    """Create a mock Wikipedia client."""
    client = AsyncMock()
    return client


@pytest.fixture
def mock_stytch_session_data():
    """Create mock Stytch session data."""
    from domain.responses.session_data import SessionData

    return SessionData(
        session_jwt="test-jwt-token",
        session_token="test-session-token",
        stytch_user_id="stytch-user-123",
    )


@pytest.fixture
def openai_search_extraction_response():
    """Mock response for OpenAI search term extraction."""
    return {"choices": [{"message": {"content": "Rolex"}}]}


@pytest.fixture
def openai_chat_response():
    """Mock response for OpenAI chat completion."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Based on Wikipedia, Rolex is a Swiss luxury watch manufacturer..."
                }
            }
        ]
    }


@pytest.fixture
def wikipedia_search_response():
    """Mock response for Wikipedia search API."""
    return {
        "query": {
            "search": [
                {
                    "title": "Rolex",
                    "snippet": "Rolex SA is a Swiss luxury watch manufacturer...",
                    "wordcount": 5000,
                },
                {
                    "title": "Rolex Submariner",
                    "snippet": "The Rolex Submariner is a diving watch...",
                    "wordcount": 3000,
                },
                {
                    "title": "Disambiguation Page",
                    "snippet": "Short disambiguation",
                    "wordcount": 100,  # Should be filtered out
                },
            ]
        }
    }


@pytest.fixture
def wikipedia_extract_response():
    """Mock response for Wikipedia extract API."""
    return {
        "query": {
            "pages": {
                "12345": {
                    "pageid": 12345,
                    "title": "Rolex",
                    "extract": "Rolex SA is a Swiss luxury watch manufacturer based in Geneva, Switzerland.",
                }
            }
        }
    }
