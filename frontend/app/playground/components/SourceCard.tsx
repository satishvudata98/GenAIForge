"use client";

import type { Source } from "@/lib/store";

export default function SourceCard({ source, index }: { source: Source; index: number }) {
  return (
    <div className="rounded-xl border border-forge-border bg-forge-surface p-3 text-sm">
      <div className="mb-1 flex items-center gap-2">
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-forge-accent/20 text-xs font-bold text-forge-accent">
          {index + 1}
        </span>
        <span className="font-medium text-forge-text truncate">{source.doc ?? "unknown"}</span>
        {source.page != null && (
          <span className="ml-auto text-xs text-forge-muted">p.{source.page}</span>
        )}
      </div>
      <p className="line-clamp-3 text-forge-muted leading-relaxed">{source.chunk}</p>
      <div className="mt-1 text-xs text-forge-muted/70">
        score: {source.score.toFixed(3)}
      </div>
    </div>
  );
}
