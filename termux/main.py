"""
Attc Jarvis AI Assistant — Termux Edition
===========================================
Premium terminal-based AI assistant for Android/Termux.

Usage:
    python main.py
"""

from __future__ import annotations

import sys
import threading
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style as PTStyle

import config
from core.brain import JarvisBrain
from core.voice import TermuxTTS, TermuxSTT
from core.listener import TermuxListener, ListenMode
from automations.termux_api import execute_function
from utils.helpers import get_greeting

# ── Rich Console ──────────────────────────────────────────
console = Console()

# ── Prompt Toolkit Style ──────────────────────────────────
pt_style = PTStyle.from_dict({
    "prompt": "#6C63FF bold",
    "": "#E8E8F0",
})


class AttcJarvisTermux:
    """Terminal-based Jarvis interface for Termux."""

    def __init__(self) -> None:
        self._language = config.DEFAULT_LANGUAGE
        self._user_name = config.USER_NAME
        self._listen_mode = ListenMode.WAKE_WORD
        self._voice_enabled = True
        self._mic_active = False

        # Core engines
        self._brain = JarvisBrain(language=self._language, user_name=self._user_name)
        self._tts = TermuxTTS(language=self._language)
        self._stt = TermuxSTT(language=self._language)
        self._listener = TermuxListener(
            mode=self._listen_mode,
            language=self._language,
            on_command=self._on_voice_command,
            on_status=self._on_listener_status,
        )

        self._chat_history: list[tuple[str, str, str]] = []  # (time, sender, text)
        self._prompt_history = InMemoryHistory()

    # ══════════════════════════════════════════════════════
    #  MAIN LOOP
    # ══════════════════════════════════════════════════════

    def run(self) -> None:
        self._show_banner()
        self._show_help()

        # Welcome message
        greeting = get_greeting(self._language, self._user_name)
        self._display_jarvis(greeting)
        self._tts.speak(greeting)

        while True:
            try:
                user_input = prompt(
                    [("class:prompt", "\n❯ ")],
                    style=pt_style,
                    history=self._prompt_history,
                ).strip()

                if not user_input:
                    continue

                # Handle slash commands
                if user_input.startswith("/"):
                    if self._handle_command(user_input):
                        continue
                    if user_input == "/quit":
                        break

                self._display_user(user_input)
                self._process(user_input)

            except (KeyboardInterrupt, EOFError):
                self._exit_gracefully()
                break

    # ══════════════════════════════════════════════════════
    #  SLASH COMMANDS
    # ══════════════════════════════════════════════════════

    def _handle_command(self, cmd: str) -> bool:
        parts = cmd.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        handlers = {
            "/help":     lambda: self._show_help(),
            "/lang":     lambda: self._switch_language(arg),
            "/name":     lambda: self._set_name(arg),
            "/mode":     lambda: self._switch_mode(arg),
            "/mic":      lambda: self._toggle_mic(),
            "/voice":    lambda: self._toggle_voice(),
            "/clear":    lambda: self._clear_chat(),
            "/history":  lambda: self._show_history(),
            "/status":   lambda: self._show_status(),
            "/quit":     lambda: self._exit_gracefully(),
        }

        handler = handlers.get(command)
        if handler:
            handler()
            return command != "/quit"
        return False

    # ══════════════════════════════════════════════════════
    #  PROCESSING
    # ══════════════════════════════════════════════════════

    def _process(self, text: str) -> None:
        with console.status("[bold #6C63FF]Düşünüyor...", spinner="dots"):
            try:
                result, func_call = self._brain.think(text)
            except Exception as e:
                self._display_jarvis(f"Bir hata oluştu: {e}")
                return

        if func_call is not None:
            func_name = result
            console.print(f"  [dim #FFB347]⚡ Çalıştırılıyor: {func_name}...[/]")
            response = execute_function(func_name, func_call)
        else:
            response = result

        self._display_jarvis(response)

        if self._voice_enabled:
            self._tts.speak(response)

    # ══════════════════════════════════════════════════════
    #  VOICE CALLBACKS
    # ══════════════════════════════════════════════════════

    def _on_voice_command(self, text: str) -> None:
        console.print(f"\n  [bold #00D9A5]🎤 Sesli komut:[/] {text}")
        self._display_user(text)
        self._process(text)

    def _on_listener_status(self, status: str) -> None:
        console.print(f"  [dim #8888AA]📡 {status}[/]")

    # ══════════════════════════════════════════════════════
    #  DISPLAY HELPERS
    # ══════════════════════════════════════════════════════

    def _display_user(self, text: str) -> None:
        ts = datetime.now().strftime("%H:%M")
        self._chat_history.append((ts, "Siz", text))
        console.print(Panel(
            Text(text, style="#E8E8F0"),
            title=f"[bold #6C63FF]Siz[/] [dim]{ts}[/]",
            border_style="#2A2A40",
            padding=(0, 2),
            expand=False,
        ))

    def _display_jarvis(self, text: str) -> None:
        ts = datetime.now().strftime("%H:%M")
        self._chat_history.append((ts, "Jarvis", text))
        console.print(Panel(
            Text(text, style="#B8B0FF"),
            title=f"[bold #9D4EDD]Jarvis[/] [dim]{ts}[/]",
            border_style="#6C63FF",
            padding=(0, 2),
            expand=False,
        ))

    def _show_banner(self) -> None:
        banner = Text()
        banner.append("\n")
        banner.append("    ╔═══════════════════════════════════════╗\n", style="bold #6C63FF")
        banner.append("    ║                                       ║\n", style="bold #6C63FF")
        banner.append("    ║", style="bold #6C63FF")
        banner.append("       ATTC ", style="bold #6C63FF")
        banner.append("JARVIS", style="bold #9D4EDD")
        banner.append("                ║\n", style="bold #6C63FF")
        banner.append("    ║", style="bold #6C63FF")
        banner.append("       AI Assistant · Termux", style="dim #8888AA")
        banner.append("       ║\n", style="bold #6C63FF")
        banner.append("    ║                                       ║\n", style="bold #6C63FF")
        banner.append("    ╚═══════════════════════════════════════╝\n", style="bold #6C63FF")
        console.print(banner)
        console.print(f"    [dim #8888AA]v{config.APP_VERSION}[/]\n")

    def _show_help(self) -> None:
        table = Table(
            title="[bold #6C63FF]Komutlar[/]",
            box=box.ROUNDED,
            border_style="#2A2A40",
            title_style="bold #6C63FF",
            show_header=True,
            header_style="bold #9D4EDD",
        )
        table.add_column("Komut", style="#B8B0FF", width=18)
        table.add_column("Açıklama", style="#E8E8F0")

        commands = [
            ("/help", "Bu yardım menüsünü göster"),
            ("/lang tr|en", "Dil değiştir (Türkçe/İngilizce)"),
            ("/name <isim>", "İsminizi ayarlayın"),
            ("/mode wake|always", "Dinleme modunu değiştir"),
            ("/mic", "Mikrofonu aç/kapat"),
            ("/voice", "Sesli yanıtı aç/kapat"),
            ("/status", "Sistem durumunu göster"),
            ("/history", "Sohbet geçmişini göster"),
            ("/clear", "Sohbeti temizle"),
            ("/quit", "Çıkış"),
        ]
        for cmd, desc in commands:
            table.add_row(cmd, desc)

        console.print()
        console.print(table)
        console.print("  [dim #8888AA]Veya doğrudan yazarak Jarvis ile konuşun.[/]\n")

    def _show_status(self) -> None:
        mode_label = "Seslenince Dinle" if self._listen_mode == ListenMode.WAKE_WORD else "Her Zaman Dinle"
        lang_label = "Türkçe" if self._language == "tr" else "English"

        table = Table(
            title="[bold #6C63FF]Sistem Durumu[/]",
            box=box.ROUNDED,
            border_style="#2A2A40",
        )
        table.add_column("Ayar", style="#9D4EDD", width=20)
        table.add_column("Değer", style="#E8E8F0")

        status_items = [
            ("Kullanıcı", f"{config.PERSONA[self._language]['title_prefix']} {self._user_name}"),
            ("Dil", lang_label),
            ("Dinleme Modu", mode_label),
            ("Mikrofon", "Aktif" if self._mic_active else "Kapalı"),
            ("Sesli Yanıt", "Açık" if self._voice_enabled else "Kapalı"),
            ("Hafıza", f"{self._brain._memory.size} mesaj"),
            ("Versiyon", config.APP_VERSION),
        ]
        for key, val in status_items:
            table.add_row(key, val)

        console.print()
        console.print(table)

    def _show_history(self) -> None:
        if not self._chat_history:
            console.print("  [dim]Henüz sohbet geçmişi yok.[/]")
            return

        console.print("\n[bold #6C63FF]─── Sohbet Geçmişi ───[/]")
        for ts, sender, text in self._chat_history[-20:]:
            color = "#6C63FF" if sender == "Siz" else "#9D4EDD"
            console.print(f"  [dim]{ts}[/] [bold {color}]{sender}:[/] {text[:100]}")
        console.print("[bold #6C63FF]──────────────────────[/]\n")

    # ══════════════════════════════════════════════════════
    #  SETTINGS
    # ══════════════════════════════════════════════════════

    def _switch_language(self, lang: str) -> None:
        lang = lang.strip().lower()
        if lang not in ("tr", "en"):
            console.print("  [#FF6B6B]Geçersiz dil. Kullanım: /lang tr veya /lang en[/]")
            return
        self._language = lang
        self._brain.set_language(lang)
        self._tts.set_language(lang)
        self._stt.set_language(lang)
        self._listener.set_language(lang)
        msg = "Dil Türkçe olarak ayarlandı." if lang == "tr" else "Language set to English."
        console.print(f"  [#00D9A5]✓ {msg}[/]")

    def _set_name(self, name: str) -> None:
        name = name.strip()
        if not name:
            console.print("  [#FF6B6B]Kullanım: /name <isim>[/]")
            return
        self._user_name = name
        config.USER_NAME = name
        self._brain.set_user_name(name)
        greeting = get_greeting(self._language, self._user_name)
        self._display_jarvis(greeting)
        self._tts.speak(greeting)

    def _switch_mode(self, mode: str) -> None:
        mode = mode.strip().lower()
        if mode in ("wake", "wake_word"):
            self._listen_mode = ListenMode.WAKE_WORD
            self._listener.set_mode(ListenMode.WAKE_WORD)
            console.print("  [#00D9A5]✓ Mod: Seslenince Dinle[/]")
        elif mode in ("always", "always_on"):
            self._listen_mode = ListenMode.ALWAYS_ON
            self._listener.set_mode(ListenMode.ALWAYS_ON)
            console.print("  [#00D9A5]✓ Mod: Her Zaman Dinle[/]")
        else:
            console.print("  [#FF6B6B]Kullanım: /mode wake veya /mode always[/]")

    def _toggle_mic(self) -> None:
        if self._mic_active:
            self._listener.stop()
            self._mic_active = False
            console.print("  [#FFB347]🎤 Mikrofon kapatıldı.[/]")
        else:
            self._listener.start()
            self._mic_active = True
            console.print("  [#00D9A5]🎤 Mikrofon açıldı.[/]")

    def _toggle_voice(self) -> None:
        self._voice_enabled = not self._voice_enabled
        state = "açıldı" if self._voice_enabled else "kapatıldı"
        console.print(f"  [#00D9A5]🔊 Sesli yanıt {state}.[/]")

    def _clear_chat(self) -> None:
        self._chat_history.clear()
        self._brain.reset_memory()
        console.clear()
        self._show_banner()
        console.print("  [#00D9A5]✓ Sohbet temizlendi.[/]")

    def _exit_gracefully(self) -> None:
        self._listener.stop()
        farewell = config.PERSONA[self._language]["farewell"].format(
            title=config.PERSONA[self._language]["title_prefix"],
            name=self._user_name,
        )
        self._display_jarvis(farewell)
        if self._voice_enabled:
            self._tts.speak_blocking(farewell)
        console.print("\n  [dim #8888AA]Attc Jarvis kapatılıyor...[/]\n")


# ── Entry Point ───────────────────────────────────────────

def main() -> None:
    app = AttcJarvisTermux()
    app.run()


if __name__ == "__main__":
    main()
