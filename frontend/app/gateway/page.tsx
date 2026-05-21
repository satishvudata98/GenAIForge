"use client";

import { useCallback, useEffect, useState } from "react";
import ApiKeyManager from "./components/ApiKeyManager";
import CacheChart from "./components/CacheChart";
import RateLimitPanel from "./components/RateLimitPanel";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:48080/v1";

type Tab = "cache" | "rate-limits" | "api-keys";

interface GatewayStats {
  cache: { hits: number; misses: number; total: number; hit_rate_pct: number };
  rate_limit: { rpm: number; window_seconds: number };
}

interface ApiKeyItem {
  id: string;
  name: string;
  prefix: string;
  created_at: string;
}

export default function GatewayPage() {
  const [tab, setTab] = useState<Tab>("cache");
  const [stats, setStats] = useState<GatewayStats | null>(null);
  const [keys, setKeys] = useState<ApiKeyItem[]>([]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/gateway/stats`);
      if (res.ok) setStats(await res.json());
    } catch {
      // silently skip
    }
  }, []);

  const fetchKeys = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/gateway/keys`);
      if (res.ok) setKeys(await res.json());
    } catch {
      // silently skip
    }
  }, []);

  useEffect(() => {
    fetchStats();
    // Refresh cache stats every 15 seconds
    const id = setInterval(fetchStats, 15_000);
    return () => clearInterval(id);
  }, [fetchStats]);

  useEffect(() => {
    if (tab === "api-keys") fetchKeys();
  }, [tab, fetchKeys]);

  const tabs: { id: Tab; label: string }[] = [
    { id: "cache", label: "Cache" },
    { id: "rate-limits", label: "Rate Limits" },
    { id: "api-keys", label: "API Keys" },
  ];

  return (
    <main className="min-h-screen bg-forge-bg text-forge-text p-6">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-bold">API Gateway</h1>
          <p className="text-sm text-forge-text/50 mt-1">
            Semantic cache performance, rate-limit configuration, and API key management.
          </p>
        </div>

        {/* Tab bar */}
        <div className="flex gap-1 border-b border-white/10">
          {tabs.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                tab === id
                  ? "bg-white/10 text-forge-text border-b-2 border-forge-accent"
                  : "text-forge-text/50 hover:text-forge-text"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Cache tab */}
        {tab === "cache" && (
          <div className="flex flex-col gap-4">
            {stats ? (
              <CacheChart stats={stats.cache} />
            ) : (
              <p className="text-forge-text/40 text-sm">Loading cache stats…</p>
            )}
          </div>
        )}

        {/* Rate limits tab */}
        {tab === "rate-limits" && (
          <div>
            {stats ? (
              <RateLimitPanel config={stats.rate_limit} />
            ) : (
              <p className="text-forge-text/40 text-sm">Loading rate-limit config…</p>
            )}
          </div>
        )}

        {/* API keys tab */}
        {tab === "api-keys" && (
          <ApiKeyManager keys={keys} onChanged={fetchKeys} />
        )}
      </div>
    </main>
  );
}
