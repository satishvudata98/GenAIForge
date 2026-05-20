# System Topology & Architecture Design

This document details the system architecture, component integrations, security controls, and scaling strategies for the **GenAI Forge** platform.

---

## 🏛️ Overall System Topology

The system is designed as a modular microservices architecture. It uses **Nginx** as a reverse proxy, a **Next.js** frontend, an async **FastAPI** backend, and a **Celery** task worker queue.

```
                  [ Public Internet traffic ]
                              │
                              ▼ (Port 80 / 443)
                    [ Nginx Reverse Proxy ]
                              │
            ┌─────────────────┴─────────────────┐
            ▼ (Port 3000)                       ▼ (Port 8000)
    [ Next.js UI ]                   [ FastAPI App Gateway ]
            │                                   │
            │ (GraphQL / HTTP)                  ├─► [ PostgreSQL 16 ] (Port 5432)
            ▼                                   ├─► [ Qdrant DB ] (Port 6333)
     [ SaaS / Embeds ]                          ├─► [ Redis Cache ] (Port 6379)
  (LangFuse / Grafana)                          │         ▲
                                                ▼         │
                                         [ Celery Workers ]
```

---

## 💻 Component Architecture

### 1. Frontend Architecture (Next.js 14)
- **Rendering Framework**: Next.js 14 App Router. It uses Server Components for page rendering and Client Components for interactive UI elements.
- **State Management**: Managed using `Zustand` stores to keep UI state synchronized.
- **Real-Time Connections**: Uses browser native `EventSource` connections to process SSE streaming tokens.
- **Visual Rendering**: Renders graph nodes dynamically using the `React Flow` framework.

### 2. Backend Architecture (FastAPI)
- **API Engine**: FastAPI handles HTTP request routing asynchronously.
- **Settings System**: Uses `pydantic-settings` to load and validate configurations from environment variables.
- **Concurrency Model**: Implements Python's async/await framework to handle connections without blocking main processes.

### 3. Background Workers (Celery)
- **Task Runner**: Celery executes long-running tasks in the background.
- **Message Broker**: Redis serves as the message queue broker.
- **Execution Queues**:
  - `agents`: Handles multi-agent execution graphs.
  - `evals`: Executes RAGAS quality checks and evaluations.

---

## 🤖 AI Orchestration Architecture

AI pipelines are managed using specialized frameworks:
- **RAG Pipeline**: Managed using `LlamaIndex` to parse documents and search vector indices.
- **Multi-Agent Systems**: Managed using `LangGraph` to enforce stateful workflows and handle human validation pauses.
- **Persona Collaborations**: Managed using `CrewAI` to run sequential multi-agent tasks.

---

## 🔒 Security Architecture

- **API Keys**: Access to endpoints is secured using API keys verified by the gateway.
- **CORS Policies**: Restricts API access to authorized frontend domains in production.
- **Credential Storage**: Database credentials and API tokens are loaded from environment variables and never hardcoded.

---

## 📈 Scaling & Reliability Strategies

- **Isolate Workloads**: Run heavy processing tasks (like evaluations or agent flows) on Celery workers to keep the FastAPI web server responsive.
- **Database Scaling**: Migrate databases to managed cloud services (like Supabase and Qdrant Cloud) in production to ensure high availability.
- **Disable Stream Buffering**: Add the `X-Accel-Buffering: no` header to streaming responses to prevent Nginx from caching data chunks.
