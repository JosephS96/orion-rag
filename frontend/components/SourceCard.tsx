"use client";

import { useState, useEffect } from "react";
import { Citation } from "@/lib/api";

interface SourceCardProps {
  citation: Citation;
}

function SourceModal({ citation, onClose }: { citation: Citation; onClose: () => void }) {
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3 px-6 py-4 border-b">
          <div className="flex items-center gap-2.5">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex items-center justify-center">
              {citation.id}
            </span>
            <div>
              <p className="font-semibold text-gray-900">{citation.title}</p>
              <p className="text-xs text-gray-400 mt-0.5">{citation.source}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors mt-0.5"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Relevance badge */}
        <div className="px-6 pt-3 pb-1">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            {(citation.score * 100).toFixed(0)}% relevance
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 min-h-0 overflow-y-auto px-6 py-4">
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
            {citation.full_text}
          </p>
        </div>
      </div>
    </div>
  );
}

export default function SourceCard({ citation }: SourceCardProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <div
        id={`source-${citation.id}`}
        onClick={() => setOpen(true)}
        className="flex-shrink-0 w-64 p-4 bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group"
      >
        <div className="flex items-start gap-2 mb-2">
          <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
            {citation.id}
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">{citation.title}</p>
            <p className="text-xs text-gray-400 truncate">{citation.source}</p>
          </div>
        </div>
        <p className="text-xs text-gray-600 line-clamp-4 leading-relaxed">{citation.snippet}</p>
        <div className="mt-2 flex items-center justify-between">
          <span className="text-xs text-gray-400">
            Relevance: {(citation.score * 100).toFixed(0)}%
          </span>
          <span className="text-xs text-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity font-medium">
            View more →
          </span>
        </div>
      </div>

      {open && <SourceModal citation={citation} onClose={() => setOpen(false)} />}
    </>
  );
}
