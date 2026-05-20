# Database & Vector Store Schema Design

This document details the PostgreSQL relational schemas, Qdrant vector database collection specifications, and Redis key designs.

---

## 🗄️ PostgreSQL Relational Database Schema

PostgreSQL stores relational metadata, user settings, request logs, and evaluation scorecards.

```
  ┌──────────────┐          ┌─────────────────────┐
  │    users     │ ◄──────  │   rag_collections   │
  └──────┬───────┘          └──────────┬──────────┘
         │                             │
         │                             ▼
         │                  ┌─────────────────────┐
         │ ◄──────────────  │     eval_runs       │
         │                  └──────────┬──────────┘
         │                             │
         │                             ▼
         │                  ┌─────────────────────┐
         │ ◄──────────────  │   eval_questions    │
         │                  └─────────────────────┘
         ▼
  ┌──────────────┐          ┌─────────────────────┐
  │ request_log  │          │     agent_runs      │
  └──────────────┘          └─────────────────────┘
```

### Table DDL Definitions

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
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
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
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
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
  pipeline TEXT NOT NULL,   -- research | code_review | content
  status TEXT NOT NULL,     -- queued | running | paused | done | error
  input TEXT NOT NULL,
  output TEXT,
  total_tokens INT,
  total_cost_usd NUMERIC(10,6),
  duration_ms INT,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Eval runs (RAGAS)
CREATE TABLE eval_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  collection_id UUID REFERENCES rag_collections(id) ON DELETE CASCADE,
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
  eval_run_id UUID REFERENCES eval_runs(id) ON DELETE CASCADE,
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

## 🔎 Qdrant Vector Database Collections

Qdrant stores document embedding vectors and their associated metadata.

### Vector Configuration
- **Embedding Model**: `text-embedding-3-large`.
- **Dimensions**: 3072.
- **Distance Metric**: Cosine Similarity.
- **Indexing Graph**: Hierarchical Navigable Small World (HNSW).

### Payload Properties
Every vector entry includes metadata inside its payload:
```json
{
  "document_id": "UUID",
  "collection_id": "UUID",
  "text": "Chunk text content...",
  "page_number": 3,
  "source_file": "file.pdf"
}
```

---

## ⚡ Redis Key Schemas

Redis acts as the cache layer and Celery message broker.

### Key Types & Formats
1. **Semantic Cache Lookup**:
   - *Key*: `semantic_cache:{collection_id}:{vector_hash}`
   - *Value*: Standard JSON payload storing the cached answer.
   - *TTL*: 3600 seconds (1 hour).
2. **Rate Limit Buckets**:
   - *Key*: `rate_limit:{api_key}:{endpoint_path}`
   - *Value*: Token bucket count and timestamp.
3. **Agent State Checkpoints**:
   - *Key*: `agent_checkpoint:{job_id}`
   - *Value*: Serialized state data for the active run.
