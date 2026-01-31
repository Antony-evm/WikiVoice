# WikiVoice

A modern voice-enabled Wikipedia query application built with FastAPI and Vue.js, deployed on AWS infrastructure.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WikiVoice Monorepo                       │
├─────────────────┬──────────────────┬───────────────────────────┤
│    Frontend     │     Backend      │      Infrastructure       │
│    (Vue 3)      │    (FastAPI)     │       (Terraform)         │
├─────────────────┼──────────────────┼───────────────────────────┤
│ • TypeScript    │ • Python 3.13    │ • AWS ECS Fargate         │
│ • Tailwind CSS  │ • SQLAlchemy     │ • RDS PostgreSQL          │
│ • Pinia         │ • Stytch Auth    │ • CloudFront + S3         │
│ • Vite          │ • OpenAI RAG     │ • VPC + Security Groups   │
└─────────────────┴──────────────────┴───────────────────────────┘
```

## 📁 Project Structure

```
WikiVoice/
├── backend/           # FastAPI Python backend
│   ├── api/           # API routes (auth, query, session)
│   ├── application/   # Business logic services
│   ├── domain/        # Domain entities and mappers
│   ├── infrastructure/# External integrations (Wikipedia, RAG)
│   ├── models/        # SQLAlchemy database models
│   └── tests/         # Pytest test suite
│
├── frontend/          # Vue 3 SPA frontend
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/# Vue components
│   │   ├── composables/# Vue composables
│   │   ├── stores/    # Pinia stores
│   │   └── views/     # Page views
│   └── public/        # Static assets
│
├── infrastructure/    # Terraform IaC
│   ├── modules/       # Reusable Terraform modules
│   ├── environments/  # Environment configurations
│   └── bootstrap/     # Initial AWS setup
│
└── .github/workflows/ # CI/CD pipelines
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- Docker (optional, for containerized development)
- AWS CLI (for deployment)

### Backend Setup

```bash
cd backend
poetry install
cp .env.example .env  # Configure environment variables
poetry run uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🔧 Development

| Command | Description |
|---------|-------------|
| `cd backend && poetry run pytest` | Run backend tests |
| `cd frontend && npm test` | Run frontend tests |
| `cd backend && poetry run ruff check .` | Lint backend code |
| `cd frontend && npm run lint` | Lint frontend code |

## 🔐 Environment Variables

See `.env.example` in each project directory. **Never commit `.env` files!**

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for RAG
- `STYTCH_*` - Authentication configuration

## 🚢 Deployment

This project uses GitHub Actions for CI/CD:

- **CI Pipeline**: Runs on all PRs and pushes to `main`
- **CD Pipeline**: Deploys backend to ECS on successful CI
- **Terraform Plan**: Reviews infrastructure changes on PRs
- **Terraform Apply**: Applies infrastructure on merge to `main`

See [.github/workflows/](.github/workflows/) for details.

## 📖 Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Infrastructure README](infrastructure/README.md)

## 📄 License

Private - All rights reserved.
