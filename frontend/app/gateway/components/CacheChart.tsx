"use client";

interface CacheStats {
  hits: number;
  misses: number;
  total: number;
  hit_rate_pct: number;
}

interface Props {
  stats: CacheStats;
}

export default function CacheChart({ stats }: Props) {
  const { hits, misses, total, hit_rate_pct } = stats;
  const hitPct = total > 0 ? (hits / total) * 100 : 0;
  const missPct = 100 - hitPct;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-5 flex flex-col gap-4">
      <h3 className="font-semibold text-forge-text">Semantic Cache Performance</h3>

      {/* Donut-style bar */}
      <div className="flex h-6 rounded-full overflow-hidden border border-white/10">
        <div
          className="bg-green-500 transition-all"
          style={{ width: `${hitPct}%` }}
          title={`Hits: ${hits}`}
        />
        <div
          className="bg-red-500/60 transition-all"
          style={{ width: `${missPct}%` }}
          title={`Misses: ${misses}`}
        />
      </div>

      {/* Legend */}
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-white/5 p-3">
          <p className="text-2xl font-bold text-green-400">{hits.toLocaleString()}</p>
          <p className="text-xs text-forge-text/50">Cache Hits</p>
        </div>
        <div className="rounded-lg bg-white/5 p-3">
          <p className="text-2xl font-bold text-red-400">{misses.toLocaleString()}</p>
          <p className="text-xs text-forge-text/50">Cache Misses</p>
        </div>
        <div className="rounded-lg bg-white/5 p-3">
          <p className="text-2xl font-bold text-forge-accent">{hit_rate_pct.toFixed(1)}%</p>
          <p className="text-xs text-forge-text/50">Hit Rate</p>
        </div>
      </div>
    </div>
  );
}
