"""
Attc Jarvis Termux - Voice Engine
===================================
STT via Termux-API (termux-microphone-record + Google STT)
TTS via edge-tts (free, unlimited) played through Termux (mpv/play-audio)
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import edge_tts

import config


class TermuxSTT:
    """Speech-to-Text using Termux microphone API + Google Speech Recognition."""

    def __init__(self, language: str = "tr") -> None:
        self._language = language
        self._lang_codes = {"tr": "tr-TR", "en": "en-US"}

    def set_language(self, lang: str) -> None:
        self._language = lang

    def listen_once(self, duration: int = 0) -> str | None:
        """
        Record audio via termux-microphone-record, then transcribe.
        If duration=0, uses config default.
        """
        duration = duration or config.RECORDING_DURATION
        tmp_wav = os.path.join(tempfile.gettempdir(), "jarvis_rec.wav")

        try:
            # Start recording
            subprocess.run(
                [
                    "termux-microphone-record",
                    "-f", tmp_wav,
                    "-l", str(duration),
                    "-r", str(config.RECORDING_SAMPLE_RATE),
                    "-c", str(config.RECORDING_CHANNELS),
                    "-e", "aac",
                ],
                timeout=duration + 5,
                capture_output=True,
            )

            # Wait for recording to finish
            time.sleep(duration + 1)

            # Stop recording (in case it's still going)
            subprocess.run(
                ["termux-microphone-record", "-q"],
                capture_output=True,
                timeout=3,
            )

            if not Path(tmp_wav).exists() or Path(tmp_wav).stat().st_size < 1000:
                return None

            # Transcribe using SpeechRecognition if available
            return self._transcribe_file(tmp_wav)

        except FileNotFoundError:
            # termux-microphone-record not found — not on Termux or API not installed
            return self._fallback_input()
        except Exception as e:
            print(f"[STT Error] {e}")
            return None
        finally:
            Path(tmp_wav).unlink(missing_ok=True)

    def _transcribe_file(self, filepath: str) -> str | None:
        """Transcribe a WAV file using SpeechRecognition."""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(filepath) as source:
                audio = recognizer.record(source)
            lang_code = self._lang_codes.get(self._language, "tr-TR")
            return recognizer.recognize_google(audio, language=lang_code)
        except ImportError:
            # SpeechRecognition not installed, try Termux speech-to-text
            return self._termux_stt(filepath)
        except Exception:
            return None

    def _termux_stt(self, filepath: str) -> str | None:
        """Fallback: use termux-speech-to-text API."""
        try:
            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            text = result.stdout.strip()
            return text if text else None
        except Exception:
            return None

    def _fallback_input(self) -> str | None:
        """Terminal text input fallback when no mic is available."""
        return None  # Will be handled by the UI layer


class TermuxTTS:
    """Text-to-Speech via edge-tts, playback via mpv or play-audio."""

    def __init__(self, language: str = "tr") -> None:
        self._language = language
        self._is_speaking = False
        self._player = self._detect_player()

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def set_language(self, lang: str) -> None:
        self._language = lang

    def speak(self, text: str, callback=None) -> None:
        thread = threading.Thread(target=self._speak_sync, args=(text, callback), daemon=True)
        thread.start()

    def speak_blocking(self, text: str) -> None:
        """Synchronous speak — blocks until done."""
        self._speak_sync(text)

    def _speak_sync(self, text: str, callback=None) -> None:
        self._is_speaking = True
        try:
            asyncio.run(self._synthesize_and_play(text))
        except Exception as e:
            # Fallback: use termux-tts-speak
            self._termux_tts_fallback(text)
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

        tmp_path = os.path.join(tempfile.gettempdir(), "jarvis_tts.mp3")
        await communicate.save(tmp_path)

        self._play_audio(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)

    def _play_audio(self, filepath: str) -> None:
        """Play audio file using available player."""
        try:
            if self._player == "play-audio":
                subprocess.run(["play-audio", filepath], capture_output=True, timeout=60)
            elif self._player == "mpv":
                subprocess.run(["mpv", "--no-video", "--really-quiet", filepath], capture_output=True, timeout=60)
            elif self._player == "termux-media-player":
                subprocess.run(["termux-media-player", "play", filepath], capture_output=True, timeout=60)
                time.sleep(3)  # rough wait
            else:
                # Last resort: pydub
                from pydub import AudioSegment
                from pydub.playback import play
                audio = AudioSegment.from_mp3(filepath)
                play(audio)
        except Exception as e:
            print(f"[Audio Playback Error] {e}")

    def _termux_tts_fallback(self, text: str) -> None:
        """Fallback: use Android's built-in TTS via Termux API."""
        try:
            subprocess.run(
                ["termux-tts-speak", "-l", self._language, text],
                capture_output=True,
                timeout=30,
            )
        except Exception:
            pass  # silently fail if nothing works

    def _detect_player(self) -> str:
        """Detect which audio player is available on this Termux install."""
        for player in ["play-audio", "mpv", "termux-media-player"]:
            try:
                result = subprocess.run(["which", player], capture_output=True, text=True)
                if result.returncode == 0:
                    return player
            except Exception:
                continue
        return "pydub"
