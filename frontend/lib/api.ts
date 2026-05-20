const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Citation {
  id: number;
  title: string;
  snippet: string;
  full_text: string;
  source: string;
  score: number;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
}

export interface ResearchStep {
  step: "decompose" | "retrieve" | "synthesize" | "reflect" | "requery" | "final";
  data: unknown;
}

export interface DocumentMetadata {
  id: string;
  filename: string;
  title: string;
  chunk_count: number;
  uploaded_at: string;
  size_bytes: number;
}

export interface HealthResponse {
  status: string;
  providers: Record<string, string>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE_URL}/api/health`);
  return res.json();
}

export async function runSimpleQuery(
  query: string,
  provider: string,
  model: string | null,
  collections: string[]
): Promise<QueryResponse> {
  const res = await fetch(`${BASE_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, provider, model, collections }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "Query failed");
  }
  return res.json();
}

export async function* streamResearch(
  query: string,
  provider: string,
  model: string | null,
  collections: string[]
): AsyncGenerator<ResearchStep> {
  const res = await fetch(`${BASE_URL}/api/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, provider, model, collections }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "Research failed");
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          yield JSON.parse(line.slice(6)) as ResearchStep;
        } catch {
          // ignore malformed lines
        }
      }
    }
  }
}

export async function uploadDocument(file: File): Promise<DocumentMetadata> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/api/documents`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "Upload failed");
  }
  return res.json();
}

export async function listDocuments(): Promise<DocumentMetadata[]> {
  const res = await fetch(`${BASE_URL}/api/documents`);
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  await fetch(`${BASE_URL}/api/documents/${id}`, { method: "DELETE" });
}
