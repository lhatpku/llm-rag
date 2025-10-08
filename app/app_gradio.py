# app_gradio.py
import os
from pathlib import Path
from datetime import datetime, timezone

import gradio as gr

from paths import OUTPUTS_DIR
from file_utils import load_all_publications
from log_utils import get_logger, JsonlTrace
from app import RAGAssistant 

LOGGER = get_logger("rag_assistant_ui", outputs_dir=OUTPUTS_DIR)
TRACE = JsonlTrace(Path(OUTPUTS_DIR) / "rag_assistant_ui_traces.jsonl")

# --- Build a single, persistent assistant instance for the Gradio app ---
ASSISTANT = None

def get_assistant():
    global ASSISTANT
    if ASSISTANT is None:
        LOGGER.info("Initializing RAGAssistant for Gradio UI...")
        ASSISTANT = RAGAssistant()
        # load docs once
        docs = load_all_publications()
        ASSISTANT.add_documents(docs)
        LOGGER.info(f"Docs loaded: {len(docs)}")
    return ASSISTANT

def format_context(docs):
    """Make a readable text block for retrieved documents."""
    if not docs:
        return "(no retrieved context)"
    return "\n\n".join(f"[{i+1}] {d}" for i, d in enumerate(docs))

def step(message, chat_messages, top_k):
    """
    Gradio chat step:
    - calls RAG with memory,
    - returns answer, plus debug panels: Context and Memory.
    """
    if chat_messages is None:
        chat_messages = []

    assistant = get_assistant()
    user_text = (message or "").strip()

    # --- append the user message in messages format ---
    chat_messages.append({"role": "user", "content": user_text})

    # --- Retrieval (use the same path assistant.invoke uses) ---
    retrieved = assistant.vector_db.search(query=user_text, n_results=int(top_k))
    docs = retrieved.get("documents", []) if isinstance(retrieved, dict) else []
    context_str = format_context(docs)

    # --- Memory block for prompt (and record the user turn) ---
    assistant.memory.add_user_turn(user_text)
    memory_block = assistant.memory.get_memory_context()

    # --- LLM call using the same chain ---
    answer = assistant.chain.invoke({
        "memory": memory_block,
        "context": context_str if docs else "",
        "question": user_text
    })

    # --- Record assistant turn (and periodic summarize/compact) ---
    assistant.memory.add_assistant_turn(answer)
    chat_messages.append({"role": "assistant", "content": answer})

    # --- Emit trace for debugging ---
    TRACE.write({
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "ui_step",
        "question": user_text,
        "retrieved_doc_count": len(docs),
        "memory_excerpt": (memory_block or "")[:600],
        "answer_excerpt": (answer or "")[:400],
    })

    return chat_messages, context_str or "(no retrieved context)", memory_block or "(no memory yet)"

def clear_all():
    """Clear chat area only; assistant memory persists (so you can keep context across UI clears)."""
    return [], "", ""

with gr.Blocks(css="""
#debug-panels {height: 260px}
""") as demo:
    gr.Markdown("## RAG Chat • with Debug Panels (Context + Memory)")

    with gr.Row():
        chatbot = gr.Chatbot(label="Chat", height=480, type="messages")
        with gr.Column():
            context_box = gr.Textbox(label="Retrieved Context (debug)", lines=12, interactive=False, elem_id="debug-panels")
            memory_box = gr.Textbox(label="Summarized Memory (debug)", lines=12, interactive=False, elem_id="debug-panels")

    with gr.Row():
        msg = gr.Textbox(placeholder="Ask anything…", show_label=False)
    with gr.Row():
        top_k = gr.Slider(1, 8, value=3, step=1, label="Top-K Context")
        send_btn = gr.Button("Send", variant="primary")
        clear_btn = gr.Button("Clear Chat")

    # wire up events
    send_btn.click(
        fn=step,
        inputs=[msg, chatbot, top_k],
        outputs=[chatbot, context_box, memory_box],
    ).then(  # clear the input box after send
        fn=lambda: "",
        inputs=None,
        outputs=msg
    )

    msg.submit(
        fn=step,
        inputs=[msg, chatbot, top_k],
        outputs=[chatbot, context_box, memory_box],
    ).then(
        fn=lambda: "",
        inputs=None,
        outputs=msg
    )

    clear_btn.click(fn=clear_all, inputs=None, outputs=[chatbot, context_box, memory_box])

if __name__ == "__main__":
    # Launch on http://127.0.0.1:7860
    demo.launch()
