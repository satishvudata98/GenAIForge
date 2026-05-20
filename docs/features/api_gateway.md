# Feature Specification: API Gateway

This document provides a technical overview and architectural design for the API Gateway features, covering security controls, rate limiting, and response caching.

---

## 📖 Feature Overview

### Description
The API Gateway acts as the entry point for the application. It manages incoming traffic, enforces rate limits, manages semantic caches to optimize response times, and standardizes error responses.

### Gateway Features
1. **Semantic Cache**: Uses `GPTCache` and Redis to cache and serve responses for semantically equivalent queries (e.g., matching queries with $\ge 0.95$ cosine similarity).
2. **Rate Limiting**: Implements a token bucket algorithm to enforce request limits per API key.
3. **Structured Errors**: Returns standardized error envelopes containing unique request identifiers.

---

## ⚙️ Technical Breakdown

### Inbound Request lifecycle

```
[Inbound Request]
       │
       ▼ (Verify API Key & Request ID middleware)
 [Rate Limiter] ──► (Limit Exceeded) ──► [429 Rate Limit Error]
       │
       ▼ (Check Semantic Cache)
   [Redis] ─────► (Cache Hit) ─────────► [Return Cache Response (100ms)]
       │
       ▼ (Cache Miss)
 [Execute API]
       │
       ▼
 [Save Response to Cache & Return]
```

### Rate Limiting (Token Bucket)
Rate limits are enforced on a per-API-key basis:
- **`v1/chat`**: 20 requests/minute (burst cap: 100 requests/hour).
- **`v1/rag/query`**: 30 requests/minute (burst cap: 200 requests/hour).

The rate limiter returns the following response headers:
- `X-RateLimit-Limit`: Maximum requests allowed in the current window.
- `X-RateLimit-Remaining`: Remaining requests allowed in the current window.
- `X-RateLimit-Reset`: Unix timestamp indicating when the limits reset.

---

## 🧠 Engineering Concepts Behind It

### Token Bucket Algorithm
- **What it is**: An algorithm used to control data transmission rates, allowing for temporary bursts while enforcing long-term average rate limits.
- **Why it is used**: It allows users to make rapid, consecutive requests (bursts) while preventing sustained high volume from overloading the system.
- **How it works**: A virtual bucket holds "tokens" up to a maximum capacity. Tokens are added to the bucket at a constant rate over time. Each incoming request consumes one token. If the bucket is empty, requests are rejected until new tokens accumulate.

```
Token replenishment (+R tokens/sec) ──►  ┌──────────────┐
                                         │ ░░░░░░░░░░░░ │  ◄── Max capacity (B tokens)
                                         └──────┬───────┘
                                                │
Inbound Request ────────────────────────────────┴──► (Token Available?) ──► Run API
                                                               │
                                                               └── (No Tokens)  ──► 429 Error
```

### Semantic Caching
- **What it is**: Caching LLM responses based on the semantic meaning of queries rather than exact string matches.
- **Why it is used**: LLM API calls are slow and expensive. Caching responses for semantically equivalent questions reduces costs and response times.
- **How it works**: When a query is received, its embedding vector is generated. The system calculates the cosine similarity between the query vector and cached query vectors. If the similarity meets the threshold ($\ge 0.95$), the cached response is returned.

### Similarity Metrics: Cosine Similarity
- **What it is**: A metric that measures the cosine of the angle between two multi-dimensional vectors, indicating how similar the vectors are in direction.
- **Why it is used**: Cosine similarity evaluates text similarity based on semantic content rather than document length.
- **How it works**: The similarity score ranges from -1 to 1:
  $$\text{Cosine Similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$
  A score close to `1.0` indicates that the queries share similar semantic meanings.

---

## 🛠️ Best Practices & Performance Optimization
- **Enforce Cache TTL**: Set an expiration time (Time-To-Live) on cache keys (e.g., 1 hour) to ensure that the system occasionally retrieves fresh data.
- **Set Up Graceful Fallbacks**: If the Redis cache fails, bypass the cache layer and route requests directly to the API handler to prevent service outages.
- **Optimize Vector Indexing**: Index cache vectors in an in-memory vector database (e.g., FAISS or Qdrant) to ensure fast similarity searches.
