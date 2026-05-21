"use client";

const LANGFUSE_BASE =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:43012`
    : "http://localhost:43012";

export default function LangFuseEmbed() {
  const src = `${LANGFUSE_BASE}/traces`;
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-sm font-semibold text-forge-text/70 uppercase tracking-widest">
        LangFuse — Live Traces
      </h3>
      <iframe
        src={src}
        title="LangFuse Traces"
        className="w-full rounded-lg border border-white/10"
        style={{ height: 480 }}
        allow="fullscreen"
      />
    </div>
  );
}
