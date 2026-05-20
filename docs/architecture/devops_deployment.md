# DevOps, Docker & Deployment Architecture

This document details the Docker Compose environments, GitHub Actions CI/CD workflows, and production cloud migration strategies.

---

## 🐋 Local Docker Compose Environment

The platform runs locally using `Docker Compose v2`. The services are organized as follows:

```
        ┌──────────────────────────────────────────────┐
        │              genai-net (Bridge)              │
        └──────┬────────────────────────────────┬──────┘
               │                                │
        ┌──────▼──────┐                  ┌──────▼──────┐
        │  Nginx Host │                  │  Celery Worker
        └──────┬──────┘                  └──────┬──────┘
               │                                │
        ┌──────▼──────┐                  ┌──────▼──────┐
        │ FastAPI App │                  │  PostgreSQL │
        └──────┬──────┘                  └──────┬──────┘
               │                                │
        ┌──────▼──────┐                  ┌──────▼──────┐
        │  Qdrant DB  │                  │  Redis Host │
        └─────────────┘                  └─────────────┘
```

### Core Services
- **`backend`**: FastAPI application container.
- **`celery-worker`**: Background worker container that executes agent graphs.
- **`frontend`**: Next.js client application container.
- **`nginx`**: Reverse proxy that handles and routes incoming web traffic.
- **`postgres`**: Relational database storage.
- **`qdrant`**: Vector index storage.
- **`redis`**: Cache and worker message broker.
- **`prometheus`**: Collects system metrics.
- **`grafana`**: Displays system and performance dashboards.
- **`jaeger`**: Stores and visualizes execution traces.

---

## 🚀 GitHub Actions CI/CD Workflows

### 1. Integration Pipeline (`ci.yml`)
Runs on all incoming Pull Requests:
- **Linting**: Runs `ruff check` on backend code and `eslint` on frontend files.
- **Code Formatting**: Checks formatting using `black` and `prettier`.
- **Unit Testing**: Runs `pytest` suites and collects coverage reports.

### 2. Deployment Pipeline (`deploy.yml`)
Runs on merges to the `main` branch:
- **Backend Deployment**: Deploys the FastAPI application and Celery worker to Railway.
- **Frontend Deployment**: Deploys the Next.js frontend to Vercel.

---

## ☁️ Cloud Migration Plan

In production, local containers are migrated to managed cloud services:

| Service | Local Container | Production SaaS Target | Migration Process |
|---|---|---|---|
| API Gateway | `backend` (FastAPI) | **Railway** / **Cloud Run** | Build Docker containers and update environment variables. |
| User Interface | `frontend` (Next.js) | **Vercel** | Link the Git repository to Vercel for automated deployments. |
| Relational DB | `postgres` (Postgres 16) | **Supabase** | Migrate schemas using Alembic and update connection string variables. |
| Vector DB | `qdrant` (Qdrant) | **Qdrant Cloud** | Export index snapshots and upload them to Qdrant Cloud. |
| Cache & Broker | `redis` (Redis 7) | **Upstash Redis** | Update connection strings to point to Upstash endpoints. |
| Observability | `langfuse-server` | **LangFuse Cloud** | Redirect tracing client variables to Langfuse Cloud. |
| Metrics | `prometheus` & `grafana` | **Grafana Cloud** | Export dashboard JSON configurations and import them to Grafana Cloud. |

---

## 🔒 Configuration Guardrails
- **Load URL variables**: Ensure that all database and service URLs are loaded from environment variables.
- **Isolate Secrets**: Store API keys and credentials in private `.env` files locally and GitHub Secrets in CI, never committing them to source control.
