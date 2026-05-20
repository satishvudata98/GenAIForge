# Study Guide: Semantic Caching

This guide explains the design, mathematics, and implementation of semantic caching systems for Large Language Model queries.

---

## 📖 Fundamentals

### What is Semantic Caching?
Semantic caching stores and retrieves LLM responses by comparing the semantic meaning of queries, rather than requiring exact string matches.

### Why does it exist?
- **Reduces Latency**: Serving cached responses takes under 100ms, bypassing slow LLM API calls.
- **Minimizes Costs**: Avoids generating duplicate responses, reducing LLM API token charges.
- **Improves Reliability**: Serves cached responses even if upstream AI providers experience outages.

### Core Concepts
- **Similarity Threshold**: The minimum similarity score (e.g., $\ge 0.95$ Cosine Similarity) required to trigger a cache hit.
- **Embedding Lookup**: Converting query strings to vectors and searching the cache database for matches.
- **Cache Eviction**: Removing old or low-frequency cache entries when storage limits are reached.

---

## ⚙️ Internal Working

### Semantic Query Matching
1. **Query Embedding**: The incoming query is converted to a vector.
2. **Similarity Query**: The system queries the cache database to find vectors close to the query vector.
3. **Threshold Check**: If the highest similarity score meets the threshold, the cached response is returned. Otherwise, the request is sent to the LLM.

```
       [User Query] ──► (Generate Vector)
                             │
                             ▼
         [Vector DB Search] ──► (Find matches in Cache)
                                      │
                         ┌────────────┴────────────┐
                         ▼ (Similarity >= 0.95)   ▼ (Similarity < 0.95)
                    [Cache Hit]               [Cache Miss]
               (Return response, 100ms)    (Call LLM & save result)
```

---

## 🛠️ Real Project Usage

### GPTCache + Redis Configuration
- **Embedding Model**: `text-embedding-3-large` (3072 dimensions) is used for consistency.
- **Vector Search Engine**: An in-memory search database is used to check vector similarity.
- **Data Store**: Redis stores the query strings, embedding vectors, and LLM text responses.
- **Eviction Configuration**: Configured with a Least Recently Used (LRU) policy and a 1-hour TTL.

---

## 💻 Practical Development Knowledge

### Recommended Libraries
- **Caching Framework**: `GPTCache` (Python caching framework for LLMs).
- **Data Store**: `redis-py` (Python Redis client).
- **Embeddings**: `openai` (OpenAI Python SDK).

### Common Pitfalls
1. **False Positives**: Serving cached answers for queries that look similar but have different meanings (e.g., "How do I start the server?" vs. "How do I stop the server?").
   * *Solution*: Set a high similarity threshold (e.g., $\ge 0.96$ Cosine Similarity) and test with sample queries.
2. **Stale Cache Entries**: Returning out-of-date answers after documentation changes.
   * *Solution*: Invalidate the cache when documents are updated or re-ingested.

---

## 🗺️ Learning Path

### 🟢 Beginner
- Implement a simple exact-match cache using an in-memory key-value store.
- Measure latency differences between cache hits and cache misses.

### 🟡 Intermediate
- Integrate a local Redis container as an API cache store.
- Build a semantic cache using Python and an in-memory vector database.

### 🔴 Advanced
- Build cache invalidation triggers that run when database collections change.
- Benchmark cache performance under heavy, concurrent query loads.
