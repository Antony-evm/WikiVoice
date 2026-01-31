# WikiVoice Backend

FastAPI backend service for WikiVoice - a RAG-powered Wikipedia query application.

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.117+
- **Python**: 3.13
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Auth**: Stytch
- **AI/RAG**: OpenAI
- **Package Manager**: Poetry

## 📁 Project Structure

```
backend/
├── api/               # API route handlers
│   ├── auth_router.py     # Authentication endpoints
│   ├── query_router.py    # Wikipedia query endpoints
│   ├── session_router.py  # Session management
│   └── health_router.py   # Health checks
├── api_requests/      # Request DTOs/Pydantic models
├── app/               # Application configuration
│   ├── config.py          # Settings management
│   ├── factory.py         # App factory
│   └── middleware.py      # Custom middleware
├── application/       # Business logic layer
│   ├── auth_service.py    # Authentication logic
│   ├── session_service.py # Session handling
│   └── user_service.py    # User management
├── domain/            # Domain layer
│   ├── entities/          # Domain entities
│   ├── mappers/           # Object mappers
│   └── responses/         # Response DTOs
├── infrastructure/    # External integrations
│   ├── rag_service.py     # OpenAI RAG integration
│   ├── wikipedia_client.py# Wikipedia API client
│   └── *_repository.py    # Data repositories
├── models/            # SQLAlchemy ORM models
├── alembic/           # Database migrations
└── tests/             # Test suite
```

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL 15+
- Poetry

### Installation

```bash
# Install dependencies
poetry install

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn main:app --reload --port 8000
```

## ⚙️ Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL async connection URL | ✅ |
| `OPENAI_API_KEY` | OpenAI API key for RAG | ✅ |
| `STYTCH_PROJECT_ID` | Stytch project ID | ✅ |
| `STYTCH_SECRET` | Stytch secret key | ✅ |
| `STYTCH_PUBLIC_TOKEN` | Stytch public token | ✅ |
| `ENVIRONMENT` | `development` / `production` | ✅ |
| `DEBUG` | Enable debug mode | ❌ |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | ❌ |
| `FRONTEND_URL` | Frontend URL for CORS | ✅ |

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=. --cov-report=html

# Run specific test file
poetry run pytest tests/test_query_validation.py -v
```

## 🔍 Code Quality

```bash
# Linting
poetry run ruff check .

# Auto-fix issues
poetry run ruff check . --fix

# Format code
poetry run ruff format .

# Type checking
poetry run mypy . --ignore-missing-imports

# Security scan
poetry run bandit -r . -x tests
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Queries
- `POST /api/v1/query` - Submit Wikipedia query
- `GET /api/v1/query/history` - Get query history

### Sessions
- `GET /api/v1/session/validate` - Validate session token

### Health
- `GET /health` - Health check endpoint

## 🐳 Docker

```bash
# Build image
docker build -t wikivoice-backend .

# Run container
docker run -p 8000:8000 --env-file .env wikivoice-backend
```

## 🗃️ Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one version
poetry run alembic downgrade -1
```

## 📄 License

Private - All rights reserved.
