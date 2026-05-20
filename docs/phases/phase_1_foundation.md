# Phase 1: Foundation & Baseline RAG

This phase establishes the developer environment, spins up the Docker-based local services, and implements the baseline async retrieval-augmented generation (RAG) query and ingestion backend.

---

## 🎯 Phase Goals
- Spin up a cohesive, local development environment with 10 integrated services running under Docker Compose.
- Establish the backend web API skeleton, relational database schemas, and migration mechanics.
- Build the core client wrappers for embeddings, vector indexing, caching, and observability.
- Deliver a production-ready async ingestion pipeline and an SSE streaming retrieval-augmented generation query API with source citations.

## ✅ Current Phase 1 Status (May 20, 2026)
- Implemented: backend app factory, request middleware, `/v1/health`, `/v1/readiness`, `/metrics`, SQLAlchemy models, Alembic migration, Dockerfiles, frontend shell, core AI wrappers, RAG ingestion schemas/service/route, RAG retrieval/SSE query flow, seed tooling, and the core Compose baseline.
- Validated: local `pytest` health test, full default-stack container boot, live health/readiness endpoints through both the app and Nginx, and the initial migration against Postgres.
- Validated: local wrapper regression test for the new Day 5 core modules.
- Validated: local Day 6 ingestion route tests with mocked ingestion dependencies.
- Validated: local Day 7 query route tests and the seed script entrypoint.
- Validated: wrapper-level tracing instrumentation and manual LangFuse event export.
- Remaining in Phase 1: no open implementation tasks for Week 1 scope.

---

## 🛠️ Features Covered
1. **Multi-Service Docker Compose Environment**: Orchestration of PostgreSQL, Qdrant, Redis, Prometheus, Grafana, Jaeger, Nginx, Celery, FastAPI, and Next.js, with `langfuse-server` defined under an optional `observability` profile.
2. **FastAPI Backbone**: Core settings system using Pydantic, request/response middleware, request ID propagation, Prometheus metrics, and status checks.
3. **Database Migration Pipeline**: Automatic relational schema setup via SQLAlchemy and Alembic.
4. **Document Ingestion API**: Implemented multipart endpoint that parses documents, chunks text recursively, calculates embeddings, upserts them to Qdrant, and updates `rag_collections` metadata.
5. **RAG Streaming Query Engine**: Implemented query path leveraging Qdrant ANN search, Cohere Rerank v3, and streamed answers using OpenAI `gpt-4o-mini` via Server-Sent Events (SSE).
6. **Seed Script**: Implemented script to seed Qdrant with sample documentation for testing.
7. **CI/CD Foundation**: Implemented GitHub Actions workflow that runs Ruff and backend pytest checks.

---

## 🗂️ Technical Modules Involved

```
backend/
├── app/
│   ├── main.py                     # App factory and health check registrations
│   ├── config.py                   # Pydantic Settings reading environment variables
│   ├── middleware.py               # Request ID, request logging, and latency metrics
│   ├── dependencies.py             # DB sessions and HTTP client dependencies
│   ├── worker.py                   # Celery application bootstrap
│   ├── core/
│   │   ├── embeddings.py           # OpenAI embedding wrapper
│   │   ├── vector_store.py         # Qdrant async wrapper
│   │   ├── cache.py                # Redis async wrapper
│   │   └── tracing.py              # LangFuse wrapper and observe decorator
│   ├── api/v1/
│   │   ├── router.py               # Aggregated endpoint router
│   │   ├── health.py               # Liveness and readiness indicators
│   │   └── rag.py                  # Ingest and query routes
│   ├── models/
│   │   ├── db.py                   # Phase 1 SQLAlchemy models
│   │   └── schemas.py              # Standard API and ingest/query schemas
│   └── rag/
│       ├── ingestion.py            # Document parsing, chunking, embedding, and upsert
│       ├── retrieval.py            # Retrieval and Cohere reranking
│       └── pipeline.py             # OpenAI streaming answer generation
├── alembic/
│   ├── env.py                      # Async migration environment
│   └── versions/
│       └── 0001_initial_schema.py  # Initial users / rag_collections / request_log tables
├── Dockerfile
└── tests/
    ├── test_health.py              # Bootstrap health regression test
    ├── test_core.py                # Wrapper regression tests
  ├── test_ingest.py              # Ingest route regression tests
  └── test_query.py               # Query route regression tests
scripts/
├── seed_qdrant.py                  # Sample collection seeding script
└── sample_docs/
  ├── platform_overview.md
  └── rag_notes.md
frontend/
├── app/
│   ├── layout.tsx                  # Initial app shell
│   ├── page.tsx                    # Week 1 landing page
│   └── globals.css                 # Base frontend styling
└── Dockerfile
```

---

## 🌐 Backend, Frontend, and AI Integrations
- **Backend-to-Vector-Store**: The FastAPI app connects asynchronously to the Qdrant service on port `6333` using the `qdrant-client` library.
- **Backend-to-AI-APIs**:
  - `text-embedding-3-large` (OpenAI API) for generating 3072-dimension vectors.
  - `gpt-4o-mini` (OpenAI API) via streamed chat completion for synthesis.
  - `Cohere Rerank v3` (Cohere API) to rerank vector search candidates.
- **Observability Hooks**: LangFuse wrapper initialization is implemented, but live trace export is still pending verification.
- **System Metrics**: Request metrics are exposed from FastAPI at `/metrics` via the `prometheus-client` package.

---

## 🗄️ Database Changes (PostgreSQL Schema)
The following tables are generated via Alembic migration scripts during setup:
- **`users`**: To authenticate clients and manage user API tokens.
- **`rag_collections`**: Tracks metadata for user collections stored inside Qdrant (e.g., total documents, chunk sizes, embedding model used).
- **`request_log`**: Saves execution logs for endpoints, storing elapsed latency, response codes, token usage, estimated costs, and semantic cache hits/misses.

*Detailed SQL schemas can be reviewed in the **[Database Design Spec](file:///E:/GenAIForge/docs/architecture/database_design.md)**.*

Implementation note: the initial migration has been applied successfully against the local Postgres container.

---

## 🔌 APIs & Services Required

### Ingestion Endpoint
* **URI**: `POST /v1/rag/ingest`
* **Content-Type**: `multipart/form-data`
* **Payload**:
  ```json
  {
    "files": "List of Uploaded Files",
    "collection_name": "string",
    "chunk_size": 512,
    "chunk_overlap": 64
  }
  ```
* **Returns**: Status details containing document, chunk counts, and estimated cost of embedding generation.

### Streaming Query Endpoint
* **URI**: `POST /v1/rag/query`
* **Content-Type**: `application/json`
* **Payload**:
  ```json
  {
    "query": "string",
    "collection_id": "UUID",
    "model": "gpt-4o-mini",
    "top_k": 5,
    "use_reranker": true
  }
  ```
* **Response Format**: Server-Sent Events (SSE) streaming events:
  - `chunk`: Contains partial markdown tokens of the response.
  - `source`: List of document sources with matching relevance scores and parent document names.
  - `meta`: Cost and latency summaries.
  - `done`: Signal marking completion.

---

## 📊 Estimated Complexity & Risks

### Estimated Complexity: Medium
- Setting up the 10-container Docker environment with appropriate health check parameters requires careful port mapping and network bridging.
- Handling async SSE generator functions cleanly inside FastAPI without blocking worker loops requires proper implementation of Python generators and streaming HTTP responses.

### Key Risks & Mitigation
1. **API Rate Limiting & Timeouts during Ingestion**: High-volume uploads might exhaust OpenAI rate limits.
   * *Mitigation*: Implement batch embedding calls with backoff retry helpers (`tenacity` module) in the client wrapper.
2. **Qdrant Connection Latency**: Qdrant connection lags can raise the p95 response time.
   * *Mitigation*: Maintain persistent async connection pools and run health checks during setup.
3. **OpenAI Cost Spikes**: Unchecked evaluation judge calls or large uploads may deplete credits.
   * *Mitigation*: Implement a hard-limit middleware to cut off external API requests if a daily budget limit is reached ($5).

---

## 🧪 Testing Requirements
- **Integration Tests**: Execute `pytest backend/tests/test_rag.py` using real test database configurations and mocked HTTP responses for the external AI providers (OpenAI, Cohere).
- **Endpoint Performance Verification**: Validate that `/health` resolves in less than 50ms, and `/metrics` exports valid Prometheus headers.
- **Generator Validation**: Verify that streaming buffers flush chunks progressively rather than caching the full response until compilation.

Current status: focused regression coverage exists for health, wrapper initialization, ingestion, and query route behavior.

---

## 🚢 Deployment Considerations
- Ensure all host URLs for Postgres, Redis, and Qdrant are loaded strictly from standard `.env` environment variables.
- Volume structures must mount Postgres (`postgres_data`), Redis (`redis_data`), and Qdrant (`qdrant_data`) configurations to persistent system directories.
- In staging, Nginx must be configured to pass headers (such as `X-Request-ID` and `Authorization` bearer schemas) cleanly to backend targets.
- Host-side backend tooling currently reads from `backend/.env`, while Docker Compose uses the repository root `.env`.
