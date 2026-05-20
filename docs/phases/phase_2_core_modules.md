# Phase 2: Core Playground & Agent Board

This phase brings the application's user interface to life by building the Next.js 14 frontend modules and implementing multi-agent execution engines with background task scheduling.

---

## 🎯 Phase Goals
- Build the Next.js 14 application shell using the App Router, incorporating unified state management via Zustand.
- Implement the client-side RAG Playground interface, demonstrating side-by-side RAG comparison.
- Design multi-model support in the backend, supporting Groq, Google Gemini, and xAI Grok.
- Construct the multi-agent execution engine using Celery, Redis, and LangGraph (with human-in-the-loop injection).
- Integrate CrewAI pipelines for collaborative, role-based multi-agent execution.
- Create the Agent Board UI featuring live execution graphs rendered dynamically via React Flow.

---

## 🛠️ Features Covered
1. **Model Router (`llm_clients.py`)**: Seamless abstraction for OpenAI (`gpt-4o-mini`), Groq (`llama3-70b`), Google AI Studio (`gemini-1.5-flash`), and xAI (`grok-2`).
2. **Research Agent (LangGraph)**: An agentic loop executing planning, Tavily/Wikipedia search, fact extraction, and report compilation.
3. **Code Review Agent with Human Oversight (LangGraph)**: Dynamic code analysis with validation checkpoints that pause execution until human input is provided.
4. **Content Pipeline (CrewAI)**: A sequential workflow where a Researcher, Writer, and Editor work together to compile articles.
5. **Async Celery Task Worker**: Backend execution of long-running agent tasks in background worker queues.
6. **Next.js Interface**: Responsive dashboard containing navigation layouts and custom themes.
7. **Interactive Agent Flow Rendering**: Real-time visualization using React Flow that lights up nodes based on execution status.

---

## 🗂️ Technical Modules Involved

```
backend/
├── app/
│   ├── api/v1/
│   │   └── agents.py               # Starts async agent runs and handles human resume calls
│   ├── core/
│   │   └── llm_clients.py          # Groq, Gemini, Grok API bindings
│   ├── agents/
│   │   ├── graph.py                # State machines for Research and Code Review graphs
│   │   ├── nodes.py                # Functions executed at each node of the state machine
│   │   ├── tools.py                # Custom tools: web search, Wikipedia, calculator
│   │   ├── crew.py                 # CrewAI agent roles and task sequences
│   │   └── state.py                # Pydantic schemas representing graph state
│   └── workers/
│       ├── celery_app.py           # Celery configuration with Redis broker
│       └── tasks.py                # Async task definitions for agent runs
frontend/
├── app/
│   ├── layout.tsx                  # Global theme context and styling imports
│   ├── page.tsx                    # Portfolio index dashboard
│   ├── playground/page.tsx         # RAG Playground module
│   └── agents/page.tsx             # Agent Board module
└── components/
    ├── chat/                       # Streaming message and citation boxes
    ├── rag/                        # Document upload and retrieval score panels
    └── agents/
        ├── AgentGraph.tsx          # React Flow visualization
        ├── AgentLog.tsx            # Streaming terminal for agent thoughts
        └── HumanInLoop.tsx         # UI prompts for human-in-the-loop execution
```

---

## 🌐 Backend, Frontend, and AI Integrations
- **Agent Tracing & SSE**: As Celery workers execute graph nodes, they publish state changes to Redis. The FastAPI application processes these logs and streams them to the frontend using SSE.
- **Human-in-the-loop Synchronization**: When the Code Review Graph hits a decision gate, it pauses and stores its state in PostgreSQL. The frontend displays an approval modal to collect user feedback, which is then submitted back to resume execution.
- **React Flow Integration**: The frontend maps incoming SSE events to specific React Flow nodes, updating their visual state (e.g., queued, running, completed) dynamically.

---

## 🗄️ Database Changes (PostgreSQL Schema)
The database structure is updated to support background executions:
- **`agent_runs`**: Tracks task status (e.g., queued, running, paused, done, error), execution parameters, token usage, cost metrics, and duration.
- **`users`**: Associated with agent runs to track execution limits and budget usage.

---

## 🔌 APIs & Services Required

### Start Agent Task
* **URI**: `POST /v1/agents/run`
* **Content-Type**: `application/json`
* **Payload**:
  ```json
  {
    "pipeline": "research | code_review | content",
    "input": "User instructions or code snippet",
    "config": {}
  }
  ```
* **Returns**: `{ "job_id": "string", "status": "queued" }`

### Live Task Monitor
* **URI**: `GET /v1/agents/status/{job_id}`
* **Response Type**: `text/event-stream` (SSE)
* **Events**:
  - `node_start`: Emitted when entering a graph node.
  - `node_end`: Emitted when completing a graph node, containing output logs.
  - `tool_call`: Emitted when an agent runs a tool.
  - `human_input_required`: Emitted when a human decision is needed.

### Resume Task
* **URI**: `POST /v1/agents/resume/{job_id}`
* **Content-Type**: `application/json`
* **Payload**: `{ "human_input": "Approval text or modified code" }`

---

## 📊 Estimated Complexity & Risks

### Estimated Complexity: High
- Implementing state persistence for LangGraph execution loops inside Celery workers requires robust transaction management.
- Synchronizing SSE message queues with React Flow graph nodes requires clean state management in Next.js.

### Key Risks & Mitigation
1. **Stuck Background Tasks**: Workers may hang if external tool APIs block indefinitely.
   * *Mitigation*: Configure request timeouts for all tool network operations (e.g., Tavily, Wikipedia).
2. **Out-of-Order SSE Events**: Rapid state transitions might cause the UI to display updates out of order.
   * *Mitigation*: Include sequential sequence IDs in the SSE payload to ensure correct message ordering in Zustand.

---

## 🧪 Testing Requirements
- **LangGraph Verification**: Write unit tests utilizing mock tool components to verify graph path logic.
- **Worker Verification**: Verify Celery task registration, task execution flow, and handling of failed jobs.
- **Frontend Component Tests**: Use Vitest to test React Flow rendering logic and verify that state changes trigger updates correctly.
