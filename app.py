import os

# Disable ChromaDB telemetry BEFORE any imports to avoid "capture() takes 1 positional argument but 3 were given" warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List
import re

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.vectordb import VectorDB
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Other Fucntion Import 
from utils.file_utils import load_all_publications, load_yaml_config
from utils.prompt_builder import build_prompt_from_config
from utils.paths import PROMPT_CONFIG_FPATH, OUTPUTS_DIR, APP_CONFIG_FPATH
from utils.log_utils import get_logger, JsonlTrace, TimingContext
from utils.memory_utils import MemoryManager

# Configuration
system_prompt = 'knowledge_assistant_prompt'

# Load environment variables
load_dotenv()

LOGGER = get_logger("rag_assistant", outputs_dir=OUTPUTS_DIR)

# Load app config
try:
    app_config = load_yaml_config(APP_CONFIG_FPATH)
    log_config = app_config.get("logging", {})
    llm_config = app_config.get("llm", {})
    vectordb_config = app_config.get("vectordb", {})
    memory_config = app_config.get("memory_strategies", {})
except Exception as e:
    LOGGER.warning(f"Could not load app_config.yaml, using default settings: {e}")
    log_config = {}
    llm_config = {}
    vectordb_config = {}
    memory_config = {}

# Default values from config
DEFAULT_N_RESULTS = vectordb_config.get("n_results", 3)
DEFAULT_THRESHOLD = vectordb_config.get("threshold", 0.5)
DEFAULT_SUMMARIZE_EVERY_N = memory_config.get("summarize_every_n", 6)
DEFAULT_RECENT_WINDOW_N = memory_config.get("recent_window_n", 8)

TRACE = JsonlTrace(Path(OUTPUTS_DIR) / "rag_assistant_traces.jsonl", log_config=log_config)

class RAGAssistant:
    """
    A simple RAG-based AI assistant using ChromaDB and multiple LLM providers.
    Supports OpenAI, Groq, and Google Gemini APIs.
    """

    def __init__(self):
        """Initialize the RAG assistant."""
        self.trace_session_id = uuid.uuid4().hex
        LOGGER.info("Initializing RAG Assistant...")

        # Initialize LLM - check for available API keys in order of preference
        self.llm = self._initialize_llm()
        if not self.llm:
            raise ValueError(
                "No valid API key found. Please set one of: "
                "OPENAI_API_KEY, GROQ_API_KEY, or GOOGLE_API_KEY in your .env file"
            )

        # Initialize vector database
        self.vector_db = VectorDB(
            collection_name="publications",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            default_threshold=DEFAULT_THRESHOLD
        )

        # Create RAG prompt template
        prompt_config = load_yaml_config(PROMPT_CONFIG_FPATH)[system_prompt]
        system_instructions = build_prompt_from_config(prompt_config)

        rag_template = """
            {system_instructions}

            You are a precise assistant. Use ONLY the provided Context and Memory when relevant.
            If the answer is not in Context, and Memory doesn't contain the needed conversational detail, say "I don't know."

            # Memory (running summary + recent turns; use only if relevant)
            {memory}

            # Context
            {context}

            # Question
            {question}

            # Answer (concise and specific):
        """

        try:
            self.prompt_template = ChatPromptTemplate.from_template(rag_template).partial(
                system_instructions=system_instructions
            )
            # Create the chain
            self.chain = self.prompt_template | self.llm | StrOutputParser()
        except Exception as e:
            LOGGER.error(f"Failed to create prompt template or chain: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Memory manager (moved to memory_utils)
        self.memory = MemoryManager(
            llm=self.llm,
            memory_dir=Path(OUTPUTS_DIR) / "memory",
            summarize_every_n=DEFAULT_SUMMARIZE_EVERY_N,
            recent_window_n=DEFAULT_RECENT_WINDOW_N,
        )
        
        # Store default config values for use in invoke
        self.default_n_results = DEFAULT_N_RESULTS
        self.default_threshold = DEFAULT_THRESHOLD

        LOGGER.info("RAG Assistant initialized successfully")

        print("RAG Assistant initialized successfully")

    def _initialize_llm(self):
        """
        Initialize the LLM by checking for available API keys.
        Uses provider preference from config, or tries OpenAI, Groq, and Google Gemini in that order.
        """
        provider_preference = llm_config.get("provider_preference", "openai").lower()
        temperature = llm_config.get("temperature", 0.0)
        
        # Determine provider order based on preference
        providers = []
        if provider_preference == "openai":
            providers = ["openai", "groq", "google"]
        elif provider_preference == "groq":
            providers = ["groq", "openai", "google"]
        elif provider_preference == "google":
            providers = ["google", "openai", "groq"]
        else:
            providers = ["openai", "groq", "google"]  # default fallback
        
        # Try providers in preference order
        for provider in providers:
            if provider == "openai" and os.getenv("OPENAI_API_KEY"):
                model_name = os.getenv("OPENAI_MODEL") or llm_config.get("openai_model", "gpt-4o-mini")
                LOGGER.info(f"Using OpenAI model: {model_name}")
                print(f"Using OpenAI model: {model_name}")
                return ChatOpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"), 
                    model=model_name, 
                    temperature=temperature
                )
            
            elif provider == "groq" and os.getenv("GROQ_API_KEY"):
                model_name = os.getenv("GROQ_MODEL") or llm_config.get("groq_model", "llama-3.1-8b-instant")
                LOGGER.info(f"Using Groq model: {model_name}")
                print(f"Using Groq model: {model_name}")
                return ChatGroq(
                    api_key=os.getenv("GROQ_API_KEY"), 
                    model=model_name, 
                    temperature=temperature
                )
            
            elif provider == "google" and os.getenv("GOOGLE_API_KEY"):
                model_name = os.getenv("GOOGLE_MODEL") or llm_config.get("google_model", "gemini-2.0-flash")
                LOGGER.info(f"Using Google Gemini model: {model_name}")
                print(f"Using Google Gemini model: {model_name}")
                return ChatGoogleGenerativeAI(
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    model=model_name,
                    temperature=temperature,
                )
        
        raise ValueError(
            "No valid API key found. Please set one of: OPENAI_API_KEY, GROQ_API_KEY, or GOOGLE_API_KEY in your .env file"
        )


    def add_documents(self, documents: List) -> None:
        """
        Add documents to the knowledge base.

        Args:
            documents: List of documents
        """
        self.vector_db.add_documents(documents)

        # Logging and Tracing 
        LOGGER.info(f"Added {len(documents)} documents to vector DB")
        TRACE.write({
            "ts": datetime.now(timezone.utc).isoformat(),
            "session": self.trace_session_id,
            "event": "add_documents",
            "count": len(documents),
        })

    def invoke(self, input: str, n_results: int = None, threshold: float = None) -> str:
        """
        Query the RAG assistant.

        Args:
            input: User's input
            n_results: Number of relevant chunks to retrieve (defaults to config value)
            threshold: Similarity threshold for retrieval (defaults to config value)

        Returns:
            The assistant's answer as a string
        """
        # Use provided values or fall back to defaults
        n_results = n_results if n_results is not None else self.default_n_results
        threshold = threshold if threshold is not None else self.default_threshold
        
        request_id = uuid.uuid4().hex
        total_timer = TimingContext()
        
        with total_timer:
            self.memory.add_user_turn(input.strip())

            # Retrieval with timing
            retrieval_timer = TimingContext()
            with retrieval_timer:
                retrieved = self.vector_db.search(query=input, n_results=n_results, threshold=threshold)
            retrieval_latency = retrieval_timer.get_elapsed()
            
            docs = retrieved.get("documents", []) if isinstance(retrieved, dict) else []
            doc_ids = retrieved.get("ids", []) if isinstance(retrieved, dict) else []
            distances = retrieved.get("distances", []) if isinstance(retrieved, dict) else []
            
            if not docs:
                context = ""  # let the prompt trigger "I don't know."
            else:
                context = "\n\n".join(f"[{i+1}] {d}" for i, d in enumerate(docs))

            # Memory block
            memory_block = self.memory.get_memory_context()

            # Invoke LLM with timing
            llm_timer = TimingContext()
            with llm_timer:
                llm_answer = self.chain.invoke({
                    "memory": memory_block,
                    "context": context,
                    "question": input
                })
            llm_latency = llm_timer.get_elapsed()

            # Record assistant turn and maybe summarize/compact
            self.memory.add_assistant_turn(llm_answer)
        
        total_latency = total_timer.get_elapsed()

        # Enhanced logging with latency info
        latency_info = f" | retrieval={retrieval_latency*1000:.1f}ms | llm={llm_latency*1000:.1f}ms | total={total_latency*1000:.1f}ms" if TRACE.log_latency else ""
        LOGGER.info(f"[request_id={request_id}] Q len={len(input)} | ctx_docs={len(docs)} | A len={len(llm_answer)}{latency_info}")
        
        # Use enhanced trace writing
        TRACE.write_enhanced_invoke(
            session_id=self.trace_session_id,
            request_id=request_id,
            question=input,
            answer=llm_answer,
            retrieved_docs=docs,
            doc_ids=doc_ids if doc_ids else None,
            distances=distances if distances else None,
            retrieval_latency=retrieval_latency,
            llm_latency=llm_latency,
            total_latency=total_latency,
            memory_excerpt=memory_block,
        )

        return llm_answer

def main():
    """Main function to demonstrate the RAG assistant."""
    try:
        # Initialize the RAG assistant
        LOGGER.info("Booting demo...")
        print("Initializing RAG Assistant...")
        assistant = RAGAssistant()

        # Load sample documents
        LOGGER.info("Loading documents...")
        print("\nLoading documents...")
        sample_docs = load_all_publications()
        LOGGER.info(f"Loaded {len(sample_docs)} sample documents")
        print(f"Loaded {len(sample_docs)} sample documents")

        assistant.add_documents(sample_docs)

        done = False

        while not done:
            question = input("Enter a question or 'quit' to exit: ")
            if question.lower() == "quit":
                done = True
            else:
                result = assistant.invoke(question)
                print(result)

    except Exception as e:
        import traceback
        print(f"Error running RAG assistant: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("\nMake sure you have set up your .env file with at least one API key: OPENAI_API_KEY, GROQ_API_KEY or GOOGLE_API_KEY")


if __name__ == "__main__":
    main()

