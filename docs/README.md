# GenAI Forge — Technical Documentation & Planning System

Welcome to the **GenAI Forge** development planning and learning hub. This documentation is structured to provide a dual purpose: a high-fidelity execution roadmap for implementing a production-grade GenAI engineer portfolio, and a deep-dive study guide covering the modern AI engineering stack.

---

## 🗺️ Documentation Map

> [!TIP]
> Use the **[Project Progress Checklist (todo.md)](file:///E:/GenAIForge/todo.md)** in the repository root to track your progress and check off completed items as you build the application.

### 1. 🚀 Phase-wise Development Planning
A macro view of the project divided into four logical milestones. Each document outlines goals, features, dependencies, backend/frontend integration details, complexity, risks, and testing metrics.
* **[Phase 1: Foundation & Baseline RAG](file:///E:/GenAIForge/docs/phases/phase_1_foundation.md)** — Docker composition, database schemas, and baseline async streaming RAG endpoints.
* **[Phase 2: Core Playground & Agent Board](file:///E:/GenAIForge/docs/phases/phase_2_core_modules.md)** — Frontend chat layout, React Flow agent graphs, LangGraph state machines, and CrewAI pipelines.
* **[Phase 3: Production Observability & RAGAS Eval](file:///E:/GenAIForge/docs/phases/phase_3_observability.md)** — LangFuse integration, custom Prometheus metrics, Grafana dashboards, and automated RAGAS eval.
* **[Phase 4: Optimization, Tests & Deploys](file:///E:/GenAIForge/docs/phases/phase_4_polish_deploy.md)** — Unit/integration tests (Pytest/Vitest), CI/CD pipelines, and cloud migrations.

### 2. 📅 Week-wise Execution Planning
Granular, day-by-day developer checklists for building the system step-by-step.
* **[Week 1: Local Stack Setup & Streaming RAG](file:///E:/GenAIForge/docs/weekly-plans/week_1.md)** — Environment bootstrap, database setup, basic ingestion, and SSE RAG query.
* **[Week 2: Frontend Modules & Multi-Agent Engines](file:///E:/GenAIForge/docs/weekly-plans/week_2.md)** — Multi-model support, LangGraph research/review pipelines, Celery jobs, and React Flow visualizers.
* **[Week 3: Full-Stack Observability & API Gateway](file:///E:/GenAIForge/docs/weekly-plans/week_3.md)** — Tracing hooks, Prometheus middleware, RAGAS execution pipelines, and token-bucket rate limits.
* **[Week 4: Quality Verification & Cloud Deployment](file:///E:/GenAIForge/docs/weekly-plans/week_4.md)** — Automated test suites, pre-commit optimization, Vercel/Railway deployments, and production smoke tests.

### 3. 🔩 Feature Specifications
Deep-dive technical breakdown of each distinct application module.
* **[RAG Playground Spec](file:///E:/GenAIForge/docs/features/rag_playground.md)** — File parsing, chunking math, Qdrant vectors, Cohere cross-encoders, and SSE streams.
* **[Multi-Agent Board Spec](file:///E:/GenAIForge/docs/features/multi_agent_board.md)** — Stateful graph nodes, human-in-the-loop socket pauses, and dynamic CrewAI sequences.
* **[Observability & Eval Spec](file:///E:/GenAIForge/docs/features/observability_eval.md)** — OpenTelemetry exporters, Prometheus gauges, Grafana panel bindings, and RAGAS metrics.
* **[API Gateway Spec](file:///E:/GenAIForge/docs/features/api_gateway.md)** — Token bucket algorithm, semantic cache (cosine similarity thresholding), and request ID propagation.

### 4. 📚 Developer Learning & Study Guides
Theory-meets-practice manuals that explain the underlying concepts, inner workings, and best practices for every component.
* **[RAG, Embeddings & Vectors](file:///E:/GenAIForge/docs/study-guides/rag_and_vectors.md)** — Core embeddings theory, ANN search index algorithms (HNSW, Cosine), and Cohere reranking.
* **[Agentic Orchestration](file:///E:/GenAIForge/docs/study-guides/agent_orchestration.md)** — Agentic loops vs. chains, state management in LangGraph, CrewAI role-play systems, and interactive human-in-loop structures.
* **[System Observability](file:///E:/GenAIForge/docs/study-guides/system_observability.md)** — Structured logging, telemetry aggregation (OTEL/Jaeger), Prometheus metrics, and LangFuse trace instrumentation.
* **[Semantic Caching](file:///E:/GenAIForge/docs/study-guides/semantic_cache.md)** — Vector caches, similarity thresholds, and Redis indexing strategies.
* **[API & Microservice Engineering](file:///E:/GenAIForge/docs/study-guides/api_engineering.md)** — Rate limiting, EventSource streams (SSE), and request correlation flow.

### 5. 🏛️ System Architecture Design
Blueprint documents outlining data flow, schemas, protocols, and scaling guidelines.
* **[System Topology Design](file:///E:/GenAIForge/docs/architecture/system_design.md)** — Overview of microservices, proxy (Nginx), and physical network mapping.
* **[Database & Vector Store Schemas](file:///E:/GenAIForge/docs/architecture/database_design.md)** — DDL schemas for PostgreSQL and collections specifications for Qdrant payload indices.
* **[API Protocols & Error Envelopes](file:///E:/GenAIForge/docs/architecture/api_standards.md)** — Standards for REST, SSE formats, and structured error responses.
* **[DevOps Setup & Cloud Deployments](file:///E:/GenAIForge/docs/architecture/devops_deployment.md)** — GitHub Actions CI/CD workflows, Docker configs, and third-party SaaS cloud endpoints.

---

## 🛠️ Tech Stack Cheat Sheet

```
   [ Nginx Reverse Proxy (Port 80) ]
              │
      ┌───────┴────────┐
      ▼                ▼
[ Next.js UI ]   [ FastAPI API (Port 8000) ] ◄──► [ LangFuse Tracing ]
(Port 3000)            │            │
                       ▼            ▼
                 [ Postgres ]   [ Qdrant DB ]
                 (Port 5432)    (Port 6333)
                       ▲
                       │ (Celery Broker / Backend)
                 [ Redis Cache & Queue ]
                 (Port 6379)
                       ▲
                       │
               [ Celery Workers ]
```
