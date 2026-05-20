const modules = [
  { name: "RAG Playground", href: "/playground", ready: true, desc: "Semantic search with multi-model support, reranking, and streaming responses." },
  { name: "Multi-Agent Board", href: "/agents", ready: true, desc: "LangGraph research & code-review agents with live graph visualization and HITL." },
  { name: "Observability & Eval", href: "/observability", ready: false, desc: "Prometheus + Grafana dashboards, LangFuse tracing, and RAGAS evaluation." },
  { name: "API Gateway", href: "/gateway", ready: false, desc: "Rate limiting, semantic cache stats, and API key management." },
];

export default function HomePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "3rem 1.5rem",
        display: "grid",
        placeItems: "center",
      }}
    >
      <section
        style={{
          width: "min(960px, 100%)",
          background: "rgba(255, 250, 240, 0.82)",
          border: "1px solid rgba(31, 27, 22, 0.12)",
          borderRadius: "28px",
          padding: "2rem",
          boxShadow: "0 20px 60px rgba(84, 59, 34, 0.08)",
        }}
      >
        <p style={{ letterSpacing: "0.24em", textTransform: "uppercase", fontSize: "0.8rem" }}>
          Week 2 — Live
        </p>
        <h1 style={{ fontSize: "clamp(2.5rem, 6vw, 5rem)", margin: "0.5rem 0 1rem" }}>
          GenAI Forge
        </h1>
        <p style={{ maxWidth: "42rem", fontSize: "1.1rem", lineHeight: 1.7, margin: 0 }}>
          Production-grade GenAI platform: RAG pipeline, multi-agent orchestration, and full observability — all in one Docker Compose.
        </p>
        <div
          style={{
            display: "grid",
            gap: "0.9rem",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            marginTop: "2rem",
          }}
        >
          {modules.map((mod) => (
            <a
              key={mod.name}
              href={mod.ready ? mod.href : undefined}
              style={{
                padding: "1rem",
                borderRadius: "18px",
                background: "rgba(255, 255, 255, 0.78)",
                border: `1px solid ${mod.ready ? "rgba(215, 142, 63, 0.30)" : "rgba(31, 27, 22, 0.08)"}`,
                textDecoration: "none",
                color: "inherit",
                opacity: mod.ready ? 1 : 0.6,
                cursor: mod.ready ? "pointer" : "default",
                transition: "border-color 0.15s",
              }}
            >
              <strong style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                {mod.name}
                {mod.ready && <span style={{ fontSize: "0.65rem", color: "#22c55e" }}>●</span>}
              </strong>
              <p style={{ marginBottom: 0, lineHeight: 1.6, marginTop: "0.4rem", fontSize: "0.9rem" }}>
                {mod.desc}
              </p>
            </a>
          ))}
        </div>
      </section>
    </main>
  );
}
