# Study Guide: Production Observability & Telemetry

This guide explains the concepts, tools, and implementation practices for setting up observability dashboards, distributed tracing, and LLM evaluations.

---

## 📖 Fundamentals

### What is Observability?
Observability measures how well a system's internal states can be inferred from its external outputs (metrics, traces, and logs).

### Why does it exist?
- **Speeds Up Debugging**: Pinpoints the source of errors in distributed microservice architectures.
- **Identifies Latency Bottlenecks**: Measures execution times for database queries, LLM calls, and network requests.
- **Controls API Costs**: Monitors token consumption and pricing metrics.

### Core Concepts
- **Metrics**: Numeric values aggregated over time (e.g., system CPU load, request count, p99 latency).
- **Traces**: Timelines showing the paths of requests as they travel through services.
- **Logs**: Text records detailing specific application events.

---

## ⚙️ Internal Working

### OpenTelemetry Distributed Tracing
OpenTelemetry uses context propagation to pass trace identifiers across service boundaries:
1. **Trace Header injection**: An incoming request generates a `traceparent` header (containing trace ID and span ID).
2. **HTTP Propagation**: The gateway propagates this header in outgoing requests.
3. **Trace Exporting**: Services format telemetry records and transmit them to a central collector (like Jaeger) using the OTLP protocol.

```
       [FastAPI Web Request] ──► (Generates Trace ID: 001)
                 │
                 ▼
         [Celery Task Run] ──► (Inherits Trace ID: 001)
                 │
                 ▼
         [OTLP Exporting] ───► [Jaeger Trace Store]
```

---

## 🛠️ Real Project Usage

### LangFuse LLM Tracing
- **Span Decorators**: Decorators (`@observe()`) track API calls to models like `gpt-4o-mini` and `llama3-70b`.
- **Attribute Logging**: Logs models used, prompt/completion tokens, latency, and estimated costs.
- **System Mapping**: Maps database calls (Postgres and Qdrant) alongside LLM operations to build a complete request timeline.

### Prometheus & Grafana Configuration
- **FastAPI Middleware**: Tracks request latencies and status codes, exposing them via a `/metrics` route.
- **Prometheus Collector**: Scrapes `/metrics` every 15 seconds to store time-series data.
- **Grafana Visualization**: Displays metrics on custom dashboards (System Health and AI Performance dashboards).

---

## 💻 Practical Development Knowledge

### Recommended Tools
- **Collector**: `OpenTelemetry Collector`.
- **Backend Trace Store**: `Jaeger` or `Zipkin`.
- **Metrics**: `Prometheus` and `Grafana`.
- **LLM Tracing**: `LangFuse` or `LangSmith`.

### Common Pitfalls
1. **High Telemetry Overhead**: Recording trace data synchronously can increase request latencies.
   * *Solution*: Export telemetry data asynchronously using background threads.
2. **Prometheus Cardinality Explosion**: Using high-cardinality labels (like user IDs or raw queries) degrades Prometheus performance.
   * *Solution*: Restrict metric labels to static values like HTTP routes and status codes.

---

## 🗺️ Learning Path

### 🟢 Beginner
- Learn to generate log files containing context metrics.
- Configure a local Prometheus container to scrape system metrics.

### 🟡 Intermediate
- Instrument APIs with OpenTelemetry to track request paths.
- Build a custom Grafana dashboard using Prometheus data.

### 🔴 Advanced
- Build context propagation layers to track traces across Celery workers.
- Run automated evaluations using RAGAS on evaluation datasets.
