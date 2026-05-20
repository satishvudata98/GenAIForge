"use client";

import { useCallback } from "react";
import {
  Background,
  Controls,
  Handle,
  type NodeProps,
  Position,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { AgentNodeState, NodeStatus } from "@/lib/store";

const STATUS_COLORS: Record<NodeStatus, string> = {
  idle: "border-forge-border bg-forge-surface text-forge-muted",
  running: "border-forge-accent bg-forge-accent/10 text-forge-accent animate-pulse",
  done: "border-green-400 bg-green-50 text-green-700",
  paused: "border-amber-400 bg-amber-50 text-amber-700",
  error: "border-red-400 bg-red-50 text-red-700",
};

function AgentNode({ data }: NodeProps) {
  const nodeData = data as { label: string; status: NodeStatus };
  return (
    <div className={`rounded-xl border-2 px-4 py-2.5 text-sm font-semibold shadow-sm transition-all ${STATUS_COLORS[nodeData.status]}`}>
      <Handle type="target" position={Position.Top} className="!bg-forge-muted" />
      {nodeData.label}
      {nodeData.status === "paused" && <span className="ml-2 text-xs">(waiting)</span>}
      <Handle type="source" position={Position.Bottom} className="!bg-forge-muted" />
    </div>
  );
}

const nodeTypes = { agentNode: AgentNode };

function buildFlowNodes(agentNodes: AgentNodeState[]): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = agentNodes.map((n, i) => ({
    id: n.id,
    type: "agentNode",
    position: { x: 180, y: i * 90 },
    data: { label: n.label, status: n.status },
  }));

  const edges: Edge[] = agentNodes.slice(0, -1).map((n, i) => ({
    id: `e${i}`,
    source: n.id,
    target: agentNodes[i + 1].id,
    animated: agentNodes[i + 1].status === "running",
    style: { stroke: "#d78e3f", strokeWidth: 2 },
  }));

  return { nodes, edges };
}

interface Props {
  agentNodes: AgentNodeState[];
}

export default function AgentGraph({ agentNodes }: Props) {
  const { nodes, edges } = buildFlowNodes(agentNodes);

  return (
    <div style={{ height: Math.max(300, agentNodes.length * 90 + 60) }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        zoomOnScroll={false}
        panOnDrag={false}
      >
        <Background color="#d78e3f" gap={24} size={1} style={{ opacity: 0.08 }} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
