# API Standards & Routing Protocols

This document defines response envelopes, real-time streaming protocols, error response standards, and endpoint routing rules.

---

## ✉️ Standard Response Envelope

All REST API responses return a structured JSON envelope containing execution metadata:

```json
{
  "data": {
    "result": "Response payload"
  },
  "meta": {
    "request_id": "req_01j2abc",
    "model": "gpt-4o-mini",
    "latency_ms": 342,
    "tokens": {
      "input": 512,
      "output": 128
    },
    "cost_usd": 0.000048,
    "cache": "MISS"
  }
}
```

---

## ⚡ Server-Sent Events (SSE) Stream Protocol

Streaming endpoints use Server-Sent Events (`text/event-stream`). Data packages are sent as JSON structures following these formats:

### Event Types & Schemas
- **`chunk`**: Partial text segments.
  `data: {"type": "chunk", "content": "The result is...", "index": 0}`
- **`source`**: Retrieval source citations.
  `data: {"type": "source", "content": {"chunk": "...", "score": 0.91, "doc": "file.pdf", "page": 3}}`
- **`meta`**: Latency and cost summaries.
  `data: {"type": "meta", "content": {"model": "gpt-4o-mini", "tokens": 256, "latency_ms": 1200}}`
- **`done`**: Stream completion signal.
  `data: {"type": "done"}`

---

## 🚨 Error Response Schema

Errors use standard JSON structures containing validation details and request correlation IDs:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Retry after 60 seconds.",
    "request_id": "req_01j2abc",
    "retry_after": 60
  }
}
```

### Standard Error Codes
- `INVALID_REQUEST` (400): Invalid request body structure.
- `UNAUTHORIZED` (401): Missing or invalid API key credentials.
- `COLLECTION_NOT_FOUND` (404): Specified collection not found in the database.
- `RATE_LIMIT_EXCEEDED` (429): Request volume limit exceeded.
- `INTERNAL_ERROR` (500): Unexpected system error.

---

## 🔌 API Endpoint Specifications

### 1. Document Ingestion (`POST /v1/rag/ingest`)
- **Method**: `POST`
- **Payload**: `multipart/form-data` containing files, collections, and partition settings.
- **Success Response**: Returns the count of chunks generated and estimated embedding costs.

### 2. Stream RAG Query (`POST /v1/rag/query`)
- **Method**: `POST`
- **Payload**: JSON parameters containing the query, target collection ID, and model name.
- **Success Response**: Streams Server-Sent Events containing text chunks and source citations.

### 3. Start Agent Job (`POST /v1/agents/run`)
- **Method**: `POST`
- **Payload**: JSON containing the agent pipeline name (`research`, `code_review`, or `content`) and prompt text.
- **Success Response**: Returns a background job ID.

### 4. Stream Agent Status (`GET /v1/agents/status/{job_id}`)
- **Method**: `GET`
- **Success Response**: Streams Server-Sent Events containing agent execution status, tool outputs, and LLM calls.

### 5. Resume Agent Job (`POST /v1/agents/resume/{job_id}`)
- **Method**: `POST`
- **Payload**: JSON containing human feedback or code updates.
- **Success Response**: Confirms that the job has resumed.
