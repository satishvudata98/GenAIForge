# Week 3: Full-Stack Observability & API Gateway

This week focuses on implementing monitoring systems, configuring distributed tracing, setting up Grafana dashboards, building the RAGAS evaluation pipeline, and creating the Observability and Gateway interfaces in the frontend.

---

## 🎯 Weekly Goals
- Instrument all LLM calls and retrieval steps with LangFuse tracing.
- Build Prometheus metrics and set up API and AI Grafana dashboards.
- Configure OpenTelemetry tracing in FastAPI to export spans to Jaeger.
- Build the async RAGAS evaluation runner and database schemas.
- Implement the Observability and API Gateway dashboards in the frontend.

---

## 📆 Day-by-Day Implementation Checklist

### Day 15: LangFuse Instrumentation
- [ ] Add LangFuse trace decorators (`@observe()`) to all LLM functions, agent graph nodes, and retrieval pipelines.
- [ ] Capture trace attributes (such as user IDs, models, prompt sizes, and estimated costs).
- [ ] Configure custom spans for Qdrant database searches and Cohere reranker operations.
- [ ] Verify that parent-child span hierarchies render correctly in the Langfuse UI.
- [ ] Add cost computation helper tools for OpenAI, Groq, and Gemini request models.

### Day 16: Prometheus Metrics Setup
- [ ] Declare custom metrics in `backend/app/observability/metrics.py` (e.g., request counters, model latency histograms, token volume counters).
- [ ] Build middleware to intercept API requests and record metrics (such as status code counters and execution times).
- [ ] Export metrics data via the `/metrics` endpoint.
- [ ] Set up scrape targets in `infra/prometheus/prometheus.yml` to collect data from the FastAPI container.
- [ ] Query Prometheus directly to verify that custom metrics are populated.

### Day 17: Grafana Dashboard Provisioning
- [ ] Configure automated Grafana data sources in `infra/grafana/datasources/` to connect to Prometheus.
- [ ] Create the System Health dashboard configuration file (`api_metrics.json`) tracking request volume and latency.
- [ ] Create the AI Quality dashboard configuration file (`llm_metrics.json`) tracking token volumes, costs, and cache hit rates.
- [ ] Import both dashboard files into Grafana during container setup.
- [ ] Test the dashboards to verify that metrics render correctly.

### Day 18: Distributed Tracing with OpenTelemetry
- [ ] Instrument the FastAPI application with OpenTelemetry middleware.
- [ ] Configure the OTLP exporter to send trace data to the Jaeger container.
- [ ] Add tracing hooks to Redis connection wrappers and Celery task execution loops.
- [ ] Propagate the request correlation ID (`X-Request-ID`) to Jaeger spans.
- [ ] Run test requests and verify that distributed spans resolve successfully in Jaeger.

### Day 19: RAGAS Evaluation Pipeline
- [ ] Build the RAGAS evaluation pipeline inside `backend/app/rag/evaluation.py`.
- [ ] Implement the evaluation executor to calculate faithfulness, answer relevance, context precision, and context recall using `gpt-4o` as a judge.
- [ ] Build the API endpoints `POST /v1/eval/run` and `GET /v1/eval/results`.
- [ ] Write DB logs to PostgreSQL to save evaluation run summaries and detailed scorecards.
- [ ] Verify that evaluation metrics calculate and save correctly using a test dataset.

### Day 20: Observability Dashboard UI
- [ ] Build the Observability Dashboard UI (`/observability`).
- [ ] Integrate Grafana dashboards directly into the UI using secure iframe embeds.
- [ ] Integrate LangFuse dashboards using iframe embeds to view live execution traces.
- [ ] Build the RAGAS evaluation runner interface, featuring CSV file uploaders for evaluation datasets.
- [ ] Build comparison cards to display evaluation runs side-by-side.

### Day 21: API Gateway Control UI
- [ ] Build the API Gateway interface page (`/gateway`).
- [ ] Create charts to display live cache hit/miss statistics.
- [ ] Implement rate-limit status trackers showing usage details.
- [ ] Build the API Key Management interface to generate, view, and revoke API keys.
- [ ] Verify that gateway statistics update dynamically based on API usage.

---

## 🛠️ Code Architecture & Design Goals
- Ensure all observability metrics and traces share the same `X-Request-ID` correlation identifier.
- Store database passwords and API tokens securely in the backend, exposing only metadata to the frontend.
- Optimize Prometheus scrape intervals to balance data resolution and container resource usage.

---

## 🔍 Refactoring Checkpoints
- **Metrics Registration**: Verify that Prometheus metrics are registered only once during application startup.
- **Trace Context Propagation**: Verify that trace contexts are preserved across async thread boundaries in Celery.

---

## 🧪 Testing & Debugging Tasks
- Verify that request latencies are logged accurately in Prometheus histograms.
- Validate that the RAGAS evaluation pipeline processes large test sets without exceeding API rate limits.
- Confirm that Jaeger maps distributed spans correctly across FastAPI and Celery.
*   
