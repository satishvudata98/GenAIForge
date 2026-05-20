# Feature Specification: Multi-Agent Board

This document provides a technical overview and architectural design for the Multi-Agent Board, which demonstrates multi-agent orchestration using LangGraph state machines and CrewAI role-based pipelines.

---

## 📖 Feature Overview

### Description
The Multi-Agent Board allows users to trigger, monitor, and interact with complex multi-agent workflows. The interface renders the agent communication graph in real-time, displaying status changes and agent thoughts dynamically. It supports human-in-the-loop validation, pausing agent executions until a user provides input.

### Pre-built Workflows
1. **Research Agent (LangGraph)**: An agentic loop executing planning, search, fact extraction, and report compilation.
2. **Code Review Agent (LangGraph)**: Parses code, checks complexity, verifies security, and pauses for human verification before suggesting changes.
3. **Content Pipeline (CrewAI)**: A sequential workflow where a Researcher, Writer, and Editor work together to compile articles.

### User Flow
1. The user navigates to `/agents`, selects a pipeline, enters an initial prompt, and clicks "Run".
2. An interactive `React Flow` canvas renders the workflow nodes.
3. As the execution begins, the active node flashes amber, transitioning to green upon completion.
4. If a human check is triggered, the run pauses, highlighting the target node in blue and displaying a text input.
5. The user enters feedback, clicks "Resume", and the workflow continues to completion.

---

## ⚙️ Technical Breakdown

### Internal Architecture & State Flow

```
[Frontend Client] 
       │
       ▼ (POST /v1/agents/run)
[FastAPI Gateway] ──► (Trigger Job) ──► [Celery Worker]
       │                                     │
       │ (SSE Stream / status)               ▼ (Update State)
[Zustand Store] ◄────────────────────── [Redis Pub/Sub]
       │
       ▼ (Render Nodes)
 [React Flow Canvas]
```

### State Checkpointing & Human-in-the-Loop
For the Code Review Agent, state persistence is handled using PostgreSQL:
1. **Graph Compilation**: The LangGraph state machine is configured with a PostgreSQL checkpoint saver (`SqliteSaver` is replaced with `PostgresSaver` in production).
2. **Execution Pause**: When execution reaches the `suggest_improvements` node, it checks if a human override flag is active. If active, it saves the current state and raises a pause interrupt.
3. **Wait State**: The Celery worker saves the state ID to the database, updates the status to `paused`, publishes a `human_input_required` event, and releases the task worker thread.
4. **Resuming Execution**: When the user submits feedback, the `/v1/agents/resume/{job_id}` endpoint updates the state history with the user's input, updates the status to `running`, and queues a new Celery worker job to resume execution from the checkpoint.

---

## 🧠 Engineering Concepts Behind It

### State Machines & Graph Architecture
- **What it is**: Software designs that represent agent workflows as networks of nodes (functions) connected by edges (execution paths).
- **Why it is used**: Large Language Models can produce inconsistent results when run in simple loops. Graph-based architectures enforce predictable execution paths.
- **How it works**: System states are modeled using structured Pydantic schemas. Each node receives the current state, performs an action, updates the state variables, and returns the modified state to the router to determine the next path.

```
       [ plan_research ]
               │
               ▼
        [ web_search ]
               │
               ▼
       [ extract_facts ] ───► (No facts found) ──► [ END ]
               │
               ├─► (facts > 3)  ──► [ cross_check ] ──┐
               │                                      ▼
               └─► (facts <= 3) ─────────────────► [ synthesize ]
                                                      │
                                                      ▼
                                                [ write_report ]
                                                      │
                                                      ▼
                                                   [ END ]
```

### Role-Based Agent Collaboration (CrewAI)
- **What it is**: Multi-agent orchestration frameworks where agents are configured with distinct personas, goals, and communication channels.
- **Why it is used**: Breaking down complex tasks into smaller sub-tasks assigned to specialized agent personas improves output quality.
- **How it works**: Agents are defined with a `role`, `backstory`, and `goal`. Tasks are mapped sequentially or hierarchically. The output of one agent is passed as context to the next agent in the sequence.

### Real-Time Event Streaming (SSE over Redis)
- **What it is**: A communication channel where the server streams updates to client browsers over a persistent HTTP connection.
- **Why it is used**: Standard API polling is inefficient and adds unnecessary load to the server. Server-Sent Events (SSE) deliver real-time logs instantly.
- **How it works**: Agent nodes publish status logs to a Redis pub/sub channel. The FastAPI application subscribes to the channel and forwards events to connected clients.

---

## 🛠️ Best Practices & Performance Optimization
- **Enforce Idempotency**: Ensure that all tool operations (e.g., search queries, database saves) can be safely retried without side effects if a node fails.
- **Set Node Timeouts**: Configure execution limits on agent nodes to prevent tasks from hanging.
- **Isolate Thread Workloads**: Run agent executions on Celery worker threads to keep the main FastAPI web server responsive.
