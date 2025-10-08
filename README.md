# RAG Assistant — Conversation‑Aware, Memory‑Efficient Chatbot (CLI + Gradio)

A production‑ready Retrieval‑Augmented Generation (RAG) assistant that:
- Talks via **CLI** or **Gradio**
- Uses a **vector DB** for document retrieval
- Maintains **token‑bounded memory** via rolling summarization
- Provides **structured logging** (rotating logs + JSONL traces)
- Shows **debug panels** (retrieved **Context** + summarized **Memory**) in the UI

---

## Key Features
- **Multi‑provider LLMs**: OpenAI, Groq, or Google Gemini (auto‑selects by available API key)
- **RAG pipeline**: `VectorDB` (MiniLM embeddings) → prompt → LLM
- **Consistent memory**: `MemoryManager` keeps a short recent window + a running summary (compact & persisted)
- **Secure prompt discipline**: Answers grounded in Context; Memory used for conversational continuity; graceful “I don’t know.”
- **Observability**: Human‑readable logs and machine‑readable JSONL traces
- **Developer UI**: Gradio app with live **Context** and **Memory** panes for instant debugging

---

## Architecture
```
app/
├─ app.py                 # CLI entry (baseline)
├─ app_gradio.py          # Gradio UI (chat + debug panels)
├─ memory_utils.py        # Rolling summary memory (persisted + recent window)
├─ log_utils.py           # Logger + JSONL trace writer
├─ vectordb.py            # Simple vector DB wrapper (add/search)
├─ file_utils.py          # load_all_publications(), load_yaml_config()
├─ prompt_builder.py      # build_prompt_from_config()
├─ paths.py               # PROMPT_CONFIG_FPATH, OUTPUTS_DIR, etc.
```

---

## Requirements
- Python 3.10+ (3.11 recommended)
- Dependencies (excerpt): `langchain-core`, `langchain-openai`/`langchain-groq`/`langchain-google-genai`, `sentence-transformers`, `chromadb`, `python-dotenv`, `gradio`

---

## Quick Start

### 1) Clone & install
```bash
git clone <your-repo-url>
cd llm-rag/app

# (recommended) create a venv/conda env, then:
pip install -r requirements.txt
# If on Windows + conda:
# conda install -c conda-forge orjson
```

### 2) Configure environment
Create `.env` at project root:
```env
# choose one provider (assistant auto-detects in this order)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# or GROQ
# GROQ_API_KEY=...
# GROQ_MODEL=llama-3.1-8b-instant

# or Google
# GOOGLE_API_KEY=...
# GOOGLE_MODEL=gemini-2.0-flash
---
```

## Run (CLI)
```bash
python app.py
# Enter a question or 'quit' to exit:
```

## Run (Gradio UI)
```bash
python app_gradio.py
# open the printed local URL (default http://127.0.0.1:7860)
```

**UI Panels**
- **Chat**: conversation with the agent
- **Retrieved Context (debug)**: exact chunks passed to the LLM
- **Summarized Memory (debug)**: running summary + recent turns

---

## How Memory Works
- **Recent window**: keeps the last N turns verbatim (default 12)
- **Running summary**: compact, bullet‑style brief maintained every `SUMMARIZE_EVERY_N` turns
- **Persists to disk**: stored under `OUTPUTS_DIR/memory/memory_summary.json`
- **Token‑safe**: prompt includes both the running summary and a small recent slice

---

## Logging & Tracing
- **Text log**: `outputs/rag_assistant.log` (rotating file handler)
- **JSONL traces**: `outputs/rag_assistant_traces.jsonl` (CLI) and `outputs/rag_assistant_ui_traces.jsonl` (UI)

Each trace includes timestamps, doc counts, memory excerpts, and answer snippets for easy offline debugging.

---

## Prompt Design (YAML)
The system prompt is **conversation‑aware**:
- Use **Memory** for meta/continuity (e.g., “What did I just ask?”, “Summarize our discussion”)
- Use **Context** for factual answers; if unsupported, say “I don’t know”
- Respect safety rules (no secrets, no jailbreaks, no speculative personal data)

See `config/prompt_config.yaml`.

---

## Typical Flow (Gradio)
1. User asks a question.
2. Top‑K chunks retrieved from `VectorDB`.
3. Prompt built with **Memory + Context + Question**.
4. LLM returns an answer.
5. Memory updated; summary refreshes every N turns.
6. UI displays answer + Context + Memory.

