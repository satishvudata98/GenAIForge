# Feature Specification: Observability & Evaluation

This document provides a technical overview and architectural design for the Observability and Evaluation features, which implement system logging, distributed tracing, and automated quality metrics.

---

## 📖 Feature Overview

### Description
The Observability and Evaluation system enables tracking and analysis of all LLM operations. It records metrics (e.g., token usage, latencies, API costs) and runs automated evaluation suites using RAGAS to assess generation quality.

### User Flow
1. The developer opens `/observability` to view system metrics and tracing logs.
2. They select a document collection, upload a test dataset containing reference questions and ground-truth answers, and click "Run Evaluation".
3. An evaluation job runs in the background. Once complete, a scorecard displays scores for faithfulness, answer relevance, context precision, and context recall.
4. The user can view latency metrics and trace timelines for individual queries directly in the UI.

---

## ⚙️ Technical Breakdown

### Telemetry Pipeline & Components

```
[FastAPI Request Router]
       │
       ├─► (Metrics API) ─────────────► [Prometheus Registry] ──► [Grafana Dashboards]
       │
       ├─► (Distributed Tracing) ─────► [Jaeger collector]
       │
       └─► (LLM SDK Calls) ───────────► [LangFuse Tracing Server]
```

### RAGAS Metric Calculation
During an evaluation run, the system evaluates the generated answers using `gpt-4o` as a judge against the following metrics:
1. **Faithfulness**: Verifies that the generated answer relies only on the retrieved context chunks.
   $$\text{Faithfulness} = \frac{\text{Number of statements in answer supported by context}}{\text{Total statements in generated answer}}$$
2. **Answer Relevance**: Evaluates whether the generated answer directly addresses the user's question.
3. **Context Precision**: Measures if the most relevant retrieved context chunks are positioned at the top of the search results.
4. **Context Recall**: Verifies that all information required to answer the question is present in the retrieved context chunks.

---

## 🧠 Engineering Concepts Behind It

### Telemetry Data Types: Metrics, Traces, and Logs
- **Metrics**: Quantitative measurements aggregated over time (e.g., CPU load, request latency). They are stored as time-series data and used to trigger alerts.
- **Traces**: End-to-end paths of requests as they flow through distributed systems. They identify performance bottlenecks across service boundaries.
- **Logs**: Discrete event text records containing timestamps and execution details, useful for debugging specific errors.

### Distributed Tracing Context Propagation
- **What it is**: Passing unique request correlation identifiers across network boundaries (e.g., HTTP requests, database queries, message queues) to map the entire lifecycle of a request.
- **Why it is used**: In microservice architectures, requests pass through multiple containers. Correlation IDs unify these logs into a single, chronological timeline.
- **How it works**: An initial request generates a `X-Request-ID` and parent span ID. Middleware injects these headers into outgoing requests, allowing downstream services (like Celery workers) to extract and register them as child spans.

```
FastAPI Router (Root Span: 01A)
  └── Trace Middleware (Injects X-Request-ID: req_abc)
        ├── Qdrant Query (Span: 01A-1)
        ├── Cohere Rerank (Span: 01A-2)
        └── Celery Agent Run (Span: 01A-3, inherits context req_abc)
              └── Wikipedia Tool (Span: 01A-3-a)
```

### LLM Judge Evaluations
- **What it is**: Using high-reasoning models (like `gpt-4o`) to evaluate text outputs based on structured criteria, replacing manual validation.
- **Why it is used**: Rule-based testing (e.g., string matching) is insufficient for evaluating natural language generation quality.
- **How it works**: The judge model is prompted with evaluation criteria, the source context, and the generated text. It outputs analysis logs and a numerical score using structured JSON formats.

---

## 🛠️ Best Practices & Performance Optimization
- **Minimize Trace Latency**: Use non-blocking, asynchronous background threads to export trace data, preventing telemetry logging from slowing down user requests.
- **Manage Evaluation Costs**: Limit evaluation test suites to key representative questions, and run evaluation jobs during off-peak hours using Celery queues.
- **Clean Up Cache**: Invalidate semantic caches during evaluations to ensure that the RAG pipeline retrieves and generates fresh content.
