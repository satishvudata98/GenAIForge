"use client";

import { usePlaygroundStore } from "@/lib/store";
import SourceCard from "./SourceCard";

export default function ResponseStream({ sessionId }: { sessionId: string }) {
  const session = usePlaygroundStore((s) => s.sessions.find((sess) => sess.id === sessionId));

  if (!session) return null;

  return (
    <div className="flex flex-col gap-4">
      {/* Response text */}
      <div className="rounded-2xl border border-forge-border bg-forge-surface p-4 min-h-[120px]">
        <div className="mb-2 flex items-center gap-2 text-xs text-forge-muted">
          <span className="font-mono">{session.model}</span>
          {session.cacheHit && (
            <span className="rounded-full bg-green-100 px-2 py-0.5 text-green-700 font-medium">
              Cache HIT
            </span>
          )}
          {session.latencyMs != null && (
            <span className="ml-auto">{session.latencyMs}ms</span>
          )}
          {session.streaming && (
            <span className="ml-auto animate-pulse text-forge-accent">●</span>
          )}
        </div>
        <p className="whitespace-pre-wrap leading-relaxed text-forge-text">
          {session.response}
          {session.streaming && <span className="animate-pulse">▍</span>}
        </p>
      </div>

      {/* Sources */}
      {session.sources.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-forge-muted">
            Sources ({session.sources.length})
          </p>
          <div className="grid gap-2 sm:grid-cols-2">
            {session.sources.map((src, i) => (
              <SourceCard key={i} source={src} index={i} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
