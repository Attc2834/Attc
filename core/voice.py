"""
Attc Jarvis - Voice Engine
============================
Speech-to-Text (STT) via SpeechRecognition + Google
Text-to-Speech (TTS) via edge-tts (free, unlimited, human-like)
"""

from __future__ import annotations

import asyncio
import io
import tempfile
import threading
from pathlib import Path

import edge_tts
import speech_recognition as sr

import config

try:
    from pydub import AudioSegment
    from pydub.playback import play as pydub_play
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False


class SpeechToText:
    """Microphone listener using SpeechRecognition."""

    def __init__(self, language: str = "tr") -> None:
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = 300
        self._recognizer.dynamic_energy_threshold = True
        self._language = language
        self._lang_codes = {"tr": "tr-TR", "en": "en-US"}

    def set_language(self, lang: str) -> None:
        self._language = lang

    def listen_once(self, timeout: float = 5.0, phrase_limit: float = 15.0) -> str | None:
        """Listen to microphone and return transcribed text, or None on failure."""
        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit,
                )
            lang_code = self._lang_codes.get(self._language, "tr-TR")
            text = self._recognizer.recognize_google(audio, language=lang_code)
            return text
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            return None
        except sr.RequestError as e:
            print(f"[STT Error] {e}")
            return None


class TextToSpeech:
    """Human-like TTS powered by edge-tts (free & unlimited)."""

    def __init__(self, language: str = "tr") -> None:
        self._language = language
        self._is_speaking = False

    def set_language(self, lang: str) -> None:
        self._language = lang

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def speak(self, text: str, callback=None) -> None:
        """Speak text in a background thread. Calls callback() when done."""
        thread = threading.Thread(target=self._speak_sync, args=(text, callback), daemon=True)
        thread.start()

    def _speak_sync(self, text: str, callback=None) -> None:
        self._is_speaking = True
        try:
            asyncio.run(self._synthesize_and_play(text))
        except Exception as e:
            print(f"[TTS Error] {e}")
        finally:
            self._is_speaking = False
            if callback:
                callback()

    async def _synthesize_and_play(self, text: str) -> None:
        voice = config.TTS_VOICES.get(self._language, "en-GB-RyanNeural")
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=config.TTS_RATE,
            volume=config.TTS_VOLUME,
        )

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        await communicate.save(tmp_path)

        if HAS_PYDUB:
            audio = AudioSegment.from_mp3(tmp_path)
            pydub_play(audio)
        else:
            # Fallback: use system player
            import subprocess
            import sys
            if sys.platform == "win32":
                import os
                os.startfile(tmp_path)
            else:
                subprocess.run(["mpv", "--no-video", tmp_path], capture_output=True)

        Path(tmp_path).unlink(missing_ok=True)
