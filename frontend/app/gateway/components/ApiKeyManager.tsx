"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:48080/v1";

interface ApiKeyItem {
  id: string;
  name: string;
  prefix: string;
  created_at: string;
}

interface Props {
  keys: ApiKeyItem[];
  onChanged: () => void;
}

export default function ApiKeyManager({ keys, onChanged }: Props) {
  const [newKeyName, setNewKeyName] = useState("");
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [revoking, setRevoking] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newKeyName.trim()) return;
    setLoading(true);
    setError(null);
    setGeneratedKey(null);

    try {
      const res = await fetch(`${API_BASE}/gateway/keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newKeyName.trim() }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setGeneratedKey(data.key);
      setNewKeyName("");
      onChanged();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create key");
    } finally {
      setLoading(false);
    }
  }

  async function handleRevoke(id: string) {
    setRevoking(id);
    try {
      await fetch(`${API_BASE}/gateway/keys/${id}`, { method: "DELETE" });
      onChanged();
    } finally {
      setRevoking(null);
    }
  }

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-5 flex flex-col gap-5">
      <h3 className="font-semibold text-forge-text">API Key Management</h3>

      {/* Create form */}
      <form onSubmit={handleCreate} className="flex gap-3 items-end">
        <div className="flex flex-col gap-1 flex-1">
          <label className="text-xs text-forge-text/60">New key name</label>
          <input
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="my-service-prod"
            required
            className="rounded-lg bg-white/10 border border-white/10 px-3 py-2 text-sm text-forge-text placeholder:text-forge-text/30 outline-none focus:border-forge-accent"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !newKeyName.trim()}
          className="rounded-lg bg-forge-accent px-4 py-2 text-sm font-semibold text-forge-bg disabled:opacity-40"
        >
          {loading ? "Generating…" : "Generate"}
        </button>
      </form>

      {/* One-time key reveal */}
      {generatedKey && (
        <div className="rounded-lg bg-green-500/10 border border-green-500/30 p-3 flex flex-col gap-1">
          <p className="text-xs text-green-400 font-semibold">Key generated — copy now, it won&apos;t be shown again</p>
          <code className="text-sm text-green-300 break-all">{generatedKey}</code>
        </div>
      )}

      {error && <p className="text-xs text-red-400">{error}</p>}

      {/* Key list */}
      {keys.length === 0 ? (
        <p className="text-sm text-forge-text/40">No active API keys yet.</p>
      ) : (
        <div className="flex flex-col gap-2">
          {keys.map((k) => (
            <div key={k.id} className="flex items-center justify-between rounded-lg bg-white/5 px-4 py-3">
              <div>
                <p className="text-sm font-medium text-forge-text">{k.name}</p>
                <p className="text-xs text-forge-text/40 font-mono">{k.prefix}</p>
                <p className="text-xs text-forge-text/30">{new Date(k.created_at).toLocaleString()}</p>
              </div>
              <button
                onClick={() => handleRevoke(k.id)}
                disabled={revoking === k.id}
                className="text-xs text-red-400 hover:text-red-300 disabled:opacity-40"
              >
                {revoking === k.id ? "Revoking…" : "Revoke"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
