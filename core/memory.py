"""
Attc Jarvis - Conversation Memory
===================================
Short-term conversation buffer to maintain context across turns.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Message:
    role: Literal["user", "model"]
    text: str


class ConversationMemory:
    """Ring-buffer style conversation memory."""

    def __init__(self, max_size: int = 20) -> None:
        self._buffer: list[Message] = []
        self._max_size = max_size

    # ── Public API ────────────────────────────────────────

    def add(self, role: Literal["user", "model"], text: str) -> None:
        self._buffer.append(Message(role=role, text=text))
        if len(self._buffer) > self._max_size:
            self._buffer = self._buffer[-self._max_size :]

    def get_history(self) -> list[dict]:
        """Return history in Gemini-compatible format."""
        return [{"role": m.role, "parts": [m.text]} for m in self._buffer]

    def clear(self) -> None:
        self._buffer.clear()

    @property
    def size(self) -> int:
        return len(self._buffer)
