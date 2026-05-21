"use client";

interface RateLimitConfig {
  rpm: number;
  window_seconds: number;
}

interface Props {
  config: RateLimitConfig;
}

export default function RateLimitPanel({ config }: Props) {
  const { rpm, window_seconds } = config;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-5 flex flex-col gap-4">
      <h3 className="font-semibold text-forge-text">Rate Limiting</h3>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg bg-white/5 p-4 text-center">
          <p className="text-3xl font-bold text-forge-accent">{rpm}</p>
          <p className="text-xs text-forge-text/50 mt-1">Requests / Minute</p>
          <p className="text-xs text-forge-text/30">(per API key)</p>
        </div>
        <div className="rounded-lg bg-white/5 p-4 text-center">
          <p className="text-3xl font-bold text-forge-text">{window_seconds}s</p>
          <p className="text-xs text-forge-text/50 mt-1">Window Duration</p>
          <p className="text-xs text-forge-text/30">rolling token bucket</p>
        </div>
      </div>

      <p className="text-xs text-forge-text/40">
        Rate limits are enforced per <code className="text-forge-accent/70">X-Api-Key</code> header. Clients
        exceeding the limit receive HTTP 429 with a <code className="text-forge-accent/70">Retry-After: 60</code>{" "}
        header.
      </p>
    </div>
  );
}
