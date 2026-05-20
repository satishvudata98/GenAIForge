# Week 1: Local Stack Setup & Streaming RAG

This week focuses on initializing the repository, configuring the Docker-based local services, and implementing the baseline async streaming RAG pipeline.

---

## 🎯 Weekly Goals
- Launch the 10-service Docker Compose environment locally.
- Build the FastAPI application structure, databases, and migrations.
- Implement the core AI client wrappers (OpenAI embeddings, Qdrant, and Redis).
- Complete the RAG Ingestion API (`/v1/rag/ingest`) and the RAG Query SSE API (`/v1/rag/query`).

---

## 📆 Day-by-Day Implementation Checklist

### Day 1: Project Initialization & Monorepo Structure
- [ ] Create the project root directory and initialize a Git repository.
- [ ] Create the monorepo folder structure: `backend/`, `frontend/`, `infra/`, and `scripts/`.
- [ ] Configure `pyproject.toml` and `requirements.txt` in the backend directory.
- [ ] Create the frontend `package.json` and install default Next.js 14 configurations.
- [ ] Initialize pre-commit configurations using `.pre-commit-config.yaml` to run `ruff` and `prettier`.

### Day 2: Orchestrating the Local Stack
- [ ] Create `infra/docker-compose.yml` defining PostgreSQL, Qdrant, Redis, Prometheus, Grafana, Jaeger, LangFuse Server, Nginx, Celery, and the FastAPI application.
- [ ] Add health checks to the Postgres, Redis, and Qdrant services.
- [ ] Configure volume structures to persist database and index storage.
- [ ] Write the initial configuration for the Nginx reverse proxy.
- [ ] Run `docker compose up -d` to verify that all containers start successfully.

### Day 3: Backend Core Bootstrap
- [ ] Implement `backend/app/main.py` containing the FastAPI application factory.
- [ ] Write `backend/app/config.py` using `pydantic-settings` to load and validate environment variables.
- [ ] Implement middleware to log incoming request sizes, statuses, and execution latencies.
- [ ] Expose basic `/health` liveness endpoints.
- [ ] Verify CORS configurations to allow local requests from the frontend.

### Day 4: Relational Databases & Migrations
- [ ] Create SQLAlchemy model definitions inside `backend/app/models/db.py` for `users`, `rag_collections`, and `request_log`.
- [ ] Configure database connections and session factories inside `backend/app/dependencies.py`.
- [ ] Initialize Alembic migrations using `alembic init alembic`.
- [ ] Generate the initial database migration script representing the PostgreSQL database tables.
- [ ] Run `alembic upgrade head` to apply database schema updates.

### Day 5: AI Client Wrappers & LangFuse Integration
- [ ] Build `backend/app/core/embeddings.py` using the OpenAI client wrapper pointing to `text-embedding-3-large`.
- [ ] Build `backend/app/core/vector_store.py` to handle async operations with Qdrant.
- [ ] Configure `backend/app/core/tracing.py` to initialize Langfuse clients.
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
