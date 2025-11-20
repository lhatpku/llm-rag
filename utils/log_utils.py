# log_utils.py
import json
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any, Optional, List
from utils.paths import OUTPUTS_DIR

DEFAULT_OUTPUTS_DIR = "outputs"

def get_logger(
    name: str = "rag_assistant",
    outputs_dir: str | Path = OUTPUTS_DIR,
    level: int = logging.INFO,
) -> logging.Logger:
    """Configure and return a named logger (console + rotating file)."""
    outputs_dir = Path(outputs_dir)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    # Rotating file
    file_log = outputs_dir / f"{name}.log"
    fh = RotatingFileHandler(file_log, maxBytes=2_000_000, backupCount=3)
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


class TimingContext:
    """Context manager for measuring execution time."""
    def __init__(self):
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        return False
    
    def get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.elapsed is None:
            return time.time() - self.start_time
        return self.elapsed


class JsonlTrace:
    """Append-only JSONL event stream for structured traces with enhanced observability."""
    def __init__(self, path: str | Path, log_config: Optional[Dict[str, Any]] = None):
        """
        Initialize JSONL trace writer.
        
        Args:
            path: Path to the JSONL trace file
            log_config: Optional logging configuration dict with keys:
                - log_scores: bool (default True)
                - log_doc_ids: bool (default True)
                - log_latency: bool (default True)
                - log_eval_flags: bool (default False)
                - log_full_documents: bool (default False)
                - max_doc_excerpt_length: int (default 500)
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Default logging config (all enabled for backward compatibility)
        self.log_config = log_config or {}
        self.log_scores = self.log_config.get("log_scores", True)
        self.log_doc_ids = self.log_config.get("log_doc_ids", True)
        self.log_latency = self.log_config.get("log_latency", True)
        self.log_eval_flags = self.log_config.get("log_eval_flags", False)
        self.log_full_documents = self.log_config.get("log_full_documents", False)
        self.max_doc_excerpt_length = self.log_config.get("max_doc_excerpt_length", 500)

    def write(self, record: Dict[str, Any]) -> None:
        """Write a trace record to the JSONL file."""
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    def write_enhanced_invoke(
        self,
        session_id: str,
        request_id: str,
        question: str,
        answer: str,
        retrieved_docs: List[str],
        doc_ids: Optional[List[str]] = None,
        distances: Optional[List[float]] = None,
        retrieval_latency: Optional[float] = None,
        llm_latency: Optional[float] = None,
        total_latency: Optional[float] = None,
        memory_excerpt: Optional[str] = None,
        eval_flags: Optional[Dict[str, Any]] = None,
        **extra_fields
    ) -> None:
        """
        Write an enhanced invoke trace with configurable observability fields.
        
        Args:
            session_id: Session identifier
            request_id: Unique request identifier
            question: User's question
            answer: LLM's answer
            retrieved_docs: List of retrieved document chunks
            doc_ids: Optional list of document chunk IDs
            distances: Optional list of similarity distances/scores
            retrieval_latency: Optional retrieval time in seconds
            llm_latency: Optional LLM call time in seconds
            total_latency: Optional total request time in seconds
            memory_excerpt: Optional memory context excerpt
            eval_flags: Optional evaluation flags/metrics dict
            **extra_fields: Additional fields to include in the trace
        """
        from datetime import datetime, timezone
        
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session": session_id,
            "request_id": request_id,
            "event": "invoke",
            "question": question,
            "retrieved_doc_count": len(retrieved_docs),
            "answer": answer,
        }
        
        # Add document IDs if enabled
        if self.log_doc_ids and doc_ids:
            record["retrieved_doc_ids"] = doc_ids
        
        # Add scores/distances if enabled
        if self.log_scores and distances:
            record["retrieval_distances"] = distances
        
        # Add latency metrics if enabled
        if self.log_latency:
            latency_info = {}
            if retrieval_latency is not None:
                latency_info["retrieval_ms"] = round(retrieval_latency * 1000, 2)
            if llm_latency is not None:
                latency_info["llm_ms"] = round(llm_latency * 1000, 2)
            if total_latency is not None:
                latency_info["total_ms"] = round(total_latency * 1000, 2)
            if latency_info:
                record["latency"] = latency_info
        
        # Add evaluation flags if enabled
        if self.log_eval_flags and eval_flags:
            record["eval_flags"] = eval_flags
        
        # Add document content (full or excerpted)
        if self.log_full_documents:
            record["retrieved_documents"] = retrieved_docs
        else:
            # Include excerpts for debugging
            excerpts = [
                doc[:self.max_doc_excerpt_length] + ("..." if len(doc) > self.max_doc_excerpt_length else "")
                for doc in retrieved_docs
            ]
            record["retrieved_doc_excerpts"] = excerpts
        
        # Add memory excerpt if provided
        if memory_excerpt:
            record["memory_excerpt"] = memory_excerpt[:300] if len(memory_excerpt) > 300 else memory_excerpt
        
        # Add any extra fields
        record.update(extra_fields)
        
        self.write(record)
