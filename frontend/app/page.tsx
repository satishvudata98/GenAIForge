const modules = [
  "RAG Playground",
  "Multi-Agent Board",
  "Observability & Eval",
  "API Gateway",
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
          Week 1 foundation
        </p>
        <h1 style={{ fontSize: "clamp(2.5rem, 6vw, 5rem)", margin: "0.5rem 0 1rem" }}>
          GenAI Forge
        </h1>
        <p style={{ maxWidth: "42rem", fontSize: "1.1rem", lineHeight: 1.7, margin: 0 }}>
          Initial workspace shell for the production-grade GenAI platform. Backend health routes,
          container orchestration, and the first app surface are now in place.
        </p>
        <div
          style={{
            display: "grid",
            gap: "0.9rem",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            marginTop: "2rem",
          }}
        >
          {modules.map((moduleName) => (
            <article
              key={moduleName}
              style={{
                padding: "1rem",
                borderRadius: "18px",
                background: "rgba(255, 255, 255, 0.78)",
                border: "1px solid rgba(31, 27, 22, 0.08)",
              }}
            >
              <strong>{moduleName}</strong>
              <p style={{ marginBottom: 0, lineHeight: 1.6 }}>
                Planned during Week 1-4 implementation and connected through the FastAPI backend.
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
