"use client";

import { useRef, useState } from "react";

interface IngestPanelProps {
  onIngestComplete: (collection: { id: string; name: string }) => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:48080/v1";

export default function IngestPanel({ onIngestComplete }: IngestPanelProps) {
  const [collectionName, setCollectionName] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [chunkSize, setChunkSize] = useState(512);
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [result, setResult] = useState<{ documents_ingested: number; chunks_indexed: number; estimated_cost_usd: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!files || files.length === 0 || !collectionName.trim()) return;

    setStatus("uploading");
    setError(null);
    setResult(null);

    const form = new FormData();
    form.append("collection_name", collectionName.trim());
    form.append("chunk_size", String(chunkSize));
    for (const f of Array.from(files)) form.append("files", f);

    try {
      const res = await fetch(`${API_BASE}/rag/ingest`, { method: "POST", body: form });
      const json = await res.json();
      if (!res.ok) {
        setError(json?.error?.message ?? "Ingestion failed.");
        setStatus("error");
        return;
      }
      const d = json?.data;
      setResult({ documents_ingested: d.documents_ingested, chunks_indexed: d.chunks_indexed, estimated_cost_usd: d.estimated_cost_usd });
      setStatus("done");
      onIngestComplete({ id: d.collection_id, name: d.collection_name });
      setCollectionName("");
      setFiles(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch {
      setError("Network error — is the backend running?");
      setStatus("error");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div>
        <label className="mb-1 block text-xs font-medium text-forge-muted">Collection Name</label>
        <input
          type="text"
          value={collectionName}
          onChange={(e) => setCollectionName(e.target.value)}
          placeholder="e.g. my-docs"
          required
          className="w-full rounded-xl border border-forge-border bg-forge-surface px-4 py-2.5 text-sm text-forge-text placeholder:text-forge-muted/60 outline-none focus:border-forge-accent/50"
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-forge-muted">Files</label>
        <input
          ref={fileRef}
          type="file"
          multiple
          accept=".pdf,.txt,.md,.docx,.pptx,.html,.htm,.csv,.json,.epub,.ipynb"
          onChange={(e) => setFiles(e.target.files)}
          className="w-full cursor-pointer rounded-xl border border-forge-border bg-forge-surface px-4 py-2.5 text-sm text-forge-muted file:mr-3 file:rounded-lg file:border-0 file:bg-forge-accent/10 file:px-3 file:py-1 file:text-xs file:font-semibold file:text-forge-accent"
        />
        {files && files.length > 0 && (
          <p className="mt-1 text-xs text-forge-muted">{files.length} file{files.length > 1 ? "s" : ""} selected</p>
        )}
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-forge-muted">Chunk Size: {chunkSize} tokens</label>
        <input
          type="range"
          min={128}
          max={2048}
          step={128}
          value={chunkSize}
          onChange={(e) => setChunkSize(Number(e.target.value))}
          className="w-full accent-forge-accent"
        />
      </div>

      {/* Inline hint when something is missing */}
      {(!collectionName.trim() || !files || files.length === 0) && status !== "uploading" && (
        <p className="text-xs text-forge-muted">
          {!collectionName.trim() && (!files || files.length === 0)
            ? "Enter a collection name and select at least one file."
            : !collectionName.trim()
            ? "Enter a collection name to continue."
            : "Select at least one file to continue."}
        </p>
      )}

      <button
        type="submit"
        disabled={status === "uploading" || !collectionName.trim() || !files || files.length === 0}
        className="rounded-xl bg-forge-accent px-5 py-2.5 text-sm font-semibold text-white hover:opacity-90 transition disabled:opacity-40"
      >
        {status === "uploading" ? "Uploading…" : "Ingest Documents"}
      </button>

      {status === "done" && result && (
        <div className="rounded-xl border border-green-500/30 bg-green-500/10 p-3 text-xs text-green-400">
          <p className="font-semibold">Ingestion complete</p>
          <p>{result.documents_ingested} docs · {result.chunks_indexed} chunks · ${result.estimated_cost_usd} embedding cost</p>
        </div>
      )}

      {status === "error" && error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
          {error}
        </div>
      )}
    </form>
  );
}
