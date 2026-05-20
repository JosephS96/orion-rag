"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";
import { Citation } from "@/lib/api";

interface AnswerPanelProps {
  answer: string;
  citations: Citation[];
}

function CitationBadge({ id, citation }: { id: number; citation: Citation }) {
  return (
    <a
      href={`#source-${id}`}
      onClick={(e) => {
        e.preventDefault();
        document.getElementById(`source-${id}`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }}
      className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold no-underline hover:bg-indigo-200 transition-colors align-middle mx-0.5 cursor-pointer"
      title={citation.title}
    >
      {id}
    </a>
  );
}

function injectCitations(text: string, citations: Citation[]): React.ReactNode[] {
  const parts = text.split(/(\[\d+\])/g);
  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/);
    if (match) {
      const id = parseInt(match[1]);
      const citation = citations.find((c) => c.id === id);
      if (citation) return <CitationBadge key={i} id={id} citation={citation} />;
    }
    return part;
  });
}

// Walk React children: inject citations into plain text strings, leave elements untouched.
function withCitations(children: React.ReactNode, citations: Citation[]): React.ReactNode {
  return React.Children.map(children, (child) => {
    if (typeof child === "string") return injectCitations(child, citations);
    return child;
  });
}

export default function AnswerPanel({ answer, citations }: AnswerPanelProps) {
  if (!answer) return null;

  const components: Components = {
    p: ({ children }) => (
      <p className="mb-3 last:mb-0 leading-relaxed">
        {withCitations(children, citations)}
      </p>
    ),
    li: ({ children }) => (
      <li className="mb-1">{withCitations(children, citations)}</li>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-gray-900">{children}</strong>
    ),
    h1: ({ children }) => <h1 className="text-xl font-bold mt-4 mb-2 text-gray-900">{children}</h1>,
    h2: ({ children }) => <h2 className="text-lg font-bold mt-4 mb-2 text-gray-900">{children}</h2>,
    h3: ({ children }) => <h3 className="text-base font-semibold mt-3 mb-1 text-gray-800">{children}</h3>,
    ul: ({ children }) => <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>,
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-indigo-200 pl-4 italic text-gray-600 my-3">{children}</blockquote>
    ),
  };

  return (
    <div className="w-full max-w-3xl bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4 text-sm font-semibold text-gray-500 uppercase tracking-wide">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        Answer
      </div>
      <div className="text-gray-800 text-base">
        <ReactMarkdown components={components}>{answer}</ReactMarkdown>
      </div>
    </div>
  );
}
