# Study Guide: Advanced API Engineering

This guide explains the design, security, and implementation of production-grade API gateways, rate limiting algorithms, and real-time streaming protocols.

---

## 📖 Fundamentals

### What is API Gateway Engineering?
API gateway engineering involves managing, securing, and optimizing entry points for web applications.

### Why does it exist?
- **Enforces Security**: Restricts access using API key verification.
- **Protects Resources**: Prevents API abuse using rate limiting algorithms.
- **Enables Real-Time Streams**: Streams server data to clients using Server-Sent Events (SSE).

### Core Concepts
- **Rate Limiting**: Restricting the number of API requests users can make in a given timeframe.
- **Correlation ID**: A unique identifier assigned to each request to track it across services.
- **Server-Sent Events (SSE)**: A one-way streaming protocol that sends real-time updates over persistent HTTP connections.

---

## ⚙️ Internal Working

### Token Bucket Rate Limiting
The Token Bucket algorithm manages request rates:
- A bucket holds up to a maximum number of tokens ($B$).
- Tokens are added to the bucket at a constant fill rate ($R$ tokens/second).
- Each incoming request consumes one token. If no tokens are available, the request is rejected with a `429 Too Many Requests` error.

$$\text{Available Tokens} = \min(B, \text{Current Tokens} + (t_{\text{now}} - t_{\text{last}}) \times R)$$

```
     Token replenishment (+R tokens/sec) ──►  ┌──────────────┐
                                              │ ░░░░░░░░░░░░ │  ◄── Bucket capacity (B)
                                              └──────┬───────┘
                                                     │
     API Request ────────────────────────────────────┴──► (Token Available?) ──► Run API
                                                                    │
                                                                    └── (Empty) ──► 429 Error
```

### Server-Sent Events (SSE)
Unlike WebSockets, which are bidirectional, Server-Sent Events (SSE) provide a lightweight, one-way text stream over standard HTTP connections:
1. **Persistent Connection**: The client initiates a connection using `EventSource`.
2. **Text Streaming**: The server keeps the connection open and streams text chunks using the `text/event-stream` content type.
3. **Data Framing**: Events are formatted as plain text blocks separated by double newlines.

---

## 🛠️ Real Project Usage

### Token Bucket Middleware
- FastAPI middleware intercepts incoming requests and verifies API keys.
- It uses Redis to track token counts and timestamps, and returns rate limit headers (`X-RateLimit-Remaining`).

### Chat SSE Endpoint
- The `/v1/chat` and `/v1/rag/query` routes return `StreamingResponse` objects.
- Response payloads use standardized events:
  - `chunk`: Contains generated response text.
  - `source`: Lists document source references.
  - `done`: Signals stream completion.

---

## 💻 Practical Development Knowledge

### Recommended Libraries
- **Rate Limiting**: `redis-py` (Python Redis integration).
- **Streaming UI**: Native browser `EventSource` APIs.
- **Testing**: `httpx` (asynchronous HTTP testing library for Python).

### Common Pitfalls
1. **Response Buffering**: Proxies like Nginx may buffer streaming responses, holding data until the stream finishes.
   * *Solution*: Add the `X-Accel-Buffering: no` header to streaming responses to disable proxy buffering.
2. **Connection Leaks**: Keeping connections open indefinitely can exhaust server ports.
   * *Solution*: Configure client timeouts and close inactive streams.

---

## 🗺️ Learning Path

### 🟢 Beginner
- Learn to build basic REST endpoints in FastAPI.
- Implement API key verification using query parameters.

### 🟡 Intermediate
- Build a rate limiter using Redis and the token bucket algorithm.
- Create a basic streaming endpoint that outputs text updates.

### 🔴 Advanced
- Build distributed tracing pipelines that propagate correlation IDs across microservices.
- Optimize Nginx reverse proxies to handle thousands of concurrent streaming connections.
