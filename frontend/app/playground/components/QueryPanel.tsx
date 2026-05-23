"use client";

import { useRef, useState } from "react";
import { streamPost } from "@/lib/sse";
import { type Source, usePlaygroundStore } from "@/lib/store";

const MODELS = [
  { label: "GPT-4o-mini", value: "gpt-4o-mini" },
  { label: "GPT-4o", value: "gpt-4o" },
  { label: "GPT-120B", value: "openai/gpt-oss-120b" },
  { label: "Groq Llama 3.3 70B", value: "llama-3.3-70b-versatile" },
  { label: "Gemini 3.1 Flash Lite", value: "gemini-3.1-flash-lite" },
  { label: "Gemini 2.5 Flash", value: "gemini-2.5-flash" },
];

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:48080/v1";

export default function QueryPanel() {
  const [query, setQuery] = useState("");
  const [collectionId, setCollectionId] = useState("");
  const [topK, setTopK] = useState(5);
  const [useReranker, setUseReranker] = useState(true);
  const [streamError, setStreamError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const { selectedModel, setSelectedModel, collections, startSession, appendChunk, addSource, finalizeSession } =
    usePlaygroundStore();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || !collectionId) return;

    setStreamError(null);
    abortRef.current?.abort();

    const sessionId = startSession(query, collectionId, selectedModel);

    abortRef.current = streamPost(
      `${API_BASE}/rag/query`,
      { query, collection_id: collectionId, model: selectedModel, top_k: topK, use_reranker: useReranker },
      {
        onChunk: (content) => {
          if (typeof content === "string") appendChunk(sessionId, content);
        },
        onSource: (content) => {
          const source: Source = content as Source;
          addSource(sessionId, source);
        },
        onMeta: (content) => {
          const meta = content as { latency_ms?: number; cache?: string };
          finalizeSession(sessionId, meta.latency_ms ?? 0, meta.cache === "HIT");
        },
        onDone: () => finalizeSession(sessionId, 0, false),
        onError: (err) => {
          setStreamError(err.message || "Stream failed — is the backend running?");
          finalizeSession(sessionId, 0, false);
        },
      }
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      {/* Collection picker */}
      <div className="flex gap-2">
        <select
          value={collectionId}
          onChange={(e) => setCollectionId(e.target.value)}
          className="flex-1 rounded-xl border border-forge-border bg-forge-surface px-3 py-2 text-sm text-forge-text outline-none"
        >
          <option value="">Select collection…</option>
          {collections.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        {/* Model picker */}
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="rounded-xl border border-forge-border bg-forge-surface px-3 py-2 text-sm text-forge-text outline-none"
        >
          {MODELS.map((m) => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>
      </div>

      {/* Options row */}
      <div className="flex items-center gap-4 text-xs text-forge-muted">
        <label className="flex items-center gap-1.5">
          <span>Top-K</span>
          <input
            type="number"
            min={1}
            max={20}
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="w-14 rounded-lg border border-forge-border bg-forge-surface px-2 py-1 text-center outline-none"
          />
        </label>
        <label className="flex items-center gap-1.5 cursor-pointer">
          <input type="checkbox" checked={useReranker} onChange={(e) => setUseReranker(e.target.checked)} />
          <span>Rerank</span>
        </label>
      </div>

      {/* Query textarea */}
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question about your documents…"
        rows={3}
        className="w-full resize-none rounded-xl border border-forge-border bg-forge-surface px-4 py-3 text-sm text-forge-text placeholder:text-forge-muted/60 outline-none focus:border-forge-accent/50"
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit(e as React.FormEvent);
        }}
      />

      <button
        type="submit"
        disabled={!query.trim() || !collectionId}
        className="rounded-xl bg-forge-accent px-5 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
      >
        Ask
      </button>

      {streamError && (
        <p role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-400">
          {streamError}
        </p>
      )}
    </form>
  );
}
