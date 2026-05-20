# GenAI Forge — Full Application Plan
> A production-grade GenAI developer showcase platform demonstrating every layer of the modern AI engineering stack.
> This document is written for an AI agent to plan, scaffold, and build the application end-to-end.

---

## 1. Project Overview

### 1.1 What This Is
GenAI Forge is a multi-module web application that serves as a live, running portfolio for a GenAI engineer. Every module is a working tool — not a mock. The app demonstrates mastery across LLM orchestration, retrieval-augmented generation, multi-agent systems, production observability, API design, and cloud-native infrastructure.

### 1.2 Core Goals
- Demonstrate end-to-end RAG pipeline with production-quality embeddings and reranking
- Show multi-agent orchestration with visible execution graphs
- Implement full observability: LLM tracing, system metrics, distributed tracing
- Build a cloud-native architecture from day one — each service maps to a specific cloud migration target
- Minimize spend: OpenAI credits for quality-critical paths only; everything else is free-tier or open-source
- One `docker compose up` starts the entire platform locally

### 1.3 Application Name
**GenAI Forge** — tagline: *"Where AI systems are built, observed, and improved."*

---

## 2. Final Tech Stack

### 2.1 Quality-Critical — OpenAI Credits
| Component | Model / Tool | Why |
|---|---|---|
| Embeddings | `text-embedding-3-large` (3072 dims) | Top MTEB benchmark scores; $0.13/1M tokens |
| Reranking | Cohere Rerank v3 (free 1k req/month) | Cross-encoder accuracy; free tier sufficient |
| LLM judge (eval) | `gpt-4o` | Highest reasoning for RAGAS faithfulness scoring |
| Primary LLM | `gpt-4o-mini` | Best quality/cost ratio for chat and structured outputs |

### 2.2 Free-Tier LLMs (Model Comparison Module)
| Model | Provider | Use Case |
|---|---|---|
| `llama3-70b-8192` | Groq (free) | Speed comparison, agent sub-tasks |
| `gemini-1.5-flash` | Google AI Studio (free) | Long-context demos, multimodal |
| `grok-2` | xAI (free tier) | Model diversity in comparison panel |

### 2.3 Infrastructure Services
| Service | Local (Docker) | Cloud Migration Target |
|---|---|---|
| Vector DB | Qdrant (Docker) | Qdrant Cloud free tier (1GB) |
| Relational DB | PostgreSQL 16 | Supabase free tier (500MB) |
| Cache + Semantic Cache | Redis 7 + GPTCache | Upstash Redis (10k req/day free) |
| Job Queue | Celery + Redis | Upstash QStash |
| LLM Observability | LangFuse (self-hosted Docker) | LangFuse Cloud free tier |
| Metrics | Prometheus + Grafana | Grafana Cloud free (10k series) |
| Distributed Tracing | OpenTelemetry + Jaeger | Any OTLP backend |
| Error Tracking | Sentry (free tier SDK) | Sentry.io free |

### 2.4 Backend
| Component | Technology |
|---|---|
| API Framework | FastAPI (Python 3.11) |
| RAG Pipeline | LlamaIndex |
| Agent Orchestration | LangGraph |
| Multi-agent (demo) | CrewAI |
| Async Task Worker | Celery |
| Reverse Proxy | Nginx |
| Schema Validation | Pydantic v2 |
| Auth | JWT + OAuth2 (FastAPI built-in) |

### 2.5 Frontend
| Component | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS v3 |
| State | Zustand |
| Streaming UI | Native SSE (EventSource) |
| Charts / Viz | Recharts + D3 |
| Agent Flow Viz | React Flow |
| Deploy | Vercel (free tier) |

### 2.6 DevOps / CI
| Component | Technology |
|---|---|
| Containerization | Docker + Docker Compose v2 |
| CI/CD | GitHub Actions |
| Linting | Ruff (Python), ESLint (JS) |
| Formatting | Black (Python), Prettier (JS) |
| Testing | Pytest + HTTPX (backend), Vitest (frontend) |
| Pre-commit hooks | pre-commit |
| Secrets | `.env` locally, GitHub Secrets in CI |

---

## 3. Repository Structure

```
genai-forge/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Lint, test, build on every PR
│       └── deploy.yml              # Deploy on merge to main
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app factory
│   │   ├── config.py               # Pydantic settings (env vars)
│   │   ├── dependencies.py         # Shared FastAPI dependencies
│   │   │
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── router.py       # Aggregate all v1 routes
│   │   │   │   ├── chat.py         # /v1/chat streaming endpoint
│   │   │   │   ├── rag.py          # /v1/rag/ingest, /v1/rag/query
│   │   │   │   ├── agents.py       # /v1/agents/run, /v1/agents/status
│   │   │   │   ├── eval.py         # /v1/eval/run, /v1/eval/results
│   │   │   │   └── health.py       # /health, /ready
│   │   │
│   │   ├── core/
│   │   │   ├── embeddings.py       # OpenAI embeddings client wrapper
│   │   │   ├── reranker.py         # Cohere reranker wrapper
│   │   │   ├── llm_clients.py      # Unified LLM client (OpenAI, Groq, Gemini, Grok)
│   │   │   ├── vector_store.py     # Qdrant client wrapper
│   │   │   ├── cache.py            # Redis + GPTCache semantic cache
│   │   │   └── tracing.py          # LangFuse + OpenTelemetry setup
│   │   │
│   │   ├── rag/
│   │   │   ├── pipeline.py         # Full RAG pipeline (LlamaIndex)
│   │   │   ├── ingestion.py        # Doc loading, chunking, embedding, upsert
│   │   │   ├── retrieval.py        # Query → embed → Qdrant → rerank
│   │   │   └── evaluation.py       # RAGAS scoring pipeline
│   │   │
│   │   ├── agents/
│   │   │   ├── graph.py            # LangGraph state machine definitions
│   │   │   ├── nodes.py            # Individual agent node functions
│   │   │   ├── tools.py            # Tool definitions (search, code exec, etc.)
│   │   │   ├── crew.py             # CrewAI pipeline definitions
│   │   │   └── state.py            # Agent state schemas (Pydantic)
│   │   │
│   │   ├── workers/
│   │   │   ├── celery_app.py       # Celery app factory
│   │   │   └── tasks.py            # Async task definitions
│   │   │
│   │   ├── models/
│   │   │   ├── db.py               # SQLAlchemy models
│   │   │   └── schemas.py          # Pydantic request/response schemas
│   │   │
│   │   └── observability/
│   │       ├── metrics.py          # Prometheus metrics definitions
│   │       ├── middleware.py       # Request logging, latency middleware
│   │       └── langfuse_hooks.py   # LangFuse callback handlers
│   │
│   ├── tests/
│   │   ├── test_rag.py
│   │   ├── test_agents.py
│   │   ├── test_api.py
│   │   └── conftest.py
│   │
│   ├── alembic/                    # DB migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Landing / module selector
│   │   ├── playground/
│   │   │   └── page.tsx            # Module 1: RAG Playground
│   │   ├── agents/
│   │   │   └── page.tsx            # Module 2: Agent Board
│   │   ├── observability/
│   │   │   └── page.tsx            # Module 3: Eval Dashboard
│   │   └── gateway/
│   │       └── page.tsx            # Module 4: API Gateway
│   │
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx      # Streaming message renderer
│   │   │   ├── MessageBubble.tsx
│   │   │   └── SourceCitations.tsx # RAG source display
│   │   ├── rag/
│   │   │   ├── DocumentUploader.tsx
│   │   │   ├── RetrievalTrace.tsx  # Show retrieved chunks + scores
│   │   │   └── RagToggle.tsx       # With/without RAG comparison
│   │   ├── agents/
│   │   │   ├── AgentGraph.tsx      # React Flow graph of agent execution
│   │   │   ├── AgentLog.tsx        # Live streaming agent thoughts
│   │   │   └── HumanInLoop.tsx     # Approval injection UI
│   │   ├── observability/
│   │   │   ├── TraceViewer.tsx     # LangFuse trace embed
│   │   │   ├── MetricsPanel.tsx    # Grafana iframe or custom charts
│   │   │   └── EvalScoreCard.tsx   # RAGAS metric display
│   │   └── shared/
│   │       ├── ModelSelector.tsx
│   │       ├── CacheIndicator.tsx  # Hit / Miss badge
│   │       └── LatencyBadge.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                  # Typed API client
│   │   ├── sse.ts                  # SSE streaming hook
│   │   └── store.ts                # Zustand stores
│   │
│   ├── Dockerfile
│   └── package.json
│
├── infra/
│   ├── docker-compose.yml          # Full local stack
│   ├── docker-compose.dev.yml      # Overrides for hot reload
│   ├── nginx/
│   │   └── nginx.conf
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   ├── datasources/
│   │   └── dashboards/
│   │       ├── api_metrics.json
│   │       └── llm_metrics.json
│   └── langfuse/
│       └── docker-compose.langfuse.yml
│
├── scripts/
│   ├── seed_qdrant.py              # Seed vector DB with sample docs
│   ├── run_eval.py                 # Run RAGAS eval suite
│   └── health_check.sh
│
├── .env.example
├── .pre-commit-config.yaml
├── Makefile                        # make dev, make test, make build
└── README.md
```

---

## 4. Module Specifications

---

### Module 1 — RAG Playground

#### Purpose
Demonstrate a production-quality RAG pipeline: document ingestion, chunking strategy, embedding with `text-embedding-3-large`, Qdrant vector search, Cohere reranking, and streamed answer generation with source citations.

#### Backend Endpoints
```
POST /v1/rag/ingest
  Body: { files: File[], collection_name: str, chunk_size: int, chunk_overlap: int }
  Action: Load → chunk (recursive text splitter) → embed (OpenAI 3-large) → upsert Qdrant
  Returns: { collection_id, doc_count, chunk_count, embedding_cost_usd }

POST /v1/rag/query  (SSE streaming)
  Body: { query: str, collection_id: str, model: str, top_k: int, use_reranker: bool }
  Pipeline:
    1. Embed query with text-embedding-3-large
    2. Check Redis semantic cache (GPTCache, cosine threshold 0.95)
    3. Cache HIT → stream cached response with [CACHE HIT] header
    4. Cache MISS → Qdrant ANN search (top_k * 3 candidates)
    5. Cohere Rerank v3 → top_k results
    6. Build prompt with retrieved chunks
    7. Stream gpt-4o-mini response via SSE
    8. Store in semantic cache
    9. Emit LangFuse trace with full pipeline
  SSE Events: { type: "chunk"|"source"|"meta"|"done", data: ... }

GET /v1/rag/collections
  Returns: list of all Qdrant collections with doc counts

DELETE /v1/rag/collections/{collection_id}
```

#### RAG Pipeline Detail (LlamaIndex)
```python
# Chunking strategy
chunk_size = 512          # tokens
chunk_overlap = 64        # tokens
splitter = RecursiveCharacterTextSplitter

# Embedding
model = "text-embedding-3-large"
dimensions = 3072         # full dims for local Qdrant

# Qdrant index config
hnsw_config = {
    "m": 16,              # connections per node (higher = better recall, more memory)
    "ef_construct": 200   # build time accuracy
}
distance = "Cosine"

# Retrieval
initial_top_k = 20        # fetch 20 from Qdrant
rerank_top_k = 5          # Cohere reranks to top 5
final_context_chunks = 5  # send to LLM
```

#### Frontend Features
- Document upload panel (PDF, TXT, MD, DOCX) with progress indicator
- Collection manager (create, list, delete)
- Chat interface with streaming response
- "Retrieval trace" panel: show top-5 retrieved chunks with similarity scores before and after reranking
- Toggle: "RAG ON / OFF" — same query, compare answers side by side
- Model selector: gpt-4o-mini, groq/llama3-70b, gemini-flash
- Cache indicator badge: HIT (green) / MISS (gray) with latency display
- Token usage and estimated cost per query

---

### Module 2 — Multi-Agent Board

#### Purpose
Demonstrate multi-agent orchestration using LangGraph for complex state machines and CrewAI for role-based pipelines. Show agent execution as a live visual graph where nodes activate in real time.

#### Pre-built Agent Pipelines

**Pipeline A — Research Agent (LangGraph)**
```
State machine nodes:
  plan_research → web_search → extract_facts → cross_check → synthesize → write_report
Edges:
  plan_research → web_search (always)
  web_search → extract_facts (always)
  extract_facts → cross_check (if facts > 3)
  extract_facts → synthesize (if facts <= 3)
  cross_check → synthesize (always)
  synthesize → write_report (always)
  write_report → END
  Any node → handle_error → END (on exception)
Tools available: tavily_search (free), wikipedia_lookup, calculator
```

**Pipeline B — Code Review Agent (LangGraph)**
```
State machine nodes:
  parse_code → analyze_complexity → check_security → suggest_improvements → format_report
Uses: gpt-4o-mini for analysis, structured JSON outputs via response_format
Human-in-loop: pause at suggest_improvements for user to approve/modify suggestions
```

**Pipeline C — Content Pipeline (CrewAI)**
```
Agents:
  Researcher: role="Senior Research Analyst", goal="Find key facts about topic"
  Writer: role="Content Writer", goal="Write engaging article from research"
  Editor: role="Editor", goal="Polish and fact-check the article"
Tasks: research_task → write_task → edit_task (sequential)
Model: gpt-4o-mini for all agents
```

#### Backend Endpoints
```
POST /v1/agents/run
  Body: { pipeline: "research"|"code_review"|"content", input: str, config: dict }
  Action: Start Celery async task, return job_id immediately
  Returns: { job_id: str, status: "queued" }

GET /v1/agents/status/{job_id}  (SSE streaming)
  Streams agent events as they happen:
  SSE Events:
    { type: "node_start", data: { node: str, input: dict } }
    { type: "node_end", data: { node: str, output: dict, duration_ms: int } }
    { type: "tool_call", data: { tool: str, input: str, output: str } }
    { type: "llm_call", data: { model: str, tokens: int, latency_ms: int } }
    { type: "human_input_required", data: { node: str, context: str } }
    { type: "done", data: { result: str, total_tokens: int, total_duration_ms: int } }

POST /v1/agents/resume/{job_id}
  Body: { human_input: str }
  Action: Resume a paused human-in-loop pipeline
```

#### Frontend Features
- Pipeline selector with description of each agent workflow
- Input box to start a pipeline run
- React Flow graph visualization: nodes light up (amber = running, green = done, red = error) in real time as SSE events arrive
- Agent thought log: streaming panel showing each node's input/output/tool calls
- Human-in-loop UI: when pipeline pauses, show a text input to inject feedback and resume
- Run history: list of past runs with status, duration, token usage
- Estimated cost per run

---

### Module 3 — Eval & Observability Dashboard

#### Purpose
Show production observability: every LLM call is traced end-to-end in LangFuse; system metrics (latency, throughput, error rate, token usage) are in Grafana; RAG quality is scored with RAGAS. This module separates a junior from a senior GenAI engineer.

#### LangFuse Integration
Every LLM call across the entire app uses LangFuse tracing:
```python
# In every LLM function:
@observe(name="rag_query_pipeline")
async def rag_query(query: str, collection_id: str) -> str:
    with langfuse.trace(name="embed_query") as span:
        embedding = await embed(query)
        span.update(output={"dims": len(embedding)})

    with langfuse.trace(name="qdrant_search") as span:
        results = await qdrant.search(embedding, top_k=20)
        span.update(output={"count": len(results)})

    with langfuse.trace(name="cohere_rerank") as span:
        reranked = await cohere.rerank(query, results)
        span.update(output={"top_score": reranked[0].relevance_score})

    with langfuse.trace(name="llm_generate") as span:
        response = await llm.stream(prompt)
        span.update(output={"tokens": response.usage.total_tokens})
```

Every trace includes: user_id, session_id, model, prompt, response, latency per step, token counts, cost estimate, cache hit/miss.

#### Prometheus Metrics (custom)
Expose `/metrics` endpoint with:
```
# LLM metrics
genai_forge_llm_requests_total{model, endpoint, status}
genai_forge_llm_latency_seconds{model, endpoint} (histogram)
genai_forge_llm_tokens_total{model, type="input|output"}
genai_forge_llm_cost_usd_total{model}

# RAG metrics
genai_forge_rag_queries_total{collection, cache_hit}
genai_forge_rag_retrieval_latency_seconds (histogram)
genai_forge_rag_rerank_latency_seconds (histogram)
genai_forge_rag_chunk_scores{position} (gauge, avg score at each rank)

# Agent metrics
genai_forge_agent_runs_total{pipeline, status}
genai_forge_agent_duration_seconds{pipeline} (histogram)
genai_forge_agent_node_executions_total{pipeline, node}

# API metrics
genai_forge_api_requests_total{endpoint, method, status_code}
genai_forge_api_latency_seconds{endpoint} (histogram)
genai_forge_cache_operations_total{type="hit|miss|set"}
```

#### Grafana Dashboards
Two pre-built dashboard JSON files (committed to repo):

**Dashboard 1: API & System Health**
- Request rate (req/min) time series
- p50 / p95 / p99 latency time series
- Error rate (5xx) gauge
- Cache hit rate gauge
- Active Celery workers

**Dashboard 2: LLM & AI Quality**
- Total tokens/min by model (stacked bar)
- Estimated cost/hour
- RAG avg retrieval score over time
- Agent run success rate by pipeline
- LLM latency by model comparison

#### RAGAS Evaluation Pipeline
```
POST /v1/eval/run
  Body: {
    collection_id: str,
    test_set: [{ question: str, ground_truth: str }],
    judge_model: "gpt-4o"   # always GPT-4o for eval quality
  }
  Action:
    For each test question:
      1. Run full RAG pipeline (embed → search → rerank → generate)
      2. Capture: question, answer, retrieved_contexts, ground_truth
    Compute RAGAS metrics:
      - faithfulness: is answer grounded in retrieved context?
      - answer_relevancy: does answer address the question?
      - context_precision: are retrieved chunks relevant?
      - context_recall: are all needed facts retrieved?
    Store results in PostgreSQL eval_runs table
    Return aggregate scores + per-question breakdown

GET /v1/eval/results
  Returns: all eval runs with scores, model, collection, timestamp

GET /v1/eval/compare?run_a={id}&run_b={id}
  Returns: side-by-side score comparison (for A/B prompt testing)
```

#### Frontend Features
- LangFuse embed: iframe to self-hosted LangFuse showing live traces
- Custom metrics panel (Recharts): request rate, latency p95, token usage, cost — pulling from `/metrics` or a custom `/v1/metrics/summary` endpoint
- Eval runner: pick a collection, upload a test set CSV (question, ground_truth), run eval, see scores
- A/B comparison: run same test set with two different prompts or models, compare RAGAS scores side by side
- Grafana panel embed (iframe to Grafana public dashboard)

---

### Module 4 — API Gateway

#### Purpose
Demonstrate production API design: semantic caching, rate limiting, request ID propagation, structured error handling, and auto-generated documentation.

#### Gateway Features

**Semantic Cache (GPTCache + Redis)**
```python
# On every /v1/chat and /v1/rag/query request:
cache_key = cosine_similarity_lookup(
    query_embedding,
    threshold=0.95,        # treat queries as "same" if similarity >= 0.95
    ttl=3600               # 1 hour cache
)
if cache_key:
    return cached_response with header: X-Cache: HIT
else:
    response = await generate()
    store_in_cache(query_embedding, response)
    return response with header: X-Cache: MISS
```

**Rate Limiting (Token Bucket)**
```python
# Per API key limits:
/v1/chat:           20 requests/min, 100 requests/hour
/v1/rag/query:      30 requests/min, 200 requests/hour
/v1/agents/run:     5 requests/min, 20 requests/hour
/v1/eval/run:       2 requests/min, 10 requests/hour

# Headers returned:
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 17
X-RateLimit-Reset: 1718000060
```

**Request Tracing**
Every request gets a `X-Request-ID` UUID. This ID flows through:
- Nginx access log
- FastAPI request log
- Every LangFuse span
- Every Prometheus metric label
- PostgreSQL request_log table

This enables: one ID → full trace across all systems.

**Structured Error Responses**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Retry after 60 seconds.",
    "request_id": "req_01j2abc...",
    "retry_after": 60
  }
}
```

#### Backend Endpoints (Gateway-specific)
```
GET /v1/gateway/stats
  Returns: { cache_hit_rate, total_requests, avg_latency_ms, active_rate_limits }

POST /v1/gateway/cache/invalidate
  Body: { collection_id: str }   # invalidate cache for a specific RAG collection

GET /v1/gateway/keys
  Returns: list of API keys with usage stats (for demo purposes)

POST /v1/gateway/keys
  Creates a new API key for demo
```

#### Frontend Features
- Live gateway stats: requests/min, cache hit rate, avg latency, active connections
- Cache visualizer: stream of recent requests showing HIT (green) / MISS (gray) with query preview and latency
- Rate limit monitor: show current usage vs limit per endpoint
- API key manager (demo): create keys, see per-key usage
- OpenAPI docs link (auto-generated at `/docs`)

---

## 5. Data Models (PostgreSQL)

```sql
-- Users (demo auth)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  api_key TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RAG collections
CREATE TABLE rag_collections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name TEXT NOT NULL,
  qdrant_collection_name TEXT UNIQUE NOT NULL,
  doc_count INT DEFAULT 0,
  chunk_count INT DEFAULT 0,
  embedding_model TEXT DEFAULT 'text-embedding-3-large',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Request log (all API requests)
CREATE TABLE request_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  method TEXT NOT NULL,
  status_code INT NOT NULL,
  latency_ms INT NOT NULL,
  user_id UUID REFERENCES users(id),
  cache_hit BOOLEAN,
  model TEXT,
  tokens_in INT,
  tokens_out INT,
  cost_usd NUMERIC(10,6),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent runs
CREATE TABLE agent_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT UNIQUE NOT NULL,
  pipeline TEXT NOT NULL,
  status TEXT NOT NULL,   -- queued | running | paused | done | error
  input TEXT NOT NULL,
  output TEXT,
  total_tokens INT,
  total_cost_usd NUMERIC(10,6),
  duration_ms INT,
  user_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Eval runs (RAGAS)
CREATE TABLE eval_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  collection_id UUID REFERENCES rag_collections(id),
  judge_model TEXT NOT NULL,
  prompt_template TEXT,
  faithfulness NUMERIC(4,3),
  answer_relevancy NUMERIC(4,3),
  context_precision NUMERIC(4,3),
  context_recall NUMERIC(4,3),
  question_count INT,
  cost_usd NUMERIC(10,4),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Eval questions (per eval run)
CREATE TABLE eval_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  eval_run_id UUID REFERENCES eval_runs(id),
  question TEXT NOT NULL,
  ground_truth TEXT NOT NULL,
  generated_answer TEXT,
  retrieved_contexts JSONB,
  faithfulness NUMERIC(4,3),
  answer_relevancy NUMERIC(4,3),
  context_precision NUMERIC(4,3),
  context_recall NUMERIC(4,3)
);
```

---

## 6. Docker Compose Architecture

### 6.1 Services
```yaml
# infra/docker-compose.yml

services:

  # ── Application ──────────────────────────────────────────
  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres, redis, qdrant]
    networks: [genai-net]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  celery-worker:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info -Q agents,evals
    env_file: .env
    depends_on: [redis, postgres]
    networks: [genai-net]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    networks: [genai-net]

  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes: ["./infra/nginx/nginx.conf:/etc/nginx/nginx.conf:ro"]
    depends_on: [backend, frontend]
    networks: [genai-net]

  # ── Data stores ───────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: genai_forge
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes: ["postgres_data:/var/lib/postgresql/data"]
    ports: ["5432:5432"]
    networks: [genai-net]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]
    volumes: ["qdrant_data:/qdrant/storage"]
    networks: [genai-net]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: ["redis_data:/data"]
    command: redis-server --appendonly yes
    networks: [genai-net]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  # ── Observability ─────────────────────────────────────────
  langfuse-server:
    image: ghcr.io/langfuse/langfuse:latest
    ports: ["3001:3000"]
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/langfuse
      NEXTAUTH_SECRET: ${LANGFUSE_SECRET}
      NEXTAUTH_URL: http://localhost:3001
      SALT: ${LANGFUSE_SALT}
    depends_on: [postgres]
    networks: [genai-net]

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - "./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro"
      - "prometheus_data:/prometheus"
    networks: [genai-net]

  grafana:
    image: grafana/grafana:latest
    ports: ["3002:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
      GF_AUTH_ANONYMOUS_ENABLED: "true"
      GF_AUTH_ANONYMOUS_ORG_ROLE: Viewer
    volumes:
      - "grafana_data:/var/lib/grafana"
      - "./infra/grafana/datasources:/etc/grafana/provisioning/datasources:ro"
      - "./infra/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro"
    depends_on: [prometheus]
    networks: [genai-net]

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports: ["16686:16686", "4317:4317", "4318:4318"]
    networks: [genai-net]

networks:
  genai-net:
    driver: bridge

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 6.2 Environment Variables (.env.example)
```bash
# OpenAI (credits)
OPENAI_API_KEY=sk-...

# Cohere (free reranking)
COHERE_API_KEY=...

# Free LLMs
GROQ_API_KEY=...
GOOGLE_API_KEY=...
GROK_API_KEY=...

# Database
POSTGRES_USER=genai_forge
POSTGRES_PASSWORD=changeme_local
DATABASE_URL=postgresql://genai_forge:changeme_local@postgres:5432/genai_forge

# Redis
REDIS_URL=redis://redis:6379/0

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# LangFuse
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_HOST=http://langfuse-server:3000
LANGFUSE_SECRET=changeme_local
LANGFUSE_SALT=changeme_local

# Grafana
GRAFANA_PASSWORD=admin

# App
SECRET_KEY=changeme_local
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 7. API Design Standards

### 7.1 All responses follow this envelope
```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_01j2abc",
    "model": "gpt-4o-mini",
    "latency_ms": 342,
    "tokens": { "input": 512, "output": 128 },
    "cost_usd": 0.000048,
    "cache": "MISS"
  }
}
```

### 7.2 SSE streaming format
Every streaming endpoint sends events in this format:
```
data: {"type": "chunk", "content": "The answer is...", "index": 0}

data: {"type": "source", "content": {"chunk": "...", "score": 0.91, "doc": "file.pdf", "page": 3}}

data: {"type": "meta", "content": {"model": "gpt-4o-mini", "tokens": 256, "latency_ms": 1200}}

data: {"type": "done"}
```

### 7.3 Error codes
| Code | HTTP | Meaning |
|---|---|---|
| `INVALID_REQUEST` | 400 | Bad input, see message |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `COLLECTION_NOT_FOUND` | 404 | Qdrant collection does not exist |
| `EMBEDDING_FAILED` | 502 | OpenAI embedding call failed |
| `LLM_TIMEOUT` | 504 | LLM call exceeded 30s timeout |
| `INTERNAL_ERROR` | 500 | Unexpected error, see request_id |

---

## 8. GitHub Actions CI/CD

### 8.1 ci.yml (runs on every PR)
```yaml
name: CI

on: [pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports: ["5432:5432"]
      redis:
        image: redis:7
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r backend/requirements.txt
      - run: ruff check backend/
      - run: black --check backend/
      - run: pytest backend/tests/ -v --cov=app --cov-report=term-missing
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY_TEST }}

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run build
```

### 8.2 deploy.yml (runs on merge to main)
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up --service backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

---

## 9. Cloud Migration Map

When each service is ready to move to cloud:

| Service | Local | Cloud | Migration Steps |
|---|---|---|---|
| FastAPI backend | Docker | Railway / Cloud Run | Change env vars, push Dockerfile |
| Frontend | Docker | Vercel | `vercel --prod` |
| PostgreSQL | Docker | Supabase | Export dump, import, update `DATABASE_URL` |
| Qdrant | Docker | Qdrant Cloud | Snapshot → restore to cloud, update `QDRANT_HOST` |
| Redis | Docker | Upstash | Update `REDIS_URL` to Upstash REST URL |
| LangFuse | Docker | LangFuse Cloud | Update `LANGFUSE_HOST` to `cloud.langfuse.com` |
| Prometheus | Docker | Grafana Cloud Agent | Update scrape target, push metrics via remote_write |
| Grafana | Docker | Grafana Cloud | Import dashboard JSONs, update datasource URLs |
| Celery workers | Docker | Cloud Run Jobs / Railway | Deploy worker Dockerfile as separate service |

Critical rule: **all service URLs are environment variables from day one.** No hardcoded `localhost:xxxx` anywhere in application code. This makes migration a config change, not a code change.

---

## 10. Build Plan — 4 Weeks

### Week 1: Foundation (Days 1–7)
**Goal:** Everything runs with `docker compose up`. Basic RAG endpoint works end-to-end.

- [ ] Initialize repo: monorepo structure, pyproject.toml, package.json, .pre-commit-config.yaml
- [ ] Write `docker-compose.yml` with all 10 services, health checks, named volumes
- [ ] FastAPI skeleton: main.py, config.py (Pydantic Settings), /health endpoint
- [ ] PostgreSQL: SQLAlchemy setup, Alembic migration for all tables
- [ ] Core clients: `embeddings.py` (OpenAI 3-large), `vector_store.py` (Qdrant), `cache.py` (Redis + GPTCache)
- [ ] Basic LangFuse setup: `tracing.py`, verify traces appear in LangFuse UI
- [ ] Prometheus: `metrics.py`, expose `/metrics`, verify Grafana can scrape
- [ ] RAG ingestion endpoint: upload → chunk → embed → Qdrant upsert
- [ ] RAG query endpoint: embed → Qdrant search → Cohere rerank → gpt-4o-mini → SSE stream
- [ ] Seed script: load 3 sample document sets into Qdrant
- [ ] GitHub Actions CI: lint + test on PR
- [ ] Deliverable: `POST /v1/rag/query` returns a streamed, grounded answer with source citations

### Week 2: Modules 1 & 2 (Days 8–14)
**Goal:** RAG Playground and Agent Board are fully functional.

- [ ] Semantic cache: GPTCache with cosine threshold 0.95, HIT/MISS headers
- [ ] Rate limiting middleware: token bucket per API key
- [ ] Multi-model support: add Groq, Gemini, Grok clients to `llm_clients.py`
- [ ] LangGraph: implement Research Agent state machine (plan → search → extract → synthesize)
- [ ] LangGraph: implement Code Review Agent with human-in-loop node
- [ ] CrewAI: Content Pipeline (Researcher → Writer → Editor)
- [ ] Celery: async job queue for agent runs, status polling
- [ ] SSE agent events: stream node_start/node_end/tool_call/done events
- [ ] Next.js: project init, layout, module navigation
- [ ] Frontend Module 1: chat window, document uploader, retrieval trace panel, RAG toggle
- [ ] Frontend Module 2: React Flow agent graph (nodes light up from SSE events), agent log panel, human-in-loop UI
- [ ] Deliverable: Full RAG playground + agent board running in browser

### Week 3: Modules 3 & 4 (Days 15–21)
**Goal:** Observability dashboard and API gateway are fully instrumented.

- [ ] Full LangFuse instrumentation: every LLM call in every module traced
- [ ] RAGAS eval pipeline: run test set, compute all 4 metrics, store in PostgreSQL
- [ ] Eval A/B comparison: two eval runs side by side
- [ ] Grafana dashboards: import `api_metrics.json` and `llm_metrics.json`, verify panels load
- [ ] OpenTelemetry: instrument FastAPI with OTLP exporter → Jaeger
- [ ] Request ID propagation: flow `X-Request-ID` through all services and logs
- [ ] Gateway stats endpoint: `/v1/gateway/stats` with live cache/rate limit data
- [ ] Frontend Module 3: eval runner UI, RAGAS score cards, Grafana iframe, LangFuse iframe
- [ ] Frontend Module 4: cache hit/miss stream visualizer, rate limit monitor, API key manager
- [ ] Structured error handling: all endpoints return error envelope with request_id
- [ ] Deliverable: Live Grafana showing real metrics from real app usage

### Week 4: Polish, Testing, Deploy (Days 22–30)
**Goal:** Deployed publicly, documented, demo-ready.

- [ ] Pytest: test all API endpoints with real Qdrant/Redis in CI (Docker services)
- [ ] Pytest: test RAG pipeline end-to-end (ingest → query → score)
- [ ] Pytest: test agent pipelines (mock LLM calls with fixtures)
- [ ] Frontend: Vitest unit tests for key components
- [ ] Write README.md: architecture diagram, quick start (`docker compose up`), module guide, cloud migration guide
- [ ] Record Loom demo: 5-min walkthrough of all 4 modules with live data
- [ ] Deploy backend to Railway (staging environment)
- [ ] Deploy frontend to Vercel
- [ ] Deploy LangFuse to LangFuse Cloud (free tier), update backend env
- [ ] Deploy Grafana to Grafana Cloud (free tier), import dashboards
- [ ] Seed production Qdrant Cloud with sample documents
- [ ] Final: smoke test all 4 modules in production, verify traces in LangFuse Cloud

---

## 11. Key Implementation Notes for the AI Agent

### Non-negotiable conventions
1. All service URLs come from environment variables. No `localhost:6333` in code.
2. Every async function that calls an LLM is wrapped with a LangFuse `@observe` decorator or manual span.
3. Every FastAPI route adds `X-Request-ID` to response headers. The ID is generated in middleware.
4. Pydantic v2 models for all request/response schemas. No raw `dict` returns from endpoints.
5. All Celery tasks are idempotent — can be safely retried on failure.
6. SSE endpoints must set `Content-Type: text/event-stream` and `Cache-Control: no-cache`.
7. Qdrant collection names use the format `{user_id}_{collection_name}_{timestamp}` to avoid collisions.
8. OpenAI calls go through a single `llm_clients.py` wrapper that adds retry logic (tenacity, max 3 retries with exponential backoff) and logs token usage.
9. `text-embedding-3-large` is the only embedding model. Do not add a fallback to a local model.
10. Cohere reranking is always called after Qdrant ANN search for all RAG queries. It is not optional.

### Latency targets (p95)
- `/v1/rag/query` (cache miss): < 4000ms end-to-end
- `/v1/rag/query` (cache hit): < 100ms
- `/v1/chat` (streaming first token): < 800ms
- `/v1/agents/run` (job queued): < 200ms (async, returns job_id immediately)
- `/health`: < 50ms

### Cost guardrails
- Add a `DRY_RUN=true` env var mode: returns mock responses, no OpenAI calls, for development
- Log estimated cost in USD on every request_log row
- Add a `/v1/admin/cost-summary` endpoint showing total spend by model and date
- Hard limit: if total daily spend exceeds $5, reject new requests with 429 and log an alert

---

## 12. Demo Script (for portfolio showcase)

When showing this to a recruiter or in an interview, walk through in this order:

1. **Start with observability** (Module 3) — show the live Grafana dashboard. Say: *"Before I show you any features, here's what's running in production right now."* This immediately signals production mindset.

2. **RAG Playground** (Module 1) — upload a PDF, run a query with RAG OFF, then RAG ON. Show the retrieval trace panel — point to the reranking scores. Say: *"The top chunk after reranking is different from the top chunk by vector similarity alone — that's Cohere's cross-encoder doing its job."*

3. **Agent Board** (Module 2) — run the Research Agent. Watch the graph light up node by node. Pause at the human-in-loop step, inject feedback, resume. Say: *"This is LangGraph — a state machine where I can inspect state at every node and inject human oversight."*

4. **Switch to LangFuse** — show the trace for the RAG query you just ran. Point to the per-step latency breakdown: embedding (Xms), Qdrant search (Xms), Cohere rerank (Xms), LLM (Xms). Say: *"Every LLM call in this system is traced. I can see exactly where latency comes from."*

5. **RAGAS eval** — run a quick eval on the uploaded collection. Show the faithfulness and context precision scores. Say: *"This is how I'd measure quality regression if I changed the chunking strategy or prompt template."*

6. **Close with architecture** — show the `docker-compose.yml` or the architecture diagram in the README. Say: *"The whole thing runs locally with one command. Each service has a defined cloud migration target — I've already mapped the env vars."*

---

*End of GenAI Forge App Plan — v1.0*
*Total estimated build time: 4 weeks with AI agent assistance*
*Estimated OpenAI credit spend during build: $15–30 (embeddings + evals + GPT-4o judge)*
*Estimated monthly cloud cost after deployment: $0 (all free tiers)*
