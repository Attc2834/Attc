"""
Attc Jarvis Termux - Listening Modes
=======================================
Two modes adapted for Termux:
  1. Wake Word  - Continuous short recordings, checks for "jarvis" keyword
  2. Always On  - Continuous recording, triggers on any "jarvis" mention
"""

from __future__ import annotations

import threading
import time
from enum import Enum, auto
from typing import Callable

import config
from core.voice import TermuxSTT


class ListenMode(Enum):
    WAKE_WORD = auto()
    ALWAYS_ON = auto()


class TermuxListener:
    """Manages microphone listening on Termux."""

    def __init__(
        self,
        mode: ListenMode = ListenMode.WAKE_WORD,
        language: str = "tr",
        on_command: Callable[[str], None] | None = None,
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        self._mode = mode
        self._language = language
        self._stt = TermuxSTT(language=language)
        self._on_command = on_command or (lambda x: None)
        self._on_status = on_status or (lambda x: None)
        self._running = False
        self._thread: threading.Thread | None = None

    def set_mode(self, mode: ListenMode) -> None:
        was_running = self._running
        if was_running:
            self.stop()
        self._mode = mode
        if was_running:
            self.start()

    def set_language(self, lang: str) -> None:
        self._language = lang
        self._stt.set_language(lang)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    @property
    def is_running(self) -> bool:
        return self._running

    def _run_loop(self) -> None:
        while self._running:
            try:
                if self._mode == ListenMode.WAKE_WORD:
                    self._wake_word_cycle()
                else:
                    self._always_on_cycle()
            except Exception as e:
                self._on_status(f"Hata: {e}")
                time.sleep(2)

    def _wake_word_cycle(self) -> None:
        self._on_status("Bekleniyor... ('Hey Jarvis' deyin)")

        # Short recordings to detect wake word (3 sec bursts)
        while self._running:
            text = self._stt.listen_once(duration=3)
            if text and config.WAKE_WORD_KEYWORD in text.lower():
                self._on_status("Uyanma kelimesi algılandı! Dinleniyor...")
                break
            time.sleep(0.3)

        if not self._running:
            return

        # Now listen for the actual command
        text = self._stt.listen_once(duration=config.RECORDING_DURATION)
        if text:
            self._on_command(text)

    def _always_on_cycle(self) -> None:
        self._on_status("Sürekli dinleniyor...")
        text = self._stt.listen_once(duration=config.RECORDING_DURATION)
        if text and config.WAKE_WORD_KEYWORD in text.lower():
            cleaned = text.lower().replace("jarvis", "").strip()
            if cleaned:
                self._on_command(cleaned)
