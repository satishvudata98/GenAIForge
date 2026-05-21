"use client";

const GRAFANA_BASE =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:43011`
    : "http://localhost:43011";

interface Props {
  uid: string;
  title: string;
}

export default function GrafanaEmbed({ uid, title }: Props) {
  const src = `${GRAFANA_BASE}/d/${uid}?orgId=1&refresh=30s&kiosk=tv`;
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-sm font-semibold text-forge-text/70 uppercase tracking-widest">{title}</h3>
      <iframe
        src={src}
        title={title}
        className="w-full rounded-lg border border-white/10"
        style={{ height: 480 }}
        allow="fullscreen"
      />
    </div>
  );
}
