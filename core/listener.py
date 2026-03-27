"""
Attc Jarvis - Listening Modes
===============================
Two modes:
  1. Wake Word Mode  - Offline wake word via openwakeword (free, no API key), then STT
  2. Always Listen   - Continuous STT, triggers on "jarvis" keyword in text
"""

from __future__ import annotations

import threading
import time
from enum import Enum, auto
from typing import Callable

import numpy as np
import pyaudio

import config
from core.voice import SpeechToText

try:
    import openwakeword
    from openwakeword.model import Model as OWWModel
    openwakeword.utils.download_models(["hey_jarvis_v0.1"])
    HAS_OWW = True
except Exception:
    HAS_OWW = False


class ListenMode(Enum):
    WAKE_WORD = auto()    # "Sadece Seslenince Dinle"
    ALWAYS_ON = auto()    # "Her Zaman Dinle"


class ListenerEngine:
    """Manages microphone listening based on selected mode."""

    def __init__(
        self,
        mode: ListenMode = ListenMode.WAKE_WORD,
        language: str = "tr",
        on_command: Callable[[str], None] | None = None,
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        self._mode = mode
        self._language = language
        self._stt = SpeechToText(language=language)
        self._on_command = on_command or (lambda x: None)
        self._on_status = on_status or (lambda x: None)
        self._running = False
        self._thread: threading.Thread | None = None

    # ── Public API ────────────────────────────────────────

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
            self._thread.join(timeout=3)
            self._thread = None

    @property
    def is_running(self) -> bool:
        return self._running

    # ── Private Loop ──────────────────────────────────────

    def _run_loop(self) -> None:
        while self._running:
            try:
                if self._mode == ListenMode.WAKE_WORD:
                    self._wake_word_cycle()
                else:
                    self._always_on_cycle()
            except Exception as e:
                self._on_status(f"Dinleyici hatası: {e}")
                time.sleep(1)

    def _wake_word_cycle(self) -> None:
        """Wait for wake word offline, then listen for command."""
        self._on_status("Bekleniyor... ('Hey Jarvis' deyin)")

        if HAS_OWW:
            self._openwakeword_wait()
        else:
            self._fallback_wake_word_wait()

        if not self._running:
            return

        self._on_status("Dinleniyor...")
        text = self._stt.listen_once(timeout=7, phrase_limit=20)
        if text:
            self._on_command(text)

    def _always_on_cycle(self) -> None:
        """Continuously listen; trigger when 'jarvis' is mentioned."""
        self._on_status("Sürekli dinleniyor...")
        text = self._stt.listen_once(timeout=10, phrase_limit=20)
        if text and config.WAKE_WORD_KEYWORD in text.lower():
            cleaned = text.lower().replace("jarvis", "").strip()
            if cleaned:
                self._on_command(cleaned)
            else:
                self._on_status("Komut algılanamadı.")

    def _openwakeword_wait(self) -> None:
        """Block until openwakeword detects 'Hey Jarvis' — fully offline, no API key."""
        oww_model = OWWModel(wakeword_models=["hey_jarvis_v0.1"])
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=1280,
        )
        try:
            while self._running:
                raw = stream.read(1280, exception_on_overflow=False)
                audio_chunk = np.frombuffer(raw, dtype=np.int16)
                prediction = oww_model.predict(audio_chunk)

                for model_name, score in prediction.items():
                    if score > config.WAKE_WORD_THRESHOLD:
                        self._on_status("Uyanma kelimesi algılandı!")
                        oww_model.reset()
                        return
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

    def _fallback_wake_word_wait(self) -> None:
        """Fallback: use STT to detect wake word (works without openwakeword)."""
        while self._running:
            text = self._stt.listen_once(timeout=5, phrase_limit=5)
            if text and "jarvis" in text.lower():
                self._on_status("Uyanma kelimesi algılandı!")
                return
            time.sleep(0.1)
