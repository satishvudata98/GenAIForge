"use client";

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

function ScoreBar({ label, value }: { label: string; value: number | null }) {
  const pct = value !== null ? Math.round(value * 100) : null;
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between text-xs text-forge-text/60">
        <span>{label}</span>
        <span className="font-mono">{pct !== null ? `${pct}%` : "—"}</span>
      </div>
      <div className="h-2 rounded-full bg-white/10 overflow-hidden">
        {pct !== null && (
          <div
            className="h-full rounded-full bg-forge-accent transition-all"
            style={{ width: `${pct}%` }}
          />
        )}
      </div>
    </div>
  );
}

interface Props {
  runs: EvalRun[];
}

export default function EvalScorecard({ runs }: Props) {
  if (runs.length === 0) {
    return (
      <p className="text-forge-text/40 text-sm text-center py-8">
        No evaluation runs yet. Upload a CSV above to start.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {runs.map((run) => (
        <div key={run.id} className="rounded-xl border border-white/10 bg-white/5 p-4 flex flex-col gap-3">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-semibold text-forge-text truncate">{run.dataset_name}</p>
              <p className="text-xs text-forge-text/40">{run.row_count} rows · {new Date(run.created_at).toLocaleString()}</p>
            </div>
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                run.status === "completed"
                  ? "bg-green-500/20 text-green-400"
                  : run.status === "error"
                  ? "bg-red-500/20 text-red-400"
                  : "bg-yellow-500/20 text-yellow-400"
              }`}
            >
              {run.status}
            </span>
          </div>

          {run.status === "error" && (
            <p className="text-xs text-red-400 bg-red-500/10 rounded p-2">{run.error}</p>
          )}

          {run.status === "completed" && (
            <div className="flex flex-col gap-2">
              <ScoreBar label="Faithfulness" value={run.faithfulness} />
              <ScoreBar label="Answer Relevancy" value={run.answer_relevancy} />
              <ScoreBar label="Context Precision" value={run.context_precision} />
              <ScoreBar label="Context Recall" value={run.context_recall} />
            </div>
          )}

          {run.status === "running" && (
            <div className="flex items-center gap-2 text-sm text-forge-text/60">
              <span className="animate-spin">⟳</span> Evaluation in progress…
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
