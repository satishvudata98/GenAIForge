# Week 4: Quality Verification & Cloud Deployment

This week focuses on writing automated tests for the frontend and backend, setting up CI/CD workflows, migrating local databases to cloud services, deploying application services, and verifying the production environment.

---

## 🎯 Weekly Goals
- Achieve test coverage across backend endpoints (Pytest) and frontend modules (Vitest).
- Configure CI/CD pipelines to build, test, and deploy services on merges to `main`.
- Migrate databases and caches to Supabase, Qdrant Cloud, and Upstash.
- Deploy the FastAPI backend to Railway and the Next.js frontend to Vercel.
- Configure production observability using LangFuse Cloud and Grafana Cloud.
- Conduct final verification tests in the production environment.

---

## 📆 Day-by-Day Implementation Checklist

### Day 22: Backend Test Fixtures
- [ ] Configure `backend/tests/conftest.py` to set up test environments.
- [ ] Implement database fixtures using SQLAlchemy to run tests against an isolated PostgreSQL instance.
- [ ] Create mock fixtures for embedding models, LLM APIs, and Cohere reranker endpoints.
- [ ] Configure clean database seed utilities to populate test data.
- [ ] Run test scripts to verify that mock fixtures execute successfully.

### Day 23: API & RAG Integration Tests
- [ ] Write integration tests in `backend/tests/test_api.py` verifying response envelopes and HTTP error codes.
- [ ] Write tests in `backend/tests/test_rag.py` to verify ingestion pipelines, document splitting, and vector queries.
- [ ] Test the semantic caching layer to confirm cache hit outputs for identical requests.
- [ ] Run the test suite and verify that all test assertions pass.

### Day 24: Agent Graph Validation Tests
- [ ] Write tests in `backend/tests/test_agents.py` to verify state transitions in LangGraph pipelines.
- [ ] Test conditional edges by simulating various tool outputs.
- [ ] Validate human-in-the-loop flows by simulating state pauses, inputs, and resume operations.
- [ ] Test Celery background task registration and worker performance.

### Day 25: Frontend Component Tests
- [ ] Configure the Vitest environment in the frontend directory.
- [ ] Write unit tests for Next.js UI components (such as chat bubbles, citation boxes, and status badges).
- [ ] Write unit tests for Zustand state stores to verify state updates and cache storage.
- [ ] Mock Server-Sent Event (SSE) connections to verify that incoming stream tokens update chat feeds correctly.
- [ ] Run the frontend tests and verify that the test suite passes.

### Day 26: Pre-Commit Checks & Makefile Utilities
- [ ] Configure linting and formatting hooks using pre-commit configurations.
- [ ] Build a `Makefile` in the root directory to simplify operations (such as `make dev`, `make test`, `make build`, and `make lint`).
- [ ] Create health check scripts (`scripts/health_check.sh`) to query local containers.
- [ ] Verify that Git operations run all pre-commit checks successfully.

### Day 27: Backend Deployment
- [ ] Set up the Railway API CLI tool and login to the control console.
- [ ] Create a deployment service config mapping the backend FastAPI application.
- [ ] Configure background tasks by creating a separate worker container on Railway for Celery.
- [ ] Add production environment variables inside the Railway console.
- [ ] Merge code changes to the `main` branch to trigger CD pipelines.

### Day 28: Data Store Migrations
- [ ] Provision a cloud PostgreSQL database using Supabase and run migrations.
- [ ] Provision a cloud Qdrant Vector database and run setup scripts.
- [ ] Provision a serverless Upstash Redis instance and update the cache URLs.
- [ ] Seed the production Qdrant database with reference documents.
- [ ] Verify that the deployed API service connects to the cloud databases successfully.

### Day 29: Frontend & Observability Deployments
- [ ] Deploy the Next.js frontend to Vercel.
- [ ] Configure CORS origins inside the backend API to authorize Vercel frontend domains.
- [ ] Update the LangFuse client variables to route traces to LangFuse Cloud.
- [ ] Connect the Prometheus metrics stream to Grafana Cloud.
- [ ] Verify that live dashboards load metric values and execution traces successfully.

### Day 30: Production Smoke Tests & Review
- [ ] Perform smoke tests on the production environment, verifying chat, agent graph, and dashboard features.
- [ ] Verify that execution logs flow correctly to the production LangFuse dashboard.
- [ ] Record a 5-minute product walkthrough video showcasing the portfolio app modules.
- [ ] Finalize the main `README.md` file, documenting the system architecture and cloud migration steps.

---

## 🛠️ Code Architecture & Design Goals
- Prevent testing code from running against production databases.
- Keep production API keys secure by loading them strictly from environment variables.
- Ensure that the frontend application remains functional even if secondary services (like Jaeger or LangFuse) are temporarily offline.

---

## 🔍 Refactoring Checkpoints
- **Mock Cleanup**: Verify that mock configurations are scoped to test runs and do not affect the main application code.
- **CORS Configuration**: Restrict allowed CORS origins in the production API to authorization domains.

---

## 🧪 Testing & Debugging Tasks
- Verify that GitHub Actions CI checks complete successfully.
- Verify that failing test cases in backend suites trigger CI build failures.
- Run final manual verification checks on the live production site.
