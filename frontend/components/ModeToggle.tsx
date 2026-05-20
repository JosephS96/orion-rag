"use client";

interface ModeToggleProps {
  mode: "simple" | "deep";
  onChange: (mode: "simple" | "deep") => void;
}

export default function ModeToggle({ mode, onChange }: ModeToggleProps) {
  return (
    <div className="flex items-center gap-1 bg-gray-100 rounded-full p-1 text-sm font-medium">
      <button
        onClick={() => onChange("simple")}
        className={`px-3 py-1 rounded-full transition-all ${
          mode === "simple"
            ? "bg-white text-gray-900 shadow-sm"
            : "text-gray-500 hover:text-gray-700"
        }`}
      >
        Simple RAG
      </button>
      <button
        onClick={() => onChange("deep")}
        className={`px-3 py-1 rounded-full transition-all flex items-center gap-1.5 ${
          mode === "deep"
            ? "bg-white text-indigo-600 shadow-sm"
            : "text-gray-500 hover:text-gray-700"
        }`}
      >
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            mode === "deep" ? "bg-indigo-500 animate-pulse" : "bg-gray-400"
          }`}
        />
        Deep Research
      </button>
    </div>
  );
}
