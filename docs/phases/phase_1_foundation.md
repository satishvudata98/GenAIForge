# Phase 1: Foundation & Baseline RAG

This phase establishes the developer environment, spins up the Docker-based local services, and implements the baseline async retrieval-augmented generation (RAG) query and ingestion backend.

---

## 🎯 Phase Goals
- Spin up a cohesive, local development environment with 10 integrated services running under Docker Compose.
- Establish the backend web API skeleton, relational database schemas, and migration mechanics.
- Build the core client wrappers for embeddings, vector indexing, caching, and observability.
- Deliver a production-ready async ingestion pipeline and an SSE streaming retrieval-augmented generation query API with source citations.

---

## 🛠️ Features Covered
1. **Multi-Service Docker Compose Environment**: Orchestration of PostgreSQL, Qdrant, Redis, Prometheus, Grafana, Jaeger, LangFuse Server, Nginx, Celery, FastAPI, and Next.js.
2. **FastAPI Backbone**: Core settings system using Pydantic, standard request/response envelopes, and status checks.
3. **Database Migration Pipeline**: Automatic relational schema setup via SQLAlchemy and Alembic.
4. **Document Ingestion API**: Endpoint to parse documents, chunk text recursively, calculate high-dimension embeddings, and upsert them to Qdrant.
5. **RAG Streaming Query Engine**: Hybrid query path leveraging Qdrant ANN search, Cohere Rerank v3, and streamed answers using OpenAI `gpt-4o-mini` via Server-Sent Events (SSE).
6. **Seed Script**: Script to seed Qdrant with domain-specific mock documentation for testing.
7. **CI/CD Foundation**: GitHub Actions workflow to lint (Ruff/ESLint) and test on Pull Requests.

---

## 🗂️ Technical Modules Involved

```
backend/
├── app/
│   ├── main.py                     # App factory and health check registrations
│   ├── config.py                   # Pydantic Settings reading environment variables
│   ├── dependencies.py             # DB sessions and HTTP client dependencies
│   ├── api/v1/
│   │   ├── router.py               # Aggregated endpoint router
│   │   ├── rag.py                  # Ingest, query, list collections, delete collections
│   │   └── health.py               # Liveness and readiness indicators
│   ├── core/
│   │   ├── embeddings.py           # text-embedding-3-large integration wrapper
│   │   ├── vector_store.py         # Qdrant client connection and index builder
│   │   ├── cache.py                # Redis cache connectivity
│   │   └── tracing.py              # LangFuse SDK wrapper for trace exports
│   └── rag/
│       ├── pipeline.py             # Core retrieval and context assembly
│       ├── ingestion.py            # Recursive character splitting logic
│       └── retrieval.py            # Search and Cohere reranker client interaction
scripts/
└── seed_qdrant.py                  # Seed script for initial setup
```

---

## 🌐 Backend, Frontend, and AI Integrations
- **Backend-to-Vector-Store**: The FastAPI app connects asynchronously to the Qdrant service on port `6333` using the `qdrant-client` library.
- **Backend-to-AI-APIs**:
  - `text-embedding-3-large` (OpenAI API) for generating 3072-dimension vectors.
  - `gpt-4o-mini` (OpenAI API) via streamed chat completion for synthesis.
  - `Cohere Rerank v3` (Cohere API) to rerank vector search candidates.
- **Observability Hooks**: The LangFuse Python SDK intercepts LLM calls, recording traces asynchronously to the `langfuse-server` container on port `3001`.
- **System Metrics**: Custom metrics are logged to Prometheus via the `prometheus-client` package and made scrapable at `/metrics` for Grafana dashboards.

---

## 🗄️ Database Changes (PostgreSQL Schema)
The following tables are generated via Alembic migration scripts during setup:
- **`users`**: To authenticate clients and manage user API tokens.
- **`rag_collections`**: Tracks metadata for user collections stored inside Qdrant (e.g., total documents, chunk sizes, embedding model used).
- **`request_log`**: Saves execution logs for endpoints, storing elapsed latency, response codes, token usage, estimated costs, and semantic cache hits/misses.

*Detailed SQL schemas can be reviewed in the **[Database Design Spec](file:///E:/GenAIForge/docs/architecture/database_design.md)**.*

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

---

## 🚢 Deployment Considerations
- Ensure all host URLs for Postgres, Redis, and Qdrant are loaded strictly from standard `.env` environment variables.
- Volume structures must mount Postgres (`postgres_data`), Redis (`redis_data`), and Qdrant (`qdrant_data`) configurations to persistent system directories.
- In staging, Nginx must be configured to pass headers (such as `X-Request-ID` and `Authorization` bearer schemas) cleanly to backend targets.
