import { create } from "zustand";

export interface Source {
  chunk: string;
  score: number;
  doc: string | null;
  page: number | string | null;
  document_id?: string;
}

export interface QuerySession {
  id: string;
  query: string;
  model: string;
  collectionId: string;
  response: string;
  sources: Source[];
  cacheHit: boolean;
  latencyMs: number | null;
  streaming: boolean;
}

interface PlaygroundStore {
  sessions: QuerySession[];
  activeSessionId: string | null;
  collections: { id: string; name: string }[];
  selectedModel: string;
  setSelectedModel: (m: string) => void;
  setCollections: (c: { id: string; name: string }[]) => void;
  startSession: (query: string, collectionId: string, model: string) => string;
  appendChunk: (id: string, chunk: string) => void;
  addSource: (id: string, source: Source) => void;
  finalizeSession: (id: string, latencyMs: number, cacheHit: boolean) => void;
  setActiveSession: (id: string) => void;
  resetPlayground: () => void;
}

export const usePlaygroundStore = create<PlaygroundStore>((set) => ({
  sessions: [],
  activeSessionId: null,
  collections: [],
  selectedModel: "gpt-4o-mini",

  setSelectedModel: (m) => set({ selectedModel: m }),
  setCollections: (c) => set({ collections: c }),

  startSession: (query, collectionId, model) => {
    const id = crypto.randomUUID();
    set((s) => ({
      sessions: [
        ...s.sessions,
        { id, query, collectionId, model, response: "", sources: [], cacheHit: false, latencyMs: null, streaming: true },
      ],
      activeSessionId: id,
    }));
    return id;
  },

  appendChunk: (id, chunk) =>
    set((s) => ({
      sessions: s.sessions.map((sess) => (sess.id === id ? { ...sess, response: sess.response + chunk } : sess)),
    })),

  addSource: (id, source) =>
    set((s) => ({
      sessions: s.sessions.map((sess) => (sess.id === id ? { ...sess, sources: [...sess.sources, source] } : sess)),
    })),

  finalizeSession: (id, latencyMs, cacheHit) =>
    set((s) => ({
      sessions: s.sessions.map((sess) => (sess.id === id ? { ...sess, latencyMs, cacheHit, streaming: false } : sess)),
    })),

  setActiveSession: (id) => set({ activeSessionId: id }),
  resetPlayground: () => set({ sessions: [], activeSessionId: null }),
}));

// ── Agent Board store ──────────────────────────────────────────────────────

export type NodeStatus = "idle" | "running" | "done" | "paused" | "error";

export interface AgentNodeState {
  id: string;
  label: string;
  status: NodeStatus;
}

export interface AgentJob {
  jobId: string;
  backendJobId?: string;
  type: "research" | "code-review";
  status: "running" | "awaiting_human" | "complete" | "error";
  nodes: AgentNodeState[];
  report: string;
  pendingReview?: { analysis: string; security_issues: string[]; suggestions: string[] };
}

interface AgentBoardStore {
  jobs: AgentJob[];
  activeJobId: string | null;
  addJob: (job: AgentJob) => void;
  updateNodeStatus: (jobId: string, nodeId: string, status: NodeStatus) => void;
  setJobStatus: (jobId: string, status: AgentJob["status"]) => void;
  setPendingReview: (jobId: string, review: AgentJob["pendingReview"]) => void;
  setBackendJobId: (jobId: string, backendJobId: string) => void;
  setReport: (jobId: string, report: string) => void;
  setActiveJob: (id: string) => void;
}

export const useAgentBoardStore = create<AgentBoardStore>((set) => ({
  jobs: [],
  activeJobId: null,

  addJob: (job) => set((s) => ({ jobs: [...s.jobs, job], activeJobId: job.jobId })),

  updateNodeStatus: (jobId, nodeId, status) =>
    set((s) => ({
      jobs: s.jobs.map((j) =>
        j.jobId === jobId
          ? { ...j, nodes: j.nodes.map((n) => (n.id === nodeId ? { ...n, status } : n)) }
          : j
      ),
    })),

  setJobStatus: (jobId, status) =>
    set((s) => ({ jobs: s.jobs.map((j) => (j.jobId === jobId ? { ...j, status } : j)) })),

  setPendingReview: (jobId, review) =>
    set((s) => ({ jobs: s.jobs.map((j) => (j.jobId === jobId ? { ...j, pendingReview: review } : j)) })),

  setBackendJobId: (jobId, backendJobId) =>
    set((s) => ({ jobs: s.jobs.map((j) => (j.jobId === jobId ? { ...j, backendJobId } : j)) })),

  setReport: (jobId, report) =>
    set((s) => ({ jobs: s.jobs.map((j) => (j.jobId === jobId ? { ...j, report } : j)) })),

  setActiveJob: (id) => set({ activeJobId: id }),
}));
