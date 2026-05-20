# Phase 4: Optimization, Tests & Deploys

This phase focuses on testing the codebase, establishing automated CI/CD pipelines, and deploying the application services to production cloud environments.

---

## 🎯 Phase Goals
- Achieve comprehensive test coverage across both backend (Pytest) and frontend (Vitest) codebases.
- Set up automated linting, formatting, and unit testing within GitHub Actions pipelines.
- Deploy the frontend to Vercel and the backend service to Railway.
- Migrate database and storage backends to cloud instances (Supabase, Qdrant Cloud, Upstash Redis).
- Configure production observability using LangFuse Cloud and Grafana Cloud.
- Conduct thorough end-to-end verification of all deployed services.

---

## 🛠️ Features Covered
1. **API Integration Tests (Pytest)**: Comprehensive API testing utilizing Docker-managed databases to isolate test runs.
2. **AI Pipeline Mock Testing**: Testing RAG operations and agent state changes using mock LLM responses.
3. **Frontend Component Isolation**: Vitest configurations to test Next.js components in isolation.
4. **Automated CI Workflows**: GitHub Actions validation running linting checks, formatting checks, and test suites on every pull request.
5. **Continuous Deployment (CD)**: Automated deployment workflows deploying the frontend to Vercel and the backend API to Railway on merges to the `main` branch.
6. **Cloud Infrastructure Migration**: Configured migrations from local containers to managed cloud services.

---

## 🗂️ Technical Modules Involved

```
backend/
├── tests/
│   ├── conftest.py                 # Set up shared fixtures, databases, and LLM mocks
│   ├── test_api.py                 # Tests verifying API route responses
│   ├── test_rag.py                 # Tests verifying RAG pipeline executions
│   └── test_agents.py              # Tests verifying agent graph transitions
frontend/
├── tests/                          # Vitest configurations
│   └── components/                 # Frontend component tests
.github/
└── workflows/
    ├── ci.yml                      # Integration tests pipeline
    └── deploy.yml                  # Deployment pipeline
```

---

## 🌐 Backend, Frontend, and AI Integrations
- **CI Service Integration**: The GitHub Actions runner provisions temporary PostgreSQL and Redis containers to execute backend integration tests.
- **Production AI API Configurations**: Deployment configurations are updated to route requests to cloud endpoints (such as Qdrant Cloud and Upstash Redis) using updated environment variables.
- **Production Observability**: Local tracing and monitoring outputs are redirected to LangFuse Cloud and Grafana Cloud.

---

## 🗄️ Database Changes (Cloud Deployment)
- **Supabase PostgreSQL**: The relational database schema is deployed to Supabase using Alembic migrations, updating the `DATABASE_URL` config.
- **Qdrant Cloud**: Vector indices are migrated to a managed Qdrant instance.
- **Upstash Redis**: Redis cache keys and Celery tasks are redirected to a serverless Redis database.

---

## 🔌 APIs & Services Required

### Verification Check
* **URI**: `/health`
* **Returns**: `{ "status": "healthy", "version": "1.0.0" }`
* **Response Time Target**: Less than 50ms.

### Production Deployment Map
* **Frontend**: Deployed on Vercel Edge Networks.
* **Backend API / Worker**: Deployed on Railway using Docker containers.
* **Databases**: Supabase (PostgreSQL), Qdrant Cloud (Vector DB), and Upstash (Redis Cache).

---

## 📊 Estimated Complexity & Risks

### Estimated Complexity: Low
- Relocating services to cloud hosting is straightforward because configurations are externalized via environment variables.
- Mocking external AI API responses inside test suites ensures reliable and cost-effective test runs.

### Key Risks & Mitigation
1. **Testing Costs**: Running integration tests in CI using live OpenAI API keys can accumulate high charges and expose keys.
   * *Mitigation*: Mock all LLM and embedding calls in test suites using custom Pytest fixtures.
2. **Cold Start Latency**: Deployed API instances on Railway may experience cold start delays.
   * *Mitigation*: Configure active health checks on Railway to keep backend containers active and warm.

---

## 🧪 Testing Requirements
- **Linter Checks**: Verify that code passes `ruff check backend/` and `npm run lint` cleanly.
- **Coverage Targets**: Aim for at least 80% test coverage across core RAG pipelines and agent state engines.
- **Manual Verification**: Walk through the user interface post-deployment to verify that chat interactions, agent runs, and tracing operations resolve successfully.
