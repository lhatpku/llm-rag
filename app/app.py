import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List
import re

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vectordb import VectorDB
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Other Fucntion Import 
from file_utils import load_all_publications, load_yaml_config
from prompt_builder import build_prompt_from_config
from paths import PROMPT_CONFIG_FPATH, OUTPUTS_DIR
from log_utils import get_logger, JsonlTrace
from memory_utils import MemoryManager

# Configuration
system_prompt = 'knowledge_assistant_prompt'
rag_invoke_n_results = 3


# Load environment variables
load_dotenv()

LOGGER = get_logger("rag_assistant", outputs_dir=OUTPUTS_DIR)
TRACE = JsonlTrace(Path(OUTPUTS_DIR) / "rag_assistant_traces.jsonl")

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
        self.vector_db = VectorDB(collection_name="publications",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",)

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

        self.prompt_template = ChatPromptTemplate.from_template(rag_template).partial(
            system_instructions=system_instructions
        )
        # Create the chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()

        # Memory manager (moved to memory_utils)
        self.memory = MemoryManager(
            llm=self.llm,
            memory_dir=Path(OUTPUTS_DIR) / "memory",
            summarize_every_n=int(os.getenv("SUMMARIZE_EVERY_N", "6")),
            recent_window_n=int(os.getenv("RECENT_WINDOW_N", "8")),
        )

        LOGGER.info("RAG Assistant initialized successfully")

        print("RAG Assistant initialized successfully")

    def _initialize_llm(self):
        """
        Initialize the LLM by checking for available API keys.
        Tries OpenAI, Groq, and Google Gemini in that order.
        """
        # Check for OpenAI API key
        if os.getenv("OPENAI_API_KEY"):
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            LOGGER.info(f"Using OpenAI model: {model_name}")
            print(f"Using OpenAI model: {model_name}")
            return ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"), model=model_name, temperature=0.0
            )

        elif os.getenv("GROQ_API_KEY"):
            model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            LOGGER.info(f"Using Groq model: {model_name}")
            print(f"Using Groq model: {model_name}")
            return ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"), model=model_name, temperature=0.0
            )

        elif os.getenv("GOOGLE_API_KEY"):
            model_name = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
            LOGGER.info(f"Using Google Gemini model: {model_name}")
            print(f"Using Google Gemini model: {model_name}")
            return ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                model=model_name,
                temperature=0.0,
            )
        else:
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

    def invoke(self, input: str, n_results: int = rag_invoke_n_results) -> str:
        """
        Query the RAG assistant.

        Args:
            input: User's input
            n_results: Number of relevant chunks to retrieve

        Returns:
            Dictionary containing the answer and retrieved context
        """
        request_id = uuid.uuid4().hex
        self.memory.add_user_turn(input.strip())

        # Retrieval
        retrieved = self.vector_db.search(query=input, n_results=n_results)
        docs = retrieved.get("documents", []) if isinstance(retrieved, dict) else []
        if not docs:
            context = ""  # let the prompt trigger "I don't know."
        else:
            context = "\n\n".join(f"[{i+1}] {d}" for i, d in enumerate(docs))

        # Memory block
        memory_block = self.memory.get_memory_context()

        # Invoke LLM
        llm_answer = self.chain.invoke({
            "memory": memory_block,
            "context": context,
            "question": input
        })

        # Record assistant turn and maybe summarize/compact
        self.memory.add_assistant_turn(llm_answer)

        # Logging + trace
        LOGGER.info(f"[request_id={request_id}] Q len={len(input)} | ctx_docs={len(docs)} | A len={len(llm_answer)}")
        TRACE.write({
            "ts": datetime.now(timezone.utc).isoformat(),
            "session": self.trace_session_id,
            "request_id": request_id,
            "event": "invoke",
            "question": input,
            "retrieved_doc_count": len(docs),
            "answer": llm_answer,
            "memory_excerpt": memory_block[:300],
        })

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
        print(f"Error running RAG assistant: {e}")
        print("Make sure you have set up your .env file with at least one API key: OPENAI_API_KEY, GROQ_API_KEY or GOOGLE_API_KEY")


if __name__ == "__main__":
    main()