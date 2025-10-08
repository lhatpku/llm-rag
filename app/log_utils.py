# log_utils.py
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any
from paths import OUTPUTS_DIR

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


class JsonlTrace:
    """Append-only JSONL event stream for structured traces."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, record: Dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
