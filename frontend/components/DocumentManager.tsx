"use client";

import { useState, useEffect, useRef } from "react";
import {
  listDocuments,
  uploadDocument,
  deleteDocument,
  DocumentMetadata,
} from "@/lib/api";

interface DocumentManagerProps {
  open: boolean;
  onClose: () => void;
}

export default function DocumentManager({ open, onClose }: DocumentManagerProps) {
  const [docs, setDocs] = useState<DocumentMetadata[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) loadDocs();
  }, [open]);

  async function loadDocs() {
    try {
      setDocs(await listDocuments());
    } catch {
      setError("Failed to load documents.");
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      await loadDocs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteDocument(id);
      setDocs((d) => d.filter((doc) => doc.id !== id));
    } catch {
      setError("Failed to delete document.");
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/30" onClick={onClose} />
      <div className="w-96 bg-white shadow-2xl flex flex-col h-full">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h2 className="text-base font-semibold text-gray-900">Your Documents</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-5 border-b">
          <label
            className={`flex flex-col items-center justify-center w-full h-28 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
              uploading
                ? "border-indigo-300 bg-indigo-50"
                : "border-gray-200 hover:border-indigo-300 hover:bg-indigo-50"
            }`}
          >
            {uploading ? (
              <span className="text-sm text-indigo-500 animate-pulse">Uploading...</span>
            ) : (
              <>
                <svg className="w-8 h-8 text-gray-400 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span className="text-sm text-gray-500">Drop a file or click to upload</span>
                <span className="text-xs text-gray-400 mt-0.5">PDF, DOCX, TXT, MD</span>
              </>
            )}
            <input
              ref={fileRef}
              type="file"
              className="hidden"
              accept=".pdf,.docx,.txt,.md"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
          {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          {docs.length === 0 ? (
            <p className="text-sm text-gray-400 text-center mt-8">No documents uploaded yet.</p>
          ) : (
            docs.map((doc) => (
              <div key={doc.id} className="flex items-start justify-between gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{doc.filename}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {doc.chunk_count} chunks · {(doc.size_bytes / 1024).toFixed(1)} KB
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="flex-shrink-0 text-gray-300 hover:text-red-400 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
