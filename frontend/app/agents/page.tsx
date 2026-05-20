"use client";

import { useState } from "react";
import { streamPost } from "@/lib/sse";
import { type AgentJob, type AgentNodeState, useAgentBoardStore } from "@/lib/store";
import AgentGraph from "./components/AgentGraph";
import HumanInputModal from "./components/HumanInputModal";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:48080/v1";

const RESEARCH_NODES: AgentNodeState[] = [
  { id: "plan", label: "Plan", status: "idle" },
  { id: "search", label: "Search", status: "idle" },
  { id: "extract", label: "Extract", status: "idle" },
  { id: "synthesize", label: "Synthesize", status: "idle" },
  { id: "report", label: "Report", status: "idle" },
];

const CODE_REVIEW_NODES: AgentNodeState[] = [
  { id: "analyze", label: "Analyze", status: "idle" },
  { id: "security", label: "Security", status: "idle" },
  { id: "suggest", label: "Suggest", status: "idle" },
  { id: "human_review", label: "Human Review", status: "idle" },
  { id: "finalize", label: "Finalize", status: "idle" },
];

export default function AgentBoardPage() {
  const { jobs, activeJobId, addJob, updateNodeStatus, setJobStatus, setPendingReview, setBackendJobId, setReport, setActiveJob } =
    useAgentBoardStore();
  const [query, setQuery] = useState("");
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [tab, setTab] = useState<"research" | "code-review">("research");
  const [showModal, setShowModal] = useState(false);

  const activeJob = jobs.find((j) => j.jobId === activeJobId);

  function startResearch() {
    if (!query.trim()) return;
    const jobId = crypto.randomUUID();
    const job: AgentJob = { jobId, type: "research", status: "running", nodes: [...RESEARCH_NODES], report: "" };
    addJob(job);

    streamPost(`${API_BASE}/agents/research`, { query, model: "gpt-4o-mini" }, {
      onChunk: (content) => {
        const c = content as { node?: string };
        if (c.node) updateNodeStatus(jobId, c.node, "running");
      },
      onSource: (content) => {
        const s = content as { report?: string };
        if (s.report) setReport(jobId, s.report);
        // Mark all nodes done when report arrives
        RESEARCH_NODES.forEach((n) => updateNodeStatus(jobId, n.id, "done"));
      },
      onMeta: () => setJobStatus(jobId, "complete"),
      onDone: () => setJobStatus(jobId, "complete"),
      onError: () => setJobStatus(jobId, "error"),
    });
  }

  function startCodeReview() {
    if (!code.trim()) return;
    const jobId = crypto.randomUUID();
    const job: AgentJob = { jobId, type: "code-review", status: "running", nodes: [...CODE_REVIEW_NODES], report: "" };
    addJob(job);

    streamPost(`${API_BASE}/agents/code-review`, { code, language, model: "gpt-4o-mini" }, {
      onChunk: (content) => {
        const c = content as { node?: string };
        if (c.node) updateNodeStatus(jobId, c.node, c.node === "human_review" ? "paused" : "running");
      },
      onSource: (content) => {
        const s = content as { job_id?: string; analysis?: string; security_issues?: string[]; suggestions?: string[] };
        if (s.job_id) setBackendJobId(jobId, s.job_id);
        setPendingReview(jobId, { analysis: s.analysis ?? "", security_issues: s.security_issues ?? [], suggestions: s.suggestions ?? [] });
        setJobStatus(jobId, "awaiting_human");
        setShowModal(true);
      },
      onMeta: () => {},
      onDone: () => {},
      onError: () => setJobStatus(jobId, "error"),
    });
  }

  function handleHumanFeedback(jobId: string, feedback: string) {
    setShowModal(false);
    updateNodeStatus(jobId, "human_review", "done");
    updateNodeStatus(jobId, "finalize", "running");

    const job = useAgentBoardStore.getState().jobs.find((j) => j.jobId === jobId);
    const resumeId = job?.backendJobId ?? jobId;

    fetch(`${API_BASE}/agents/resume/${resumeId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback }),
    }).then((r) => {
      if (r.ok) {
        updateNodeStatus(jobId, "finalize", "done");
        setJobStatus(jobId, "complete");
      }
    });
  }

  return (
    <main className="min-h-screen bg-forge-bg p-6">
      <div className="mx-auto w-full max-w-5xl">
        {/* Header */}
        <div className="mb-6">
          <a href="/" className="text-xs text-forge-muted hover:text-forge-accent">← Home</a>
          <h1 className="mt-1 text-3xl font-bold text-forge-text">Agent Board</h1>
          <p className="mt-1 text-sm text-forge-muted">
            Run LangGraph agents with live graph visualization and human-in-the-loop review.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
          {/* Left: controls */}
          <div className="rounded-2xl border border-forge-border bg-forge-surface/60 p-5 shadow-sm">
            {/* Tabs */}
            <div className="mb-4 flex gap-1 rounded-xl border border-forge-border p-1">
              {(["research", "code-review"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`flex-1 rounded-lg py-1.5 text-xs font-semibold transition ${
                    tab === t ? "bg-forge-accent text-white" : "text-forge-muted hover:text-forge-text"
                  }`}
                >
                  {t === "research" ? "Research Agent" : "Code Review"}
                </button>
              ))}
            </div>

            {tab === "research" ? (
              <div className="flex flex-col gap-3">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Research topic or question…"
                  rows={3}
                  className="w-full resize-none rounded-xl border border-forge-border bg-forge-surface px-4 py-3 text-sm text-forge-text placeholder:text-forge-muted/60 outline-none focus:border-forge-accent/50"
                />
                <button
                  onClick={startResearch}
                  disabled={!query.trim()}
                  className="rounded-xl bg-forge-accent px-5 py-2.5 text-sm font-semibold text-white hover:opacity-90 transition disabled:opacity-40"
                >
                  Run Research Agent
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                <div className="flex gap-2">
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="rounded-xl border border-forge-border bg-forge-surface px-3 py-2 text-sm text-forge-text outline-none"
                  >
                    {["python", "typescript", "go", "rust", "java"].map((l) => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </select>
                </div>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="Paste code here…"
                  rows={8}
                  className="w-full resize-none rounded-xl border border-forge-border bg-forge-surface px-4 py-3 font-mono text-xs text-forge-text placeholder:text-forge-muted/60 outline-none focus:border-forge-accent/50"
                />
                <button
                  onClick={startCodeReview}
                  disabled={!code.trim()}
                  className="rounded-xl bg-forge-accent px-5 py-2.5 text-sm font-semibold text-white hover:opacity-90 transition disabled:opacity-40"
                >
                  Start Code Review
                </button>
              </div>
            )}

            {/* Job list */}
            {jobs.length > 0 && (
              <div className="mt-4 border-t border-forge-border pt-4">
                <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-forge-muted">Jobs</p>
                <div className="flex flex-col gap-1">
                  {jobs.map((j) => (
                    <button
                      key={j.jobId}
                      onClick={() => setActiveJob(j.jobId)}
                      className={`flex items-center justify-between rounded-lg px-3 py-2 text-xs transition ${
                        j.jobId === activeJobId
                          ? "bg-forge-accent/10 text-forge-accent"
                          : "text-forge-muted hover:bg-forge-surface"
                      }`}
                    >
                      <span>{j.type} — {j.jobId.slice(0, 8)}</span>
                      <span className={`rounded-full px-2 py-0.5 font-medium ${
                        j.status === "complete" ? "bg-green-100 text-green-700" :
                        j.status === "awaiting_human" ? "bg-amber-100 text-amber-700" :
                        j.status === "error" ? "bg-red-100 text-red-700" : "bg-forge-accent/10 text-forge-accent"
                      }`}>{j.status}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right: graph + report */}
          <div className="flex flex-col gap-4">
            {activeJob ? (
              <>
                <div className="rounded-2xl border border-forge-border bg-forge-surface overflow-hidden">
                  <AgentGraph agentNodes={activeJob.nodes} />
                </div>
                {activeJob.report && (
                  <div className="rounded-2xl border border-forge-border bg-forge-surface p-4">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-forge-muted">Report</p>
                    <p className="whitespace-pre-wrap text-sm leading-relaxed text-forge-text">{activeJob.report}</p>
                  </div>
                )}
              </>
            ) : (
              <div className="flex h-full min-h-[300px] items-center justify-center rounded-2xl border border-dashed border-forge-border text-forge-muted text-sm">
                Run an agent to see the graph
              </div>
            )}
          </div>
        </div>
      </div>

      {/* HITL Modal */}
      {showModal && activeJob?.pendingReview && (
        <HumanInputModal
          jobId={activeJob.jobId}
          summary={activeJob.pendingReview}
          onSubmit={(fb) => handleHumanFeedback(activeJob.jobId, fb)}
          onClose={() => setShowModal(false)}
        />
      )}
    </main>
  );
}
