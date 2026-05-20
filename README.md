# Simple RAG

A full-stack RAG (Retrieval-Augmented Generation) pipeline with two modes, a Glean-inspired UI, and support for multiple LLM providers.

## Modes

**Simple RAG** — standard pipeline: embed query → similarity search → LLM answer with inline citations.

**Deep Research** — agentic pipeline powered by LangGraph:
1. Decomposes the question into sub-queries
2. Retrieves passages for each sub-query in parallel
3. Synthesizes a draft answer
4. Reflects on confidence — re-queries if needed
5. Streams each step to the UI in real time

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python |
| LLM routing | LiteLLM (OpenAI, Anthropic, Gemini, Mistral) |
| Agentic loop | LangGraph |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, local) |
| Vectorstore | ChromaDB (persistent, named collections) |
| Document parsing | pypdf, python-docx |
| Frontend | Next.js 14 + Tailwind CSS |

## Setup

### 1. Clone and configure

```bash
git clone https://github.com/your-username/orion-rag.git
cd orion-rag
cp .env.example .env
```

Edit `.env` and add at least one API key:

```
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
# or
GEMINI_API_KEY=...
# or
MISTRAL_API_KEY=...
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

### 3. Run locally (without Docker)

**Backend:**
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## Bundled Corpus

The backend ships with 15 Wikipedia articles on space exploration (Apollo program, ISS, Mars rovers, SpaceX, Hubble, Voyager, and more). These are automatically indexed into ChromaDB on first startup.

## Adding Your Own Documents

Click **My Docs** in the top-right corner to upload PDF, DOCX, TXT, or Markdown files. Toggle **Include my docs** in the search bar to include them in retrieval.

## Project Structure

```
orion-rag/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── config/settings.py         # Pydantic settings, provider config
│   ├── rag/
│   │   ├── embeddings.py          # sentence-transformers
│   │   ├── vectorstore.py         # ChromaDB collections
│   │   ├── loader.py              # PDF/DOCX/TXT/MD parsing
│   │   ├── retriever.py           # Similarity search
│   │   ├── simple_chain.py        # Simple RAG pipeline
│   │   └── deep_research/
│   │       ├── graph.py           # LangGraph StateGraph
│   │       ├── nodes.py           # decompose/retrieve/synthesize/reflect
│   │       └── tools.py           # vectorstore search tool
│   ├── api/routes/                # FastAPI route handlers
│   └── data/corpus/               # Bundled Wikipedia articles
├── frontend/
│   ├── app/page.tsx               # Main search page
│   └── components/                # SearchBar, AnswerPanel, ThinkingTrace, ...
├── docker-compose.yml
└── .env.example
```
