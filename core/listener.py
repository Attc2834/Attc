"""
Attc Jarvis - Listening Modes
===============================
Two modes:
  1. Wake Word Mode  - Offline wake word via Porcupine, then STT
  2. Always Listen   - Continuous STT, triggers on "jarvis" keyword in text
"""

from __future__ import annotations

import struct
import threading
import time
from enum import Enum, auto
from typing import Callable

import speech_recognition as sr

import config
from core.voice import SpeechToText

try:
    import pvporcupine
    import pyaudio
    HAS_PORCUPINE = True
except ImportError:
    HAS_PORCUPINE = False


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
                self._on_status(f"Listener error: {e}")
                time.sleep(1)

    def _wake_word_cycle(self) -> None:
        """Wait for wake word offline, then listen for command."""
        self._on_status("Bekleniyor... ('Hey Jarvis' deyin)")

        if HAS_PORCUPINE and config.PORCUPINE_ACCESS_KEY:
            self._porcupine_wait()
        else:
            # Fallback: use STT and check for wake word
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
            # Remove the wake word from the command
            cleaned = text.lower().replace("jarvis", "").strip()
            if cleaned:
                self._on_command(cleaned)
            else:
                self._on_status("Komut algılanamadı.")

    def _porcupine_wait(self) -> None:
        """Block until Porcupine detects 'Jarvis' wake word offline."""
        porcupine = None
        pa = None
        audio_stream = None
        try:
            porcupine = pvporcupine.create(
                access_key=config.PORCUPINE_ACCESS_KEY,
                keywords=["jarvis"],
            )
            pa = pyaudio.PyAudio()
            audio_stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length,
            )
            while self._running:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    self._on_status("Uyanma kelimesi algılandı!")
                    break
        finally:
            if audio_stream:
                audio_stream.close()
            if pa:
                pa.terminate()
            if porcupine:
                porcupine.delete()

    def _fallback_wake_word_wait(self) -> None:
        """Fallback: use STT to detect wake word (uses API but works without Porcupine)."""
        while self._running:
            text = self._stt.listen_once(timeout=5, phrase_limit=5)
            if text and "jarvis" in text.lower():
                self._on_status("Uyanma kelimesi algılandı!")
                return
            time.sleep(0.1)
