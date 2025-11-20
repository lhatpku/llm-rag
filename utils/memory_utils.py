# memory_utils.py
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
You compress conversation history into a concise, factual running brief.

Guidelines:
- Keep key user preferences, goals, entities, decisions, and unresolved items.
- Remove chit-chat, duplicated facts, and stale threads.
- Use neutral, bullet-like sentences (max 8 bullets).
- ≤ 1800 characters.

# Existing Summary
{existing_summary}

# New Turns (most recent first)
{new_turns}

# Updated Running Summary:
""")

class MemoryManager:
    """
    Maintains a rolling running_summary plus a small recent window.
    Periodically summarizes (using the provided LLM) to bound token growth.
    """
    def __init__(
        self,
        llm,
        memory_dir: str | Path,
        session_id: Optional[str] = None,
        summarize_every_n: int = 6,
        recent_window_n: int = 8,
        summary_file: str = "memory_summary.json",
    ):
        self.llm = llm
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id 
        self.summarize_every_n = summarize_every_n
        self.recent_window_n = recent_window_n
        self.summary_path = self.memory_dir / summary_file

        self.running_summary: str = ""
        self.turns: List[Dict[str, str]] = []  # [{role: "user"/"assistant", "content": "..."}]
        self._load_summary()

        self.summarize_chain = SUMMARY_PROMPT | self.llm | StrOutputParser()

    # ---------------- private ----------------
    def _load_summary(self) -> None:
        if self.summary_path.exists():
            try:
                obj = json.loads(self.summary_path.read_text(encoding="utf-8"))
                self.running_summary = obj.get("running_summary", "")
            except Exception:
                self.running_summary = ""
        else:
            self.running_summary = ""

    def _persist_summary(self) -> None:
        data = {
            "session_id": self.session_id,
            "updated_at": datetime.utcnow().isoformat(),
            "running_summary": self.running_summary,
        }
        self.summary_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _summarize_and_compact(self) -> None:
        recent = self.turns[-self.recent_window_n:]
        new_turns_text = "\n".join(
            f"- {t['role']}: {t['content'][:800]}" for t in reversed(recent)
        )
        updated_summary = self.summarize_chain.invoke({
            "existing_summary": self.running_summary or "(none yet)",
            "new_turns": new_turns_text or "(no new turns)",
        })
        self.running_summary = updated_summary.strip()
        self.turns = recent[:]  # retain only small window
        self._persist_summary()

    # ---------------- public ----------------
    def add_user_turn(self, text: str) -> None:
        self.turns.append({"role": "user", "content": text})

    def add_assistant_turn(self, text: str) -> None:
        self.turns.append({"role": "assistant", "content": text})
        if len(self.turns) % self.summarize_every_n == 0:
            self._summarize_and_compact()

    def get_memory_context(self) -> str:
        """
        Returns concise memory block for prompts:
        - Running summary (compact, always available)
        - Last few turns (to preserve immediate local coherence)
        """
        recent_lines = "\n".join(f"{t['role']}: {t['content']}" for t in self.turns[-4:])
        memory = []
        if self.running_summary:
            memory.append(f"[Running Summary]\n{self.running_summary}")
        if recent_lines:
            memory.append(f"[Recent Turns]\n{recent_lines}")
        return "\n\n".join(memory).strip()
