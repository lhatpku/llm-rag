# Retirement Planning RAG Assistant — Conversation‑Aware, Memory‑Efficient Chatbot (CLI + Streamlit)
# Empowering advisors & investors with document-grounded insights for capital markets, portfolios, and retirement planning.
A production‑ready Retrieval‑Augmented Generation (RAG) assistant that helps **financial advisors and self-directed investors** make evidence-backed retirement and investment decisions. It conversationally surfaces insights from the curated research set under `documents/`, including:
- Capital market assumption playbooks (`capital_market_assumptions_overview.md`, `CMA_in_portfolio_optimization_and_simulation.md`)
- Asset-class risk/return and optimization guides (`deriving_asset_class_returns_and_risks.md`, `portfolio_opt_sections_1_3.md`, `portfolio_opt_sections_4_5.md`, `portfolio_opt_sections_6_7.md`)
- Yield-curve modeling references (`yield_curve_forecasting_and_nelson_siegel_models.md`)
- Retirement income, Social Security, and account drawdown strategies (`cash_flows_and_retirement_income.md`, `social_security_basics_and_strategies.md`, `account_types_and_tax_rules.md`)

Example questions the assistant is designed to answer:
- “How do Nelson–Siegel factors influence bond ladder construction?”
- “Summarize the CMA workflow before running a Monte Carlo simulation.”
- “Compare Roth vs Traditional IRA drawdown rules for a client retiring at 62.”

Core capabilities:
- Talks via **CLI** or **Streamlit**
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
- **Developer UI**: Streamlit dashboard with live **Context** and **Memory** panels for instant debugging

---

## Architecture
```
├─ app.py                 # CLI entry (baseline)
├─ app_streamlit.py       # Streamlit UI (chat + debug panels)
utils/
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
- Dependencies (excerpt): `langchain-core`, `langchain-openai`/`langchain-groq`/`langchain-google-genai`, `sentence-transformers`, `chromadb`, `python-dotenv`, `streamlit`

---

## Quick Start

### 1) Clone & install
```bash
git clone <repo-url>
cd llm-rag

pip install -r requirements.txt

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

## Run (Streamlit UI)
```bash
streamlit run app_streamlit.py
# open the printed local URL (default http://localhost:8501)
```

**UI Features**
- **Chat Interface**: Interactive conversation with the agent
- **Retrieved Context Panel**: Shows exact document chunks retrieved from vector DB with similarity scores
- **Memory State**: Displays running summary + recent conversation turns
- **Statistics**: Real-time metrics for retrieval and LLM latency

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

## Typical Flow (Streamlit)
1. User asks a question.
2. Top‑K chunks retrieved from `VectorDB`.
3. Prompt built with **Memory + Context + Question**.
4. LLM returns an answer.
5. Memory updated; summary refreshes every N turns.
6. UI displays answer + Context + Memory.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contribution & Compliance

### Contributing

Contributions are welcome! When contributing to this project:

- Follow the existing code style and architecture patterns
- Ensure all new features include appropriate logging and error handling
- Update documentation (README.md, docstrings) as needed
- Test your changes with both CLI and Streamlit interfaces

### Security & Privacy

**API Keys & Environment Variables:**
- This project requires API keys for LLM providers (OpenAI, Groq, or Google Gemini)
- **Never commit API keys or `.env` files to version control**
- Store API keys securely in your local `.env` file (which is gitignored)
- Review the `.env.example` (if provided) for required variables

**Data Handling:**
- The assistant processes documents from the `documents/` directory
- Vector embeddings and conversation memory are stored locally in `data/` and `outputs/` directories
- Logs and traces may contain query text and retrieved document excerpts
- For privacy-sensitive deployments, review and configure logging settings in `config/app_config.yaml`

**Reporting Security Issues:**
- If you discover a security vulnerability, please report it responsibly
- Do not open public issues for security concerns
- Contact the project maintainers directly with security-related information

### Compliance Notes

- This software is provided "as is" without warranty (see LICENSE)
- Users are responsible for ensuring their use complies with:
  - Terms of service of LLM providers (OpenAI, Groq, Google)
  - Data privacy regulations applicable to their jurisdiction
  - Organizational policies regarding AI/ML tool usage
- The project maintainers are not responsible for misuse of this software

