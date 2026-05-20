# Week 2: Frontend Modules & Multi-Agent Engines

This week focuses on implementing semantic caching and rate limiting, adding multi-model support, creating LangGraph and CrewAI pipelines, setting up Celery workers, and building the RAG Playground and Agent Board user interfaces.

---

## 🎯 Weekly Goals
- Build the token bucket rate limiter and GPTCache semantic caching system.
- Integrate Groq, Gemini, and Grok clients into the backend.
- Build the Research Agent and Code Review Agent (with human-in-the-loop validation) using LangGraph.
- Implement the sequential content pipeline using CrewAI.
- Configure Celery background workers to execute agent jobs asynchronously.
- Build the Next.js frontend pages for the RAG Playground and Agent Board (using React Flow).

---

## 📆 Day-by-Day Implementation Checklist

### Day 8: Semantic Caching & Rate Limiting
- [ ] Build a rate-limiting middleware in FastAPI using Redis to enforce token bucket limits per API key.
- [ ] Set up `GPTCache` on top of Redis to cache LLM responses using semantic similarity.
- [ ] Configure the semantic similarity threshold to `0.95` cosine similarity.
- [ ] Update the RAG query path to return `X-Cache: HIT` or `X-Cache: MISS` headers.
- [ ] Verify that cached requests resolve in under 100ms.

### Day 9: Multi-Model Integration
- [ ] Build `backend/app/core/llm_clients.py` as a unified abstraction for model providers.
- [ ] Add client bindings for Groq (`llama3-70b-8192`), Google AI Studio (`gemini-1.5-flash`), and xAI (`grok-2`).
- [ ] Implement retry helpers using `tenacity` to handle rate limits and transient errors.
- [ ] Map token counting utilities for each model provider to ensure accurate usage stats.
- [ ] Expose model selection query APIs to list supported models.

### Day 10: Research Agent Graph (LangGraph)
- [ ] Define the agent state schema in `backend/app/agents/state.py`.
- [ ] Implement the planning, web search, fact extraction, and report compilation nodes.
- [ ] Configure conditional routing edges based on search results.
- [ ] Connect the Tavily Search API and Wikipedia APIs as tools.
- [ ] Test the agent graph locally to ensure compile operations resolve successfully.

### Day 11: Code Review Agent & Human-in-the-Loop
- [ ] Design the Code Review state machine using LangGraph.
- [ ] Add the analysis, security verification, and suggestion nodes.
- [ ] Configure a state checkpointing memory database using PostgreSQL.
- [ ] Add an approval node that pauses graph execution and waits for human input.
- [ ] Expose the `/v1/agents/resume/{job_id}` endpoint to accept human feedback and resume the execution flow.

### Day 12: CrewAI Pipeline & Celery Workers
- [ ] Define CrewAI agents (Researcher, Writer, Editor) and sequential task workflows.
- [ ] Configure Celery workers inside `backend/app/workers/celery_app.py` with Redis task queues.
- [ ] Define Celery task jobs to execute agent workflows in the background.
- [ ] Create SSE endpoints to stream worker execution events (such as active nodes, tool calls, and LLM completions) in real-time.
- [ ] Verify background worker executions by running test jobs.

### Day 13: Next.js Bootstrap & RAG Playground UI
- [ ] Initialize the Next.js 14 repository using the App Router.
- [ ] Set up the styling system using Tailwind CSS v3 and load clean font families.
- [ ] Configure global state stores using Zustand to manage current sessions and queries.
- [ ] Build the RAG Playground UI (`/playground`) featuring a side-by-side RAG comparison mode.
- [ ] Implement document upload indicators and cache hit indicators.

### Day 14: Agent Board UI & React Flow integration
- [ ] Build the Agent Board UI (`/agents`) featuring run configurations and logs.
- [ ] Implement the agent execution visualizer using `React Flow`.
- [ ] Connect SSE event streams to light up graph nodes (such as running, paused, or completed) in real-time.
- [ ] Build the human-in-the-loop input modal to display review prompts and submit approvals back to the backend.
- [ ] Verify that agent workflows run, pause, collect input, and resume successfully from the UI.

---

## 🛠️ Code Architecture & Design Goals
- Isolate agent state storage using Pydantic schemas to prevent data conflicts.
- Leverage Redis pub/sub features to stream worker logs to SSE client connections.
- Ensure React Flow layouts are computed dynamically based on the active graph definition.

---

## 🔍 Refactoring Checkpoints
- **Zustand State Cleanup**: Reset workspace stores when navigating between pages to avoid memory leaks.
- **Worker Concurrency**: Configure Celery prefetch limits to prevent task starvation on single worker instances.

---

## 🧪 Testing & Debugging Tasks
- Verify rate limiting rules by sending concurrent requests.
- Verify that semantic caching returns correct hits for similar query strings.
- Test agent state machines using mocks for external tools to ensure paths resolve correctly.
