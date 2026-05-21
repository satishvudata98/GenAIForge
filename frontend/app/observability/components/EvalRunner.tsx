"use client";

import { useRef, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:48080/v1";

interface Props {
  onRunStarted: () => void;
}

export default function EvalRunner({ onRunStarted }: Props) {
  const [datasetName, setDatasetName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !datasetName.trim()) return;
    setLoading(true);
    setError(null);

    const form = new FormData();
    form.append("dataset_name", datasetName.trim());
    form.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/eval/run`, { method: "POST", body: form });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error ?? `HTTP ${res.status}`);
      }
      setDatasetName("");
      setFile(null);
      if (fileRef.current) fileRef.current.value = "";
      onRunStarted();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex flex-col gap-1 flex-1 min-w-[180px]">
        <label className="text-xs text-forge-text/60">Dataset name</label>
        <input
          value={datasetName}
          onChange={(e) => setDatasetName(e.target.value)}
          placeholder="my-eval-v1"
          required
          className="rounded-lg bg-white/10 border border-white/10 px-3 py-2 text-sm text-forge-text placeholder:text-forge-text/30 outline-none focus:border-forge-accent"
        />
      </div>

      <div className="flex flex-col gap-1 flex-1 min-w-[200px]">
        <label className="text-xs text-forge-text/60">CSV file (question, answer, contexts, ground_truth)</label>
        <input
          ref={fileRef}
          type="file"
          accept=".csv"
          required
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="text-sm text-forge-text/70 file:mr-3 file:rounded file:border-0 file:bg-forge-accent/20 file:px-3 file:py-1 file:text-forge-accent file:cursor-pointer"
        />
      </div>

      <button
        type="submit"
        disabled={loading || !file || !datasetName.trim()}
        className="rounded-lg bg-forge-accent px-4 py-2 text-sm font-semibold text-forge-bg disabled:opacity-40"
      >
        {loading ? "Running…" : "Run Evaluation"}
      </button>

      {error && <p className="w-full text-xs text-red-400">{error}</p>}
    </form>
  );
}
