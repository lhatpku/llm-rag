# app_streamlit.py
import os

# Disable ChromaDB telemetry BEFORE any imports to avoid "capture() takes 1 positional argument but 3 were given" warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

from utils.paths import OUTPUTS_DIR, APP_CONFIG_FPATH
from utils.file_utils import load_all_publications, load_yaml_config
from utils.log_utils import get_logger, JsonlTrace, TimingContext
from app import RAGAssistant

LOGGER = get_logger("rag_assistant_ui", outputs_dir=OUTPUTS_DIR)

# Load app config for logging settings
try:
    app_config = load_yaml_config(APP_CONFIG_FPATH)
    log_config = app_config.get("logging", {})
except Exception as e:
    LOGGER.warning(f"Could not load app_config.yaml, using default logging settings: {e}")
    log_config = {}

TRACE = JsonlTrace(Path(OUTPUTS_DIR) / "rag_assistant_ui_traces.jsonl", log_config=log_config)

# Page config
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "assistant" not in st.session_state:
    st.session_state.assistant = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "retrieved_contexts" not in st.session_state:
    st.session_state.retrieved_contexts = []
if "memory_history" not in st.session_state:
    st.session_state.memory_history = []


@st.cache_resource
def get_assistant():
    """Initialize and cache the RAG assistant."""
    if st.session_state.assistant is None:
        LOGGER.info("Initializing RAGAssistant for Streamlit UI...")
        assistant = RAGAssistant()
        # Load documents once
        docs = load_all_publications()
        assistant.add_documents(docs)
        LOGGER.info(f"Docs loaded: {len(docs)}")
        st.session_state.assistant = assistant
    return st.session_state.assistant


def format_context(docs, doc_ids=None, distances=None):
    """Format retrieved documents for display."""
    if not docs:
        return "No retrieved context"
    
    formatted = []
    for i, doc in enumerate(docs):
        context_item = f"**[{i+1}]** {doc[:500]}"
        if len(doc) > 500:
            context_item += "..."
        
        # Add metadata if available
        if doc_ids and i < len(doc_ids):
            context_item += f"\n  *ID: {doc_ids[i]}*"
        if distances and i < len(distances):
            context_item += f" | *Distance: {distances[i]:.4f}*"
        
        formatted.append(context_item)
    
    return "\n\n".join(formatted)


def process_query(user_input, top_k=3, threshold=0.5):
    """Process a user query and return response with context."""
    assistant = get_assistant()
    request_id = assistant.trace_session_id[:8] + "_" + str(len(st.session_state.chat_history))
    
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    total_timer = TimingContext()
    with total_timer:
        # Retrieval with timing
        retrieval_timer = TimingContext()
        with retrieval_timer:
            retrieved = assistant.vector_db.search(query=user_input, n_results=top_k, threshold=threshold)
        retrieval_latency = retrieval_timer.get_elapsed()
        
        docs = retrieved.get("documents", []) if isinstance(retrieved, dict) else []
        doc_ids = retrieved.get("ids", []) if isinstance(retrieved, dict) else []
        distances = retrieved.get("distances", []) if isinstance(retrieved, dict) else []
        
        # Memory block for prompt
        assistant.memory.add_user_turn(user_input)
        memory_block = assistant.memory.get_memory_context()
        
        # LLM call with timing
        llm_timer = TimingContext()
        with llm_timer:
            answer = assistant.chain.invoke({
                "memory": memory_block,
                "context": "\n\n".join(f"[{i+1}] {d}" for i, d in enumerate(docs)) if docs else "",
                "question": user_input
            })
        llm_latency = llm_timer.get_elapsed()
        
        # Record assistant turn
        assistant.memory.add_assistant_turn(answer)
    
    total_latency = total_timer.get_elapsed()
    
    # Add assistant response to history
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    # Store context and memory for display
    context_info = {
        "query": user_input,
        "documents": docs,
        "doc_ids": doc_ids,
        "distances": distances,
        "threshold": threshold,
        "n_results": top_k,
        "retrieval_latency": retrieval_latency,
        "llm_latency": llm_latency,
        "total_latency": total_latency,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    st.session_state.retrieved_contexts.append(context_info)
    st.session_state.memory_history.append({
        "memory": memory_block,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Enhanced trace for debugging
    TRACE.write_enhanced_invoke(
        session_id=assistant.trace_session_id,
        request_id=request_id,
        question=user_input,
        answer=answer,
        retrieved_docs=docs,
        doc_ids=doc_ids if doc_ids else None,
        distances=distances if distances else None,
        retrieval_latency=retrieval_latency,
        llm_latency=llm_latency,
        total_latency=total_latency,
        memory_excerpt=memory_block or "",
    )
    
    return answer, context_info, memory_block


# Main UI
st.title("🤖 RAG Assistant")
st.markdown("Conversation-aware RAG assistant with document retrieval and memory management")

# Load default config values for UI
try:
    app_config_ui = load_yaml_config(APP_CONFIG_FPATH)
    vectordb_config_ui = app_config_ui.get("vectordb", {})
    default_top_k = vectordb_config_ui.get("n_results", 3)
    default_threshold_ui = vectordb_config_ui.get("threshold", 0.5)
except Exception:
    default_top_k = 3
    default_threshold_ui = 0.5

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider("Top-K Context", min_value=1, max_value=8, value=default_top_k, step=1)
    threshold = st.slider(
        "Similarity Threshold", 
        min_value=0.0, 
        max_value=1.0, 
        value=default_threshold_ui, 
        step=0.05,
        help="Lower values = more strict (fewer results), Higher values = more lenient (more results)"
    )
    
    st.header("📊 Statistics")
    if st.session_state.assistant:
        st.metric("Total Messages", len(st.session_state.chat_history))
        if st.session_state.retrieved_contexts:
            avg_retrieval = sum(c["retrieval_latency"] for c in st.session_state.retrieved_contexts) / len(st.session_state.retrieved_contexts)
            avg_llm = sum(c["llm_latency"] for c in st.session_state.retrieved_contexts) / len(st.session_state.retrieved_contexts)
            st.metric("Avg Retrieval Time", f"{avg_retrieval*1000:.1f}ms")
            st.metric("Avg LLM Time", f"{avg_llm*1000:.1f}ms")
    
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.chat_history = []
        st.session_state.retrieved_contexts = []
        st.session_state.memory_history = []
        st.rerun()

# Main chat interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Conversation")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])
                    # Show latency info if available
                    if i > 0 and i // 2 < len(st.session_state.retrieved_contexts):
                        ctx_idx = (i - 1) // 2
                        if ctx_idx < len(st.session_state.retrieved_contexts):
                            ctx = st.session_state.retrieved_contexts[ctx_idx]
                            st.caption(
                                f"⏱️ Retrieval: {ctx['retrieval_latency']*1000:.1f}ms | "
                                f"LLM: {ctx['llm_latency']*1000:.1f}ms | "
                                f"Total: {ctx['total_latency']*1000:.1f}ms"
                            )

    # Chat input
    user_input = st.chat_input("Ask a question...")
    
    if user_input:
        with st.spinner("Processing your query..."):
            answer, context_info, memory_block = process_query(user_input, top_k, threshold)
            st.rerun()

with col2:
    st.header("🔍 Retrieved Context")
    
    if st.session_state.retrieved_contexts:
        # Show context for the most recent query
        latest_context = st.session_state.retrieved_contexts[-1]
        
        st.subheader("Latest Query Context")
        st.write(f"**Query:** {latest_context['query']}")
        st.write(f"**Retrieved:** {len(latest_context['documents'])} documents")
        if 'threshold' in latest_context:
            st.caption(f"Threshold: {latest_context['threshold']:.2f} | Top-K: {latest_context.get('n_results', 'N/A')}")
        
        # Display retrieved documents
        if latest_context['documents']:
            for i, doc in enumerate(latest_context['documents']):
                with st.expander(f"Document {i+1}"):
                    st.write(doc[:1000] + "..." if len(doc) > 1000 else doc)
                    if latest_context['doc_ids'] and i < len(latest_context['doc_ids']):
                        st.caption(f"ID: {latest_context['doc_ids'][i]}")
                    if latest_context['distances'] and i < len(latest_context['distances']):
                        st.caption(f"Similarity Distance: {latest_context['distances'][i]:.4f}")
        else:
            st.info("No documents retrieved for this query")
    else:
        st.info("No context retrieved yet. Start a conversation to see retrieved documents.")
    
    st.header("🧠 Memory State")
    if st.session_state.memory_history:
        latest_memory = st.session_state.memory_history[-1]
        with st.expander("View Memory", expanded=True):
            st.text_area(
                "Running Summary + Recent Turns",
                value=latest_memory["memory"] or "(no memory yet)",
                height=200,
                disabled=True,
                label_visibility="collapsed"
            )
    else:
        st.info("Memory will appear after the first conversation turn.")

# Footer
st.divider()
st.caption("RAG Assistant - Powered by LangChain, ChromaDB, and Streamlit")

