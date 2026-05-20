"use client";

import { useState } from "react";

interface Props {
  jobId: string;
  summary: { analysis: string; security_issues: string[]; suggestions: string[] };
  onSubmit: (feedback: string) => void;
  onClose: () => void;
}

export default function HumanInputModal({ jobId, summary, onSubmit, onClose }: Props) {
  const [feedback, setFeedback] = useState("");

  function handleApprove() {
    onSubmit("approved");
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (feedback.trim()) onSubmit(feedback.trim());
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-2xl border border-forge-border bg-forge-bg shadow-2xl p-6">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-forge-muted">Human Review Required</p>
            <h2 className="mt-0.5 text-xl font-bold text-forge-text">Code Review — Job {jobId.slice(0, 8)}</h2>
          </div>
          <button onClick={onClose} className="text-forge-muted hover:text-forge-text text-xl leading-none">×</button>
        </div>

        {/* Analysis summary */}
        <div className="mb-4 max-h-48 overflow-y-auto rounded-xl border border-forge-border bg-forge-surface p-4 text-sm">
          <p className="mb-2 font-medium text-forge-text">Analysis</p>
          <p className="text-forge-muted leading-relaxed">{summary.analysis}</p>

          {summary.security_issues.length > 0 && (
            <div className="mt-3">
              <p className="mb-1 font-medium text-red-600">Security Issues</p>
              <ul className="list-disc pl-4 space-y-0.5">
                {summary.security_issues.map((i, idx) => (
                  <li key={idx} className="text-forge-muted">{i}</li>
                ))}
              </ul>
            </div>
          )}

          {summary.suggestions.length > 0 && (
            <div className="mt-3">
              <p className="mb-1 font-medium text-forge-text">Suggestions</p>
              <ul className="list-disc pl-4 space-y-0.5">
                {summary.suggestions.map((s, idx) => (
                  <li key={idx} className="text-forge-muted">{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Feedback form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Optional: provide additional feedback or corrections…"
            rows={3}
            className="w-full resize-none rounded-xl border border-forge-border bg-forge-surface px-4 py-3 text-sm text-forge-text placeholder:text-forge-muted/60 outline-none focus:border-forge-accent/50"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleApprove}
              className="flex-1 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-semibold text-white hover:opacity-90 transition"
            >
              Approve & Continue
            </button>
            <button
              type="submit"
              disabled={!feedback.trim()}
              className="flex-1 rounded-xl bg-forge-accent px-4 py-2.5 text-sm font-semibold text-white hover:opacity-90 transition disabled:opacity-40"
            >
              Submit Feedback
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
