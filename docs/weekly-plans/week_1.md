# Week 1: Local Stack Setup & Streaming RAG

This week focuses on initializing the repository, configuring the Docker-based local services, and implementing the baseline async streaming RAG pipeline.

---

## 🎯 Weekly Goals
- Launch the 10-service Docker Compose environment locally.
- Build the FastAPI application structure, databases, and migrations.
- Implement the core AI client wrappers (OpenAI embeddings, Qdrant, and Redis).
- Complete the RAG Ingestion API (`/v1/rag/ingest`) and the RAG Query SSE API (`/v1/rag/query`).

## ✅ Current Implementation Status (May 20, 2026)
- Backend bootstrap is live with `FastAPI`, CORS, request ID middleware, `/v1/health`, `/v1/readiness`, and `/metrics`.
- Core local stack has been validated for `postgres`, `redis`, `qdrant`, and `app` through Docker Compose.
- Phase 1 relational tables (`users`, `rag_collections`, `request_log`) are implemented and applied through Alembic.
- Day 5 wrapper modules are implemented for OpenAI embeddings, Qdrant access, Redis cache access, and LangFuse tracing hooks.
- Minimal frontend shell, Dockerfiles, `.env` templates, and pre-commit hooks are in place.
- Remaining Week 1 work: LangFuse trace verification, RAG ingestion/query APIs, seed script, and CI workflow.

---

## 📆 Day-by-Day Implementation Checklist

### Day 1: Project Initialization & Monorepo Structure
- [x] Create the project root directory and initialize a Git repository.
- [x] Create the monorepo folder structure: `backend/`, `frontend/`, `infra/`, and `scripts/`.
- [x] Configure `pyproject.toml` and `requirements.txt` in the backend directory.
- [x] Create the frontend `package.json` and baseline Next.js 14 configuration files.
- [x] Initialize pre-commit configurations using `.pre-commit-config.yaml` to run `ruff` and `prettier`.

### Day 2: Orchestrating the Local Stack
- [x] Create `infra/docker-compose.yml` defining PostgreSQL, Qdrant, Redis, Prometheus, Grafana, Jaeger, Nginx, Celery, frontend, and the FastAPI application.
- [x] Add health checks to the Postgres, Redis, and Qdrant services.
- [x] Configure volume structures to persist database and index storage.
- [x] Write the initial configuration for the Nginx reverse proxy.
- [ ] Run `docker compose up -d` to verify that the full stack starts successfully.

Note: the core backend stack (`postgres`, `redis`, `qdrant`, `app`) is already validated. `langfuse-server` is defined behind an optional `observability` profile until its full backing stack is provisioned.

### Day 3: Backend Core Bootstrap
- [x] Implement `backend/app/main.py` containing the FastAPI application factory.
- [x] Write `backend/app/config.py` using `pydantic-settings` to load and validate environment variables.
- [x] Implement middleware to log incoming request sizes, statuses, and execution latencies.
- [x] Expose basic `/health` liveness endpoints.
- [x] Verify CORS configurations to allow local requests from the frontend.

### Day 4: Relational Databases & Migrations
- [x] Create SQLAlchemy model definitions inside `backend/app/models/db.py` for `users`, `rag_collections`, and `request_log`.
- [x] Configure database connections and session factories inside `backend/app/dependencies.py`.
- [x] Initialize Alembic migration scaffolding for the backend.
- [x] Generate the initial database migration script representing the PostgreSQL database tables.
- [x] Run `alembic upgrade head` to apply database schema updates.

### Day 5: AI Client Wrappers & LangFuse Integration
- [x] Build `backend/app/core/embeddings.py` using the OpenAI client wrapper pointing to `text-embedding-3-large`.
- [x] Build `backend/app/core/vector_store.py` to handle async operations with Qdrant.
- [x] Build `backend/app/core/cache.py` to handle async operations with Redis.
- [x] Configure `backend/app/core/tracing.py` to initialize Langfuse clients.
- [ ] Instrument embeddings and Qdrant wrapper functions with Langfuse `@observe()` trace decorators.
- [ ] Run manual scripts to verify that test traces log correctly to the LangFuse dashboard.

### Day 6: RAG Ingestion Pipeline
- [ ] Write `backend/app/rag/ingestion.py` using `LlamaIndex` to parse documents, chunk text, and generate embeddings.
- [ ] Build the file upload API route `POST /v1/rag/ingest` to handle document uploads, parse chunks, generate embeddings, and upsert them to Qdrant.
- [ ] Add exception handling to capture parse failures or API connection errors.
- [ ] Verify that document and chunk counts are logged correctly in the PostgreSQL `rag_collections` table.

### Day 7: RAG Streaming Query Engine & Seed Script
- [ ] Write `backend/app/rag/retrieval.py` to retrieve relevant document chunks from Qdrant and rerank them using Cohere Rerank v3.
- [ ] Build the streaming query API route `POST /v1/rag/query` returning Server-Sent Events (SSE).
- [ ] Write `scripts/seed_qdrant.py` to seed the database with sample documents for testing.
- [ ] Set up the GitHub Actions workflow file `.github/workflows/ci.yml` to run linting and pytest suites.

---

## 🛠️ Code Architecture & Design Goals
- Ensure all services (such as databases and APIs) utilize environment variables for configuration rather than hardcoded URLs.
- Implement async operations for all database, vector store, and external AI network requests.
- Establish standard Pydantic request and response schemas to ensure consistent API inputs and outputs.

---

## 🔍 Refactoring Checkpoints
- **Database Sessions**: Verify that database connection sessions are closed after request completion to prevent resource leaks.
- **Error Propagation**: Catch external API connection timeouts and format them into structured error responses.

---

## 🧪 Testing & Debugging Tasks
- Run integration tests to verify the RAG query flow using mock API endpoints.
- Check that the SSE endpoint flushes chunks progressively during generation.
- Monitor log files to ensure `X-Request-ID` correlation identifiers are propagated across requests.

## ⚠️ Known Limitations
- `langfuse-server` is intentionally behind an optional Compose profile for now; the backend tracing wrapper exists, but trace export has not been verified against a live LangFuse target yet.
- RAG ingestion and streaming query routes are still pending.
- Full-stack `docker compose up -d` validation is pending the remaining service surfaces.
