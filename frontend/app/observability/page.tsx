"use client";

import { useCallback, useEffect, useState } from "react";
import EvalRunner from "./components/EvalRunner";
import EvalScorecard from "./components/EvalScorecard";
import GrafanaEmbed from "./components/GrafanaEmbed";
import LangFuseEmbed from "./components/LangFuseEmbed";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:48080/v1";

type Tab = "metrics" | "traces" | "evaluation";

interface EvalRun {
  id: string;
  dataset_name: string;
  row_count: number;
  status: string;
  faithfulness: number | null;
  answer_relevancy: number | null;
  context_precision: number | null;
  context_recall: number | null;
  created_at: string;
  error?: string | null;
}

export default function ObservabilityPage() {
  const [tab, setTab] = useState<Tab>("metrics");
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [polling, setPolling] = useState(false);

  const fetchRuns = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/eval/results`);
      if (res.ok) setRuns(await res.json());
    } catch {
      // silently skip on network error
    }
  }, []);

  useEffect(() => {
    if (tab === "evaluation") {
      fetchRuns();
    }
  }, [tab, fetchRuns]);

  // Poll every 5 seconds when there are running evaluations
  useEffect(() => {
    const hasRunning = runs.some((r) => r.status === "running");
    if (hasRunning && !polling) {
      setPolling(true);
      const id = setInterval(fetchRuns, 5000);
      return () => {
        clearInterval(id);
        setPolling(false);
      };
    }
  }, [runs, polling, fetchRuns]);

  const tabs: { id: Tab; label: string }[] = [
    { id: "metrics", label: "Metrics" },
    { id: "traces", label: "Traces" },
    { id: "evaluation", label: "Evaluation" },
  ];

  return (
    <main className="min-h-screen bg-forge-bg text-forge-text p-6">
      <div className="max-w-7xl mx-auto flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-bold">Observability</h1>
          <p className="text-sm text-forge-text/50 mt-1">
            Real-time metrics, distributed traces, and RAG quality evaluation.
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

        {/* Metrics tab */}
        {tab === "metrics" && (
          <div className="flex flex-col gap-6">
            <GrafanaEmbed uid="genai-forge-api" title="System Health" />
            <GrafanaEmbed uid="genai-forge-llm" title="AI Quality" />
          </div>
        )}

        {/* Traces tab */}
        {tab === "traces" && (
          <div>
            <LangFuseEmbed />
          </div>
        )}

        {/* Evaluation tab */}
        {tab === "evaluation" && (
          <div className="flex flex-col gap-6">
            <EvalRunner onRunStarted={fetchRuns} />
            <EvalScorecard runs={runs} />
          </div>
        )}
      </div>
    </main>
  );
}
