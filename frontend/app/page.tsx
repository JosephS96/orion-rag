"use client";

import { useState, useEffect, useCallback } from "react";
import SearchBar from "@/components/SearchBar";
import ModeToggle from "@/components/ModeToggle";
import AnswerPanel from "@/components/AnswerPanel";
import SourceCard from "@/components/SourceCard";
import ThinkingTrace from "@/components/ThinkingTrace";
import DocumentManager from "@/components/DocumentManager";
import {
  fetchHealth,
  runSimpleQuery,
  streamResearch,
  Citation,
  ResearchStep,
} from "@/lib/api";

type Mode = "simple" | "deep";

export default function Home() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<Mode>("simple");
  const [provider, setProvider] = useState<string>("");
  const [providers, setProviders] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [steps, setSteps] = useState<ResearchStep[]>([]);
  const [docsOpen, setDocsOpen] = useState(false);
  const [collections, setCollections] = useState<string[]>(["bundled"]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth()
      .then((h) => {
        setProviders(h.providers);
        const first = Object.keys(h.providers)[0];
        if (first) setProvider(first);
      })
      .catch(() => setError("Cannot reach backend. Is it running?"));

    const saved = localStorage.getItem("rag-mode");
    if (saved === "simple" || saved === "deep") setMode(saved);
  }, []);

  const handleModeChange = (m: Mode) => {
    setMode(m);
    localStorage.setItem("rag-mode", m);
  };

  const handleSearch = useCallback(async () => {
    if (!query.trim() || !provider || loading) return;
    setLoading(true);
    setAnswer("");
    setCitations([]);
    setSteps([]);
    setError(null);

    try {
      if (mode === "simple") {
        const result = await runSimpleQuery(query, provider, null, collections);
        setAnswer(result.answer);
        setCitations(result.citations);
      } else {
        for await (const step of streamResearch(query, provider, null, collections)) {
          setSteps((prev) => [...prev, step]);
          if (step.step === "final") {
            const data = step.data as { answer: string; citations: Citation[] };
            setAnswer(data.answer);
            setCitations(data.citations);
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }, [query, provider, mode, collections, loading]);

  const hasUserDocs = collections.includes("user");

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-gray-900">🚀 Orion RAG</span>
        </div>
        <div className="flex items-center gap-3">
          {/* Collection toggle */}
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={hasUserDocs}
              onChange={(e) =>
                setCollections(
                  e.target.checked ? ["bundled", "user"] : ["bundled"]
                )
              }
              className="rounded text-indigo-600"
            />
            Include my docs
          </label>

          {/* Provider selector */}
          {Object.keys(providers).length > 0 && (
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="text-sm border border-gray-200 rounded-lg px-2 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {Object.entries(providers).map(([p, m]) => (
                <option key={p} value={p}>
                  {p.charAt(0).toUpperCase() + p.slice(1)} — {m}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={() => setDocsOpen(true)}
            className="flex items-center gap-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            My Docs
          </button>

          <ModeToggle mode={mode} onChange={handleModeChange} />
        </div>
      </header>

      {/* Search area */}
      <div className="flex flex-col items-center pt-16 pb-8 px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 text-center">
          Ask about space exploration
        </h1>
        <p className="text-gray-500 mb-8 text-center text-sm">
          Powered by {Object.keys(providers).length > 0 ? "your API key" : "—"} ·{" "}
          {mode === "deep" ? "Deep Research mode" : "Simple RAG mode"}
        </p>
        <SearchBar
          value={query}
          onChange={setQuery}
          onSubmit={handleSearch}
          loading={loading}
        />
        {error && (
          <p className="mt-3 text-sm text-red-500 text-center">{error}</p>
        )}
      </div>

      {/* Results */}
      {(answer || steps.length > 0 || loading) && (
        <div className="flex flex-col items-center gap-5 px-4 pb-16">
          {mode === "deep" && (
            <ThinkingTrace steps={steps} loading={loading && steps.length > 0} />
          )}

          {answer && <AnswerPanel answer={answer} citations={citations} />}

          {citations.length > 0 && (
            <div className="w-full max-w-3xl">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
                Sources
              </p>
              <div className="flex gap-3 overflow-x-auto pb-2">
                {citations.map((c) => (
                  <SourceCard key={c.id} citation={c} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <DocumentManager open={docsOpen} onClose={() => setDocsOpen(false)} />
    </main>
  );
}
