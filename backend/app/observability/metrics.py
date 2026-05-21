"""Prometheus metrics registry — all custom metrics declared here as module-level singletons.

Import and call .inc() / .observe() / .set() from anywhere; Prometheus deduplication
guarantees each metric is registered exactly once per process.
"""
from prometheus_client import Counter, Gauge, Histogram

# ── HTTP metrics (imported by middleware) ────────────────────────────────────

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the API.",
    labelnames=("method", "path", "status_code"),
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    labelnames=("method", "path"),
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0),
)

# ── LLM metrics ──────────────────────────────────────────────────────────────

LLM_TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "Cumulative LLM token volume.",
    labelnames=("model", "token_type"),  # token_type: prompt | completion
)

LLM_REQUEST_DURATION = Histogram(
    "llm_request_duration_seconds",
    "Time from LLM call start to first token received.",
    labelnames=("model", "provider"),
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0),
)

LLM_ESTIMATED_COST_USD = Counter(
    "llm_estimated_cost_usd_total",
    "Cumulative estimated LLM cost in USD.",
    labelnames=("model",),
)

# ── RAG / cache metrics ──────────────────────────────────────────────────────

RAG_CACHE_HITS = Counter(
    "rag_cache_hits_total",
    "Semantic cache hits on RAG queries.",
)

RAG_CACHE_MISSES = Counter(
    "rag_cache_misses_total",
    "Semantic cache misses on RAG queries.",
)

# ── Agent metrics ─────────────────────────────────────────────────────────────

ACTIVE_AGENT_RUNS = Gauge(
    "active_agent_runs",
    "Number of agent graph runs currently in progress.",
    labelnames=("agent_type",),
)

AGENT_RUNS_TOTAL = Counter(
    "agent_runs_total",
    "Total agent graph runs started.",
    labelnames=("agent_type", "status"),  # status: started | completed | error
)
