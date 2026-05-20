# Phase 3: Production Observability & RAGAS Eval

This phase instruments the application with production-grade monitoring systems. It implements distributed tracing, system health and cost monitoring, and automated evaluations for RAG output quality.

---

## 🎯 Phase Goals
- Integrate LangFuse tracing across all LLM operations to track parameters, latency, token consumption, and API costs.
- Set up Prometheus to collect system, RAG-specific, and agent metrics, and build Grafana dashboards to visualize them.
- Implement OpenTelemetry middleware inside FastAPI to export distributed traces to Jaeger.
- Propagate a standard correlation identifier (`X-Request-ID`) across all request paths.
- Build the RAGAS evaluation pipeline to score LLM outputs based on faithfulness, precision, and recall.
- Deliver the Observability Dashboard UI to display performance metrics, trace timelines, and evaluation scorecards.

---

## 🛠️ Features Covered
1. **End-to-End Tracing (LangFuse)**: Custom tracing spans that capture context, latency, and costs for all retrieval and generation steps.
2. **FastAPI Telemetry (OpenTelemetry)**: API request tracing that exports span data to Jaeger.
3. **Prometheus Metrics Engine**: Custom metrics tracking API performance, RAG metrics, and worker execution rates.
4. **Grafana Visualization**:
   - *API & System Dashboard*: Monitoring latency, cache hit rates, and database connections.
   - *AI Quality Dashboard*: Visualizing token costs and LLM performance.
5. **RAGAS Evaluator**: Background testing pipelines that measure the quality of RAG generations against ground-truth datasets.
6. **API Gateway Monitoring**: Next.js panels visualizing live cache hit/miss statuses and active rate limits.

---

## 🗂️ Technical Modules Involved

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── eval.py                 # Endpoint to execute RAGAS evaluations and fetch run history
│   │   └── gateway.py              # Endpoint for API key metrics and gateway status logs
│   ├── core/
│   │   └── tracing.py              # OpenTelemetry exporter configurations
│   ├── rag/
│   │   └── evaluation.py           # RAGAS metric scoring implementation
│   └── observability/
│       ├── metrics.py              # Prometheus registry declarations
│       ├── middleware.py           # Latency logs and Request-ID propagation
│       └── langfuse_hooks.py       # Langfuse callback wrappers
frontend/
├── app/
│   ├── observability/page.tsx     # Dashboard displaying RAGAS and Grafana details
│   └── gateway/page.tsx            # API Gateway control center
└── components/
    ├── observability/
    │   ├── TraceViewer.tsx         # Embed panel for LangFuse
    │   ├── MetricsPanel.tsx        # Charts for system requests and latencies
    │   └── EvalScoreCard.tsx       # Comparison UI for RAGAS metrics
    └── gateway/
        ├── CacheIndicator.tsx      # Hit/Miss indicator
        └── LatencyBadge.tsx        # Latency metric badge
```

---

## 🌐 Backend, Frontend, and AI Integrations
- **Prometheus Scrape Path**: FastAPI exposes a `/metrics` route. The Prometheus service queries this endpoint at regular intervals and forwards data to Grafana.
- **OTEL-to-Jaeger Export**: FastAPI routes generate span data that is exported asynchronously via the OTLP protocol to Jaeger.
- **RAGAS Evaluations**: The evaluation pipeline uses `gpt-4o` as a judge to assess faithfulness, context precision, and context recall, storing the scores in PostgreSQL.

---

## 🗄️ Database Changes (PostgreSQL Schema)
The database structure is updated to support evaluation tracking:
- **`eval_runs`**: Stores aggregated RAGAS metric scores, target collection IDs, test sizes, and token costs.
- **`eval_questions`**: Stores question-by-question metrics, generated text outputs, retrieved contexts, and ground-truth values.

---

## 🔌 APIs & Services Required

### Run RAGAS Evaluation
* **URI**: `POST /v1/eval/run`
* **Content-Type**: `application/json`
* **Payload**:
  ```json
  {
    "collection_id": "UUID",
    "test_set": [
      {
        "question": "Sample Question",
        "ground_truth": "Expected Answer"
      }
    ],
    "judge_model": "gpt-4o"
  }
  ```
* **Returns**: Task ID for the background evaluation job.

### Retrieve Evaluation Results
* **URI**: `GET /v1/eval/results`
* **Returns**: List of all evaluation runs with aggregated metric scores.

### Compare Evaluation Runs
* **URI**: `GET /v1/eval/compare?run_a={uuid}&run_b={uuid}`
* **Returns**: Side-by-side comparison data for prompt testing.

---

## 📊 Estimated Complexity & Risks

### Estimated Complexity: High
- Configuring OpenTelemetry span propagation across processes (FastAPI, Redis, Celery) requires correct header formatting.
- Managing API costs for `gpt-4o` during high-volume RAGAS evaluations requires careful optimization of request volumes.

### Key Risks & Mitigation
1. **High Evaluation Costs**: Using `gpt-4o` as a judge for large test suites can quickly deplete budgets.
   * *Mitigation*: Limit test suites to 20 representative questions per evaluation, and run jobs asynchronously via Celery.
2. **Prometheus Cardinality Explosion**: Storing raw query strings or user IDs in metric labels can degrade Prometheus performance.
   * *Mitigation*: Restrict metric labels to low-cardinality keys (e.g., HTTP method, status codes, model names).

---

## 🧪 Testing Requirements
- **Observability Verification**: Verify that HTTP requests contain correct `X-Request-ID` headers in responses.
- **Metrics Verification**: Query `/metrics` to ensure custom counters (e.g., RAG queries, cache hits) increment correctly.
- **Evaluation Verification**: Run the evaluation task with mock LLM outputs to verify that Postgres tables are populated correctly.
