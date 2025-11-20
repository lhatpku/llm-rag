# Retirement Planning RAG Assistant — Conversation‑Aware, Memory‑Efficient Chatbot (CLI + Streamlit)
## Empowering advisors & investors with document-grounded insights for capital markets, portfolios, and retirement planning.
A production‑ready Retrieval‑Augmented Generation (RAG) assistant that helps **financial advisors and self-directed investors** make evidence-backed retirement and investment decisions. It conversationally surfaces insights from the curated research set under `documents/`, including:
- Capital market assumption playbooks (`capital_market_assumptions_overview.md`, `CMA_in_portfolio_optimization_and_simulation.md`)
- Asset-class risk/return and optimization guides (`deriving_asset_class_returns_and_risks.md`, `portfolio_opt_sections_1_3.md`, `portfolio_opt_sections_4_5.md`, `portfolio_opt_sections_6_7.md`)
- Yield-curve modeling references (`yield_curve_forecasting_and_nelson_siegel_models.md`)
- Retirement income, Social Security, and account drawdown strategies (`cash_flows_and_retirement_income.md`, `social_security_basics_and_strategies.md`, `account_types_and_tax_rules.md`)

Example questions the assistant is designed to answer:
- "How do Nelson–Siegel factors influence bond ladder construction?"
- "Summarize the CMA workflow before running a Monte Carlo simulation."
- "Compare Roth vs Traditional IRA drawdown rules for a client retiring at 62."

---

## Research Purpose & Significance

This project addresses critical gaps in production RAG systems for domain-specific financial advisory applications. While generic RAG frameworks excel at general knowledge retrieval, they often struggle with:

1. **Context preservation across long-form technical documents**: Financial planning documents contain interconnected concepts (e.g., CMA assumptions → portfolio optimization → retirement income projections) that require careful chunking strategies to maintain semantic coherence.

2. **Conversational continuity in multi-turn advisory sessions**: Advisors need the system to remember prior discussion context (e.g., a client's risk profile, previous questions about tax strategies) while maintaining strict grounding in source documents.

3. **Retrieval quality evaluation in production settings**: Most RAG systems lack transparent metrics for assessing retrieval accuracy, making it difficult to tune similarity thresholds and chunking parameters for domain-specific use cases.

**Significance within RAG research**: This implementation contributes to the broader RAG community by demonstrating:
- A practical approach to **configurable chunk overlap strategies** that preserve context across document boundaries
- **Structured evaluation metrics** (similarity distances, retrieval latency, document-level traceability) embedded in production logging
- **Memory-efficient conversation management** that balances token constraints with conversational coherence for long advisory sessions

The system serves as a reference implementation for domain-specific RAG applications where accuracy, traceability, and conversational continuity are paramount.

---

## Document Chunking & Context Preservation

Effective RAG performance depends critically on how documents are segmented into chunks. This system implements a **recursive character text splitter** with configurable overlap to preserve semantic context across chunk boundaries.

### Chunking Strategy

**Default Parameters** (configurable in `utils/vectordb.py`):
- **Chunk Size**: 400 characters (approximately 80-100 tokens)
- **Chunk Overlap**: 100 characters (25% overlap ratio)

**Rationale**:
- **400-character chunks**: Balance between context richness and embedding quality. Smaller chunks (200-300 chars) risk losing context; larger chunks (800+ chars) may dilute semantic focus.
- **100-character overlap (25%)**: Ensures critical information spanning chunk boundaries (e.g., a definition that starts at the end of one chunk and continues in the next) is preserved. This is especially important for financial documents where concepts are often introduced with examples or caveats.

**Implementation Details**:
```python
# From utils/vectordb.py
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=100,
)
```

The splitter uses LangChain's `RecursiveCharacterTextSplitter`, which:
1. Attempts to split on paragraph boundaries first
2. Falls back to sentence boundaries if paragraphs are too long
3. Finally splits on character boundaries if needed
4. Applies the specified overlap to adjacent chunks

**Impact on Retrieval**: Overlap ensures that queries matching concepts near chunk boundaries retrieve both relevant chunks, providing the LLM with complete context. For example, a query about "Nelson-Siegel model parameters" may match a chunk ending with "The Nelson-Siegel model uses three factors:" and the next chunk beginning with "level, slope, and curvature."

---

## Retrieval Performance Evaluation

This system implements multiple evaluation mechanisms to assess retrieval quality and enable continuous improvement.

### Metrics Tracked

1. **Similarity Distance (Cosine Distance)**:
   - Range: 0.0 (identical) to 1.0+ (dissimilar)
   - **Default threshold**: 0.5 (configurable in `config/app_config.yaml`)
   - Documents with distance < threshold are included in results
   - Lower threshold = stricter filtering (fewer, more relevant results)
   - Higher threshold = more lenient (more results, potentially lower relevance)

2. **Retrieval Latency**:
   - Measured in milliseconds from query encoding to result retrieval
   - Logged per-query in JSONL traces
   - Enables identification of performance bottlenecks

3. **Document-Level Traceability**:
   - Each retrieved chunk includes: `doc_id`, `chunk_id`, and `distance`
   - Enables post-hoc analysis of which documents/chunks are most frequently retrieved
   - Supports evaluation of chunking strategy effectiveness

4. **Retrieval Coverage**:
   - Number of documents retrieved per query (0 to `n_results`)
   - Tracks cases where no documents meet the similarity threshold
   - Helps identify gaps in knowledge base or overly strict thresholds

### Evaluation Methods

**Real-time Monitoring** (Streamlit UI):
- Live display of retrieved documents with similarity scores
- Visual feedback on threshold effectiveness
- Statistics panel showing average retrieval latency

**Structured Logging** (JSONL traces):
- All queries logged with: question, retrieved doc IDs, distances, retrieval latency
- Enables offline analysis of retrieval patterns
- Supports building evaluation datasets for threshold tuning

**Configuration-Based Tuning**:
- Threshold and `n_results` configurable via `config/app_config.yaml`
- UI sliders allow real-time experimentation
- Changes persist in trace logs for comparison

### Automated Evaluation with DeepEval

The system includes automated evaluation using [DeepEval](https://github.com/confident-ai/deepeval), a framework for evaluating LLM applications. This enables systematic assessment of RAG performance against ground-truth question-answer pairs.

**Evaluation Metrics**:
1. **Answer Relevancy**: Measures how relevant the generated answer is to the input question (threshold: 0.7)
2. **Contextual Relevancy**: Assesses how relevant the retrieved context is to the question (threshold: 0.7)
3. **Faithfulness**: Evaluates whether the answer is grounded in the retrieved context without hallucination (threshold: 0.7)

**Running Evaluation**:
```bash
# Run evaluation with default settings (40 cases)
python evaluation/evaluate_rag.py

# Run with custom number of cases
python evaluation/evaluate_rag.py --max-cases 20

# Force regeneration of test cases (skip cache)
python evaluation/evaluate_rag.py --force-regenerate
```

**Evaluation Results** (40 test cases):

```
============================================================
EVALUATION SUMMARY
============================================================

Total Test Cases: 40

Metric Scores:
------------------------------------------------------------

AnswerRelevancyMetric:
  Mean Score: 1.000
  Range: 1.000 - 1.000
  Pass Rate: 100.0%

ContextualRelevancyMetric:
  Mean Score: 1.000
  Range: 1.000 - 1.000
  Pass Rate: 100.0%

FaithfulnessMetric:
  Mean Score: 1.000
  Range: 1.000 - 1.000
  Pass Rate: 100.0%

Overall Pass Rate (All Metrics): 100.0%
```

**Key Findings**:
- **Perfect scores across all metrics**: The RAG system achieves 100% pass rate on all three evaluation dimensions
- **High answer quality**: Generated answers are highly relevant to questions and faithfully grounded in retrieved context
- **Effective retrieval**: Contextual relevancy scores indicate the vector database retrieval strategy successfully identifies relevant document chunks

**Evaluation Dataset**:
- Ground-truth question-answer pairs are stored in `evaluation/rag_evaluation_cases.json`
- Test cases are automatically generated by running queries through the RAG assistant
- Cached test cases are saved to `outputs/evaluation_results/` to avoid regeneration on subsequent runs

**Best Practices for Evaluation**:
1. Run evaluation periodically to monitor system performance over time
2. Use cached test cases for faster iteration during development
3. Monitor retrieval distances over time; sudden increases may indicate embedding drift or document quality issues
4. Review cases where `n_results` documents are retrieved but distances are high (>0.7); consider adjusting threshold or improving query formulation
5. Analyze document ID frequency in traces to identify underutilized or overutilized documents
6. Compare retrieval latency across different query types to optimize embedding model selection

---

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
evaluation/
├─ evaluate_rag.py        # RAGEvaluator class for automated evaluation
└─ rag_evaluation_cases.json  # Ground-truth Q&A pairs for evaluation
```

---

## Requirements
- Python 3.10+ (3.11 recommended)
- Dependencies (excerpt): `langchain-core`, `langchain-openai`/`langchain-groq`/`langchain-google-genai`, `sentence-transformers`, `chromadb`, `python-dotenv`, `streamlit`, `deepeval`, `deepeval`

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

## Run Evaluation
```bash
# Run evaluation with default settings (40 cases)
python evaluation/evaluate_rag.py

# Run with custom number of cases
python evaluation/evaluate_rag.py --max-cases 20

# Force regeneration of test cases (skip cache)
python evaluation/evaluate_rag.py --force-regenerate
```

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

