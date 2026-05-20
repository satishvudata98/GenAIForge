# GenAI Forge — Project Progress Checklist

Use this checklist to track your implementation progress across all 4 weeks of the build plan. 

---

## Progress Summary

- Week 1 completed day blocks: 7 of 7 (`Day 1` through `Day 7`)
- Week 1 in-progress day: none
- Remaining Week 1 day blocks: none

Current implementation:
- Done: repository scaffold, docker baseline, FastAPI bootstrap, request middleware, health/readiness/metrics, SQLAlchemy models, Alembic migration.
- Done: Day 5 wrapper layer for embeddings, Qdrant, Redis, and LangFuse integration hooks, plus manual LangFuse event verification.
- Done: Day 6 RAG ingestion schemas, ingestion service, and `POST /v1/rag/ingest` route with route tests.
- Done: Day 7 RAG retrieval, SSE query route, seed script, sample docs, and CI workflow.
- Done: full default local stack validation for backend, worker, frontend, Nginx, Prometheus, Grafana, and Jaeger.
- Pending: Week 2 implementation.

## 📅 Week 1: Foundation & Baseline RAG

- [x] **Day 1: Repository Setup**
  - [x] Initialize git repo and project root.
  - [x] Create folder structure: `backend/`, `frontend/`, `infra/`, `scripts/`.
  - [x] Set up `backend/pyproject.toml`, `requirements.txt` and frontend `package.json`.
  - [x] Create `.pre-commit-config.yaml` for Ruff and Prettier.
- [x] **Day 2: Docker Compose Environment**
  - [x] Configure `infra/docker-compose.yml` for all 10 services.
  - [x] Add health checks and named volumes.
  - [x] Validate environment file loader structure (`.env.example`).
  - [x] Spin up and verify the core local containers (`postgres`, `redis`, `qdrant`, `app`).
- [x] **Day 3: FastAPI Backend skeleton**
  - [x] Implement `backend/app/main.py` application factory.
  - [x] Setup Pydantic configs in `backend/app/config.py`.
  - [x] Add request logging and latency middlewares.
  - [x] Expose `/health`, `/readiness`, and `/metrics` endpoints.
- [x] **Day 4: Relational Databases & Migrations**
  - [x] Map PostgreSQL models (`users`, `rag_collections`, `request_log`).
  - [x] Setup SQLAlchemy session dependencies.
  - [x] Initialize Alembic and generate initial migrations.
  - [x] Apply database migrations (`alembic upgrade head`).
- [x] **Day 5: AI Client Wrappers & LangFuse Integration**
  - [x] Build `embeddings.py` (OpenAI `text-embedding-3-large`).
  - [x] Create `vector_store.py` (Qdrant client connectivity).
  - [x] Add Redis cache wrapper for async cache access.
  - [x] Set up LangFuse tracing hooks inside `tracing.py`.
  - [x] Verify test traces log correctly to the LangFuse dashboard.
- [x] **Day 6: RAG Ingestion Pipeline**
  - [x] Build LlamaIndex document chunking and indexing logic in `backend/app/rag/ingestion.py`.
  - [x] Implement API endpoint `POST /v1/rag/ingest`.
  - [x] Log collection stats in PostgreSQL `rag_collections`.
- [x] **Day 7: Streaming RAG Query API**
  - [x] Implement `backend/app/rag/retrieval.py` with Qdrant query and Cohere Rerank v3.
  - [x] Implement query API endpoint `POST /v1/rag/query` with SSE stream.
  - [x] Write `scripts/seed_qdrant.py` script.
  - [x] Configure GitHub Actions `ci.yml` pipeline.

---

## 📅 Week 2: Frontend Playground & Multi-Agent Board

- [ ] **Day 8: Semantic Caching & Rate Limiting**
  - [ ] Create Token Bucket rate-limiting middleware using Redis.
  - [ ] Integrate `GPTCache` on Redis with cosine similarity limit $\ge 0.95$.
  - [ ] Add cache indicator headers (`X-Cache: HIT / MISS`) to query API.
- [ ] **Day 9: Multi-Model Integration**
  - [ ] Integrate Groq (`llama3-70b`), Google Gemini (`gemini-1.5-flash`), and xAI (`grok-2`) into `llm_clients.py`.
  - [ ] Set up backoff retry handling with `tenacity`.
  - [ ] Implement token counting utilities per model provider.
- [ ] **Day 10: Research Agent Graph (LangGraph)**
  - [ ] Design graph state in `backend/app/agents/state.py`.
  - [ ] Create nodes (`plan`, `search`, `extract`, `synthesize`, `report`).
  - [ ] Implement Tavily Search and Wikipedia APIs as tools.
- [ ] **Day 11: Code Review Agent & Human-in-the-Loop**
  - [ ] Create Code Review state machine using LangGraph.
  - [ ] Set up Postgres database checkpoint saver (`PostgresSaver`).
  - [ ] Add approval interrupts at code suggestion nodes.
  - [ ] Implement API endpoint `POST /v1/agents/resume/{job_id}`.
- [ ] **Day 12: CrewAI Pipeline & Celery Workers**
  - [ ] Define Researcher, Writer, and Editor tasks using CrewAI.
  - [ ] Configure Celery workers inside `backend/app/workers/celery_app.py`.
  - [ ] Implement Celery task execution queues.
  - [ ] Build SSE routes to stream Celery task execution events.
- [ ] **Day 13: Next.js Bootstrap & RAG Playground UI**
  - [ ] Setup Next.js 14 App Router environment.
  - [ ] Install Tailwind CSS styling system.
  - [ ] Build RAG Playground interface with side-by-side comparison mode.
- [ ] **Day 14: Agent Board UI & React Flow**
  - [ ] Create Agent Board view `/agents`.
  - [ ] Build graph visualizer using `React Flow`.
  - [ ] Implement live agent logs and human-in-the-loop validation modals.

---

## 📅 Week 3: Full-Stack Observability & API Gateway

- [ ] **Day 15: LangFuse Instrumentation**
  - [ ] Instrument all LLM, agent, and retrieval calls with `@observe()` decorators.
  - [ ] Map token usage, API pricing, and custom spans (Qdrant, Cohere).
- [ ] **Day 16: Prometheus Metrics Setup**
  - [ ] Setup Prometheus gauges and counters in `backend/app/observability/metrics.py`.
  - [ ] Expose metrics via `/metrics` endpoint.
  - [ ] Setup Prometheus configuration targets.
- [ ] **Day 17: Grafana Dashboard Provisioning**
  - [ ] Provision Prometheus data source configs.
  - [ ] Write System Health Dashboard dashboard configs (`api_metrics.json`).
  - [ ] Write AI Performance Dashboard dashboard configs (`llm_metrics.json`).
- [ ] **Day 18: Distributed Tracing with OpenTelemetry**
  - [ ] Set up OpenTelemetry middleware and OTLP exporters.
  - [ ] Trace API requests, database queries, and Celery executions through Jaeger.
  - [ ] Propagate correlation ID `X-Request-ID` across all spans.
- [ ] **Day 19: RAGAS Evaluation Pipeline**
  - [ ] Build RAGAS calculation scripts checking faithfulness, recall, and precision.
  - [ ] Expose evaluation run endpoints (`POST /v1/eval/run`, `GET /v1/eval/results`).
  - [ ] Create PostgreSQL logs mapping evaluation scores.
- [ ] **Day 20: Observability Dashboard UI**
  - [ ] Create Observability interface page `/observability`.
  - [ ] Embed Grafana and LangFuse dashboards using secure iframe containers.
  - [ ] Build the RAGAS evaluation runner and scorecard comparison panels.
- [ ] **Day 21: API Gateway Control UI**
  - [ ] Build API Gateway interface view `/gateway`.
  - [ ] Build cache performance charts and rate-limit counters.
  - [ ] Create API Key generator panels.

---

## 📅 Week 4: Quality Verification & Cloud Deployment

- [ ] **Day 22: Backend Test Fixtures**
  - [ ] Write `backend/tests/conftest.py` setting up clean environments.
  - [ ] Mock embedding APIs, LLM calls, and Cohere rerank responses.
- [ ] **Day 23: API & RAG Integration Tests**
  - [ ] Test REST endpoint routes and error handlers using Pytest.
  - [ ] Test doc parser splits, vector indexing, and caching performance.
- [ ] **Day 24: Agent Graph Validation Tests**
  - [ ] Run test executions checking LangGraph node state updates.
  - [ ] Validate manual resume inputs and Celery task execution queues.
- [ ] **Day 25: Frontend Component Tests**
  - [ ] Configure the Vitest environment in Next.js.
  - [ ] Test UI components and Zustand state store actions.
  - [ ] Validate SSE data stream processing.
- [ ] **Day 26: Pre-Commit Checks & Makefile**
  - [ ] Verify Ruff and Prettier configurations.
  - [ ] Write clean `Makefile` shortcuts (e.g. `make test`, `make dev`).
  - [ ] Build system liveness check scripts (`scripts/health_check.sh`).
- [ ] **Day 27: Backend Deployment**
  - [ ] Deployed FastAPI application and Celery workers on Railway.
  - [ ] Setup PostgreSQL, Redis, and Qdrant container targets on Railway.
- [ ] **Day 28: Data Store Migrations**
  - [ ] Migrate database schemas to Supabase Postgres.
  - [ ] Migrate vector indices to Qdrant Cloud.
  - [ ] Update connection settings to point to Upstash Redis.
- [ ] **Day 29: Frontend & Observability Deployments**
  - [ ] Deploy Next.js frontend to Vercel.
  - [ ] Link production logs to LangFuse Cloud and Grafana Cloud.
- [ ] **Day 30: Production Smoke Tests & Review**
  - [ ] Run automated checks verifying production endpoints.
  - [ ] Seed cloud Qdrant collections.
  - [ ] Record product walkthrough video and finalize docs.
