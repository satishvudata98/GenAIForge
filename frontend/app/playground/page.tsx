"use client";

import { useEffect, useState } from "react";
import { usePlaygroundStore } from "@/lib/store";
import IngestPanel from "./components/IngestPanel";
import QueryPanel from "./components/QueryPanel";
import ResponseStream from "./components/ResponseStream";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:48080/v1";

export default function PlaygroundPage() {
  const { sessions, activeSessionId, collections, setCollections } = usePlaygroundStore();
  const [tab, setTab] = useState<"query" | "ingest">("query");

  function loadCollections() {
    fetch(`${API_BASE}/rag/collections`)
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data?.data)) setCollections(data.data);
      })
      .catch(() => {});
  }

  useEffect(() => {
    loadCollections();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <main className="min-h-screen bg-forge-bg p-6">
      <div className="mx-auto w-full max-w-5xl">
        {/* Header */}
        <div className="mb-6">
          <a href="/" className="text-xs text-forge-muted hover:text-forge-accent">← Home</a>
          <h1 className="mt-1 text-3xl font-bold text-forge-text">RAG Playground</h1>
          <p className="mt-1 text-sm text-forge-muted">
            Query your document collections with semantic search, reranking, and multi-model support.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
          {/* Left panel */}
          <div className="rounded-2xl border border-forge-border bg-forge-surface/60 p-5 shadow-sm">
            {/* Tab switcher */}
            <div className="mb-4 flex gap-1 rounded-xl border border-forge-border p-1">
              {(["query", "ingest"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`flex-1 rounded-lg py-1.5 text-xs font-semibold transition ${
                    tab === t ? "bg-forge-accent text-white" : "text-forge-muted hover:text-forge-text"
                  }`}
                >
                  {t === "query" ? "Query" : "Ingest"}
                </button>
              ))}
            </div>

            {tab === "query" ? (
              <>
                {collections.length === 0 && (
                  <p className="mb-3 rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-400">
                    No collections yet — use the Ingest tab to upload documents first.
                  </p>
                )}
                <QueryPanel />
              </>
            ) : (
              <IngestPanel
                onIngestComplete={(col) => {
                  loadCollections();
                  setTab("query");
                  // Notify user the collection is ready
                  void col;
                }}
              />
            )}
          </div>

          {/* Right: response stream */}
          <div>
            {activeSession ? (
              <ResponseStream sessionId={activeSession.id} />
            ) : (
              <div className="flex h-full min-h-[200px] items-center justify-center rounded-2xl border border-dashed border-forge-border text-forge-muted text-sm">
                Response will appear here
              </div>
            )}

            {/* Session history */}
            {sessions.length > 1 && (
              <div className="mt-4">
                <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-forge-muted">History</p>
                <div className="flex flex-wrap gap-2">
                  {sessions.map((s) => (
                    <button
                      key={s.id}
                      onClick={() => usePlaygroundStore.getState().setActiveSession(s.id)}
                      className={`truncate max-w-[200px] rounded-lg px-3 py-1.5 text-xs border transition ${
                        s.id === activeSessionId
                          ? "border-forge-accent bg-forge-accent/10 text-forge-accent"
                          : "border-forge-border bg-forge-surface text-forge-muted hover:border-forge-accent/40"
                      }`}
                    >
                      {s.query}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
