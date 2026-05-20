"use client";

import { useState } from "react";
import { ResearchStep } from "@/lib/api";

interface ThinkingTraceProps {
  steps: ResearchStep[];
  loading: boolean;
}

const STEP_LABELS: Record<string, string> = {
  decompose: "Breaking question into sub-queries",
  retrieve: "Retrieving relevant passages",
  synthesize: "Synthesizing draft answer",
  reflect: "Evaluating answer quality",
  requery: "Refining search for gaps",
  final: "Finalizing answer",
};

const STEP_ICONS: Record<string, string> = {
  decompose: "🔍",
  retrieve: "📄",
  synthesize: "✍️",
  reflect: "🤔",
  requery: "🔄",
  final: "✅",
};

function StepDetail({ step }: { step: ResearchStep }) {
  if (step.step === "decompose" && Array.isArray(step.data)) {
    return (
      <ul className="mt-1.5 space-y-1">
        {(step.data as string[]).map((q, i) => (
          <li key={i} className="text-xs text-gray-500 pl-3 border-l-2 border-indigo-200">
            {q}
          </li>
        ))}
      </ul>
    );
  }
  if (step.step === "retrieve" && Array.isArray(step.data)) {
    const data = step.data as { sub_q: string; chunk_count: number }[];
    return (
      <p className="mt-1 text-xs text-gray-500">
        Found {data.reduce((s, d) => s + d.chunk_count, 0)} unique passages across {data.length} sub-queries
      </p>
    );
  }
  if (step.step === "reflect") {
    const data = step.data as { confidence: number; requery: boolean };
    return (
      <p className="mt-1 text-xs text-gray-500">
        Confidence: {(data.confidence * 100).toFixed(0)}%
        {data.requery ? " — refining search" : " — answer is sufficient"}
      </p>
    );
  }
  if (step.step === "requery") {
    const data = step.data as { query: string; new_chunks: number };
    return (
      <p className="mt-1 text-xs text-gray-500">
        Searched: &ldquo;{data.query}&rdquo; → {data.new_chunks} new passages
      </p>
    );
  }
  return null;
}

export default function ThinkingTrace({ steps, loading }: ThinkingTraceProps) {
  const [open, setOpen] = useState(true);

  if (steps.length === 0 && !loading) return null;

  return (
    <div className="w-full max-w-3xl bg-indigo-50 rounded-xl border border-indigo-100 overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-3 text-sm font-medium text-indigo-700 hover:bg-indigo-100 transition-colors"
      >
        <span className="flex items-center gap-2">
          <span>Deep Research Trace</span>
          {loading && (
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
          )}
        </span>
        <svg
          className={`w-4 h-4 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="px-5 pb-4 space-y-3">
          {steps.map((step, i) => (
            <div key={i} className="flex gap-3">
              <div className="flex flex-col items-center">
                <span className="text-base">{STEP_ICONS[step.step] ?? "•"}</span>
                {i < steps.length - 1 && (
                  <div className="w-px flex-1 bg-indigo-200 mt-1" />
                )}
              </div>
              <div className="pb-2">
                <p className="text-sm font-medium text-indigo-800">
                  {STEP_LABELS[step.step] ?? step.step}
                </p>
                <StepDetail step={step} />
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <span className="text-base animate-pulse">⏳</span>
              <p className="text-sm text-indigo-400 animate-pulse">Working...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
