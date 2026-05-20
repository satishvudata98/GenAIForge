# GenAI Forge

Week 1 delivers the local platform foundation for GenAI Forge:

- FastAPI backend with health, readiness, metrics, RAG ingest, and RAG query routes
- PostgreSQL metadata storage, Qdrant vector storage, and Redis cache/broker plumbing
- Docker Compose local stack with frontend, backend, worker, Nginx, Prometheus, Grafana, and Jaeger
- Seed script and focused backend regression tests
- GitHub Actions backend CI workflow

This README only covers how to run and test the Week 1 implementation.

## Week 1 Features

- `GET /v1/health`
- `GET /v1/readiness`
- `POST /v1/rag/ingest`
- `POST /v1/rag/query` with Server-Sent Events
- `GET /metrics`

## Prerequisites

- Docker and Docker Compose v2
- Python 3.12
- Node.js 20+ if you want to run the frontend outside Docker
- API keys for real end-to-end testing:
	- `OPENAI_API_KEY` for embeddings and streamed generation
	- `COHERE_API_KEY` for reranking in the query path
	- `LANGFUSE_*` keys are optional if you want tracing

## Configuration

1. Copy the root env template and fill in your real API keys.

```bash
cp .env.example .env
```

2. Set at least these values in `.env`:

```env
OPENAI_API_KEY=your_openai_key
COHERE_API_KEY=your_cohere_key
LANGFUSE_HOST=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_DISABLED=false
```

Notes:

- The root `.env` is used by Docker Compose and therefore uses container hostnames like `postgres`, `redis`, and `qdrant`.
- `backend/.env` is reserved for host-side Python runs and uses `localhost` service addresses.
- Nginx publishes on `http://localhost:8080` by default to avoid port `80` conflicts.

## Run the Full Week 1 Stack

From the repository root:

```bash
cd infra
docker compose up -d --build
docker compose ps
```

Expected local endpoints:

- Frontend: `http://localhost:3000`
- Nginx proxy: `http://localhost:8080`
- FastAPI direct: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
- Jaeger: `http://localhost:16686`
- Qdrant dashboard: `http://localhost:6333/dashboard`

Optional LangFuse self-hosted profile:

```bash
cd infra
docker compose --profile observability up -d langfuse-server
```

## Quick Smoke Tests

Health through Nginx:

```bash
curl -sS http://localhost:8080/v1/health
```

Readiness direct to backend:

```bash
curl -sS http://localhost:8000/v1/readiness
```

Metrics:

```bash
curl -sS http://localhost:8000/metrics | head
```

## Seed Sample Documents

The repository includes sample docs under `scripts/sample_docs/`.

Run the seed script from the repository root:

```bash
cd backend
. .venv/bin/activate
cd ..
python scripts/seed_qdrant.py
```

Custom collection example:

```bash
python scripts/seed_qdrant.py --collection-name my-test-kb
```

The script prints a JSON response containing:

- `collection_id`
- `collection_name`
- `qdrant_collection_name`
- `documents_ingested`
- `chunks_indexed`

## Manual API Testing

### 1. Ingest a File

```bash
curl -X POST http://localhost:8080/v1/rag/ingest \
	-F "collection_name=knowledge-base" \
	-F "chunk_size=512" \
	-F "chunk_overlap=64" \
	-F "files=@scripts/sample_docs/platform_overview.md"
```

Save the returned `collection_id`.

### 2. Query with SSE

```bash
curl -N -X POST http://localhost:8080/v1/rag/query \
	-H "Content-Type: application/json" \
	-d '{
		"query": "What is GenAI Forge?",
		"collection_id": "PASTE_COLLECTION_ID_HERE",
		"model": "gpt-4o-mini",
		"top_k": 5,
		"use_reranker": true
	}'
```

Expected SSE event order:

- `chunk`
- `source`
- `meta`
- `done`

## Run Backend Tests

From the backend directory:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest tests/test_health.py tests/test_core.py tests/test_ingest.py tests/test_query.py
```

If your `.venv` already exists, only run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_health.py tests/test_core.py tests/test_ingest.py tests/test_query.py
```

## Run Lint Checks

```bash
cd backend
. .venv/bin/activate
ruff check .
```

## Frontend Local Run Without Docker

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`.

## Current Week 1 Scope Status

Completed:

- Local stack orchestration
- Backend foundation and database migration
- AI wrappers and tracing hooks
- RAG ingestion and query APIs
- Seed tooling
- Focused backend tests and CI workflow

Known runtime constraints:

- Real ingest/query execution requires valid OpenAI credentials.
- Query reranking requires a valid Cohere key.
- LangFuse Cloud verification is supported; self-hosted LangFuse remains optional.

## Useful Commands

Stop the stack:

```bash
cd infra
docker compose down
```

Stop and remove volumes:

```bash
cd infra
docker compose down -v
```

Check compose status:

```bash
cd infra
docker compose ps
```
