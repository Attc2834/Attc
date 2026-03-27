"""
Attc Jarvis - Main Desktop Application UI
============================================
Premium dark-mode branded interface using CustomTkinter.
"""

from __future__ import annotations

import threading
from datetime import datetime

import customtkinter as ctk

import config
from ui.theme import COLORS, FONTS
from core.brain import JarvisBrain
from core.voice import TextToSpeech
from core.listener import ListenerEngine, ListenMode
from automations.browser import execute_function
from utils.helpers import get_greeting


class AttcJarvisApp(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        # ── Window Setup ──────────────────────────────────
        self.title(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.geometry("1000x700")
        self.minsize(800, 600)
        self.configure(fg_color=COLORS["bg_primary"])

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # ── State ─────────────────────────────────────────
        self._language = config.DEFAULT_LANGUAGE
        self._user_name = config.USER_NAME
        self._listen_mode = ListenMode.WAKE_WORD
        self._is_listening = False

        # ── Core Engines ──────────────────────────────────
        self._brain = JarvisBrain(language=self._language, user_name=self._user_name)
        self._tts = TextToSpeech(language=self._language)
        self._listener = ListenerEngine(
            mode=self._listen_mode,
            language=self._language,
            on_command=self._on_voice_command,
            on_status=self._on_listener_status,
        )

        # ── Build UI ──────────────────────────────────────
        self._build_header()
        self._build_main_area()
        self._build_input_bar()

        # ── Welcome Message ───────────────────────────────
        greeting = get_greeting(self._language, self._user_name)
        self._add_message("Jarvis", greeting)
        self._tts.speak(greeting)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ══════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ══════════════════════════════════════════════════════

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=70, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Brand
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.pack(side="left", padx=20)

        ctk.CTkLabel(
            brand_frame,
            text="ATTC",
            font=("Segoe UI", 26, "bold"),
            text_color=COLORS["accent_primary"],
        ).pack(side="left")

        ctk.CTkLabel(
            brand_frame,
            text="  JARVIS",
            font=("Segoe UI", 20),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")

        # ── Right Controls ────────────────────────────────
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right", padx=20)

        # Language selector
        self._lang_var = ctk.StringVar(value="Türkçe")
        lang_menu = ctk.CTkOptionMenu(
            controls,
            variable=self._lang_var,
            values=["Türkçe", "English"],
            command=self._on_language_change,
            width=120,
            fg_color=COLORS["bg_tertiary"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_secondary"],
            font=FONTS["small"],
        )
        lang_menu.pack(side="left", padx=5)

        # User name entry
        self._name_entry = ctk.CTkEntry(
            controls,
            placeholder_text="İsminiz...",
            width=130,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            font=FONTS["small"],
        )
        self._name_entry.pack(side="left", padx=5)
        self._name_entry.bind("<Return>", self._on_name_change)

        # Mic status indicator
        self._mic_indicator = ctk.CTkLabel(
            controls,
            text="\u25CF",
            font=("Segoe UI", 18),
            text_color=COLORS["mic_idle"],
        )
        self._mic_indicator.pack(side="left", padx=10)

    def _build_main_area(self) -> None:
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=(10, 5))

        # ── Chat Area ─────────────────────────────────────
        chat_frame = ctk.CTkFrame(main, fg_color=COLORS["bg_secondary"], corner_radius=12)
        chat_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        chat_header = ctk.CTkFrame(chat_frame, fg_color="transparent", height=40)
        chat_header.pack(fill="x", padx=15, pady=(10, 0))
        chat_header.pack_propagate(False)

        ctk.CTkLabel(
            chat_header,
            text="Konuşma Geçmişi",
            font=FONTS["subheading"],
            text_color=COLORS["text_accent"],
        ).pack(side="left")

        clear_btn = ctk.CTkButton(
            chat_header,
            text="Temizle",
            width=70,
            height=28,
            font=FONTS["small"],
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["accent_error"],
            command=self._clear_chat,
        )
        clear_btn.pack(side="right")

        self._chat_box = ctk.CTkTextbox(
            chat_frame,
            fg_color=COLORS["bg_primary"],
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
            corner_radius=8,
            wrap="word",
            state="disabled",
        )
        self._chat_box.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Side Panel ────────────────────────────────────
        side = ctk.CTkFrame(main, fg_color=COLORS["bg_secondary"], width=250, corner_radius=12)
        side.pack(side="right", fill="y", padx=(8, 0))
        side.pack_propagate(False)

        ctk.CTkLabel(
            side,
            text="Kontrol Paneli",
            font=FONTS["subheading"],
            text_color=COLORS["text_accent"],
        ).pack(pady=(15, 10))

        # Listen mode selector
        ctk.CTkLabel(
            side,
            text="Dinleme Modu",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack(pady=(10, 5))

        self._mode_var = ctk.StringVar(value="wake_word")
        modes = [
            ("Seslenince Dinle", "wake_word"),
            ("Her Zaman Dinle", "always_on"),
        ]
        for label, value in modes:
            ctk.CTkRadioButton(
                side,
                text=label,
                variable=self._mode_var,
                value=value,
                font=FONTS["small"],
                fg_color=COLORS["accent_primary"],
                hover_color=COLORS["accent_secondary"],
                command=self._on_mode_change,
            ).pack(pady=3, padx=20, anchor="w")

        # Mic toggle
        self._mic_btn = ctk.CTkButton(
            side,
            text="Mikrofonu Aç",
            font=FONTS["button"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            height=42,
            corner_radius=10,
            command=self._toggle_mic,
        )
        self._mic_btn.pack(pady=20, padx=20, fill="x")

        # Status
        self._status_label = ctk.CTkLabel(
            side,
            text="Hazır",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            wraplength=200,
        )
        self._status_label.pack(pady=10, padx=15)

        # Separator
        ctk.CTkFrame(side, fg_color=COLORS["border"], height=1).pack(fill="x", padx=20, pady=10)

        # Version
        ctk.CTkLabel(
            side,
            text=f"v{config.APP_VERSION}",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack(side="bottom", pady=10)

    def _build_input_bar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=60, corner_radius=0)
        bar.pack(fill="x", padx=0, pady=0, side="bottom")
        bar.pack_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=10)

        self._input_entry = ctk.CTkEntry(
            inner,
            placeholder_text="Bir mesaj yazın veya mikrofonu kullanın...",
            font=FONTS["body"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            corner_radius=10,
            height=38,
        )
        self._input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._input_entry.bind("<Return>", self._on_text_submit)

        send_btn = ctk.CTkButton(
            inner,
            text="Gönder",
            font=FONTS["button"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            width=90,
            height=38,
            corner_radius=10,
            command=lambda: self._on_text_submit(None),
        )
        send_btn.pack(side="right")

    # ══════════════════════════════════════════════════════
    #  EVENT HANDLERS
    # ══════════════════════════════════════════════════════

    def _on_language_change(self, choice: str) -> None:
        self._language = "en" if choice == "English" else "tr"
        self._brain.set_language(self._language)
        self._tts.set_language(self._language)
        self._listener.set_language(self._language)
        status = "Language switched to English." if self._language == "en" else "Dil Türkçe olarak değiştirildi."
        self._set_status(status)

    def _on_name_change(self, event=None) -> None:
        name = self._name_entry.get().strip()
        if name:
            self._user_name = name
            config.USER_NAME = name
            self._brain.set_user_name(name)
            greeting = get_greeting(self._language, self._user_name)
            self._add_message("Jarvis", greeting)
            self._tts.speak(greeting)

    def _on_mode_change(self) -> None:
        mode_str = self._mode_var.get()
        self._listen_mode = ListenMode.ALWAYS_ON if mode_str == "always_on" else ListenMode.WAKE_WORD
        self._listener.set_mode(self._listen_mode)
        label = "Her Zaman Dinle" if mode_str == "always_on" else "Seslenince Dinle"
        self._set_status(f"Mod: {label}")

    def _toggle_mic(self) -> None:
        if self._is_listening:
            self._listener.stop()
            self._is_listening = False
            self._mic_btn.configure(text="Mikrofonu Aç", fg_color=COLORS["accent_primary"])
            self._mic_indicator.configure(text_color=COLORS["mic_idle"])
            self._set_status("Mikrofon kapatıldı.")
        else:
            self._listener.start()
            self._is_listening = True
            self._mic_btn.configure(text="Mikrofonu Kapat", fg_color=COLORS["accent_error"])
            self._mic_indicator.configure(text_color=COLORS["mic_active"])
            self._set_status("Mikrofon açıldı.")

    def _on_text_submit(self, event) -> None:
        text = self._input_entry.get().strip()
        if not text:
            return
        self._input_entry.delete(0, "end")
        self._process_command(text)

    def _on_voice_command(self, text: str) -> None:
        self.after(0, lambda: self._process_command(text))

    def _on_listener_status(self, status: str) -> None:
        self.after(0, lambda: self._set_status(status))

    # ══════════════════════════════════════════════════════
    #  COMMAND PROCESSING
    # ══════════════════════════════════════════════════════

    def _process_command(self, text: str) -> None:
        self._add_message("Siz", text)
        self._set_status("Düşünüyor...")
        self._mic_indicator.configure(text_color=COLORS["mic_processing"])

        thread = threading.Thread(target=self._background_process, args=(text,), daemon=True)
        thread.start()

    def _background_process(self, text: str) -> None:
        try:
            result, func_call = self._brain.think(text)

            if func_call is not None:
                func_name = result
                self.after(0, lambda: self._set_status(f"Çalıştırılıyor: {func_name}..."))
                response = execute_function(func_name, func_call)
            else:
                response = result

            self.after(0, lambda: self._add_message("Jarvis", response))
            self.after(0, lambda: self._set_status("Hazır"))
            self.after(0, lambda: self._mic_indicator.configure(
                text_color=COLORS["mic_active"] if self._is_listening else COLORS["mic_idle"]
            ))

            self._tts.speak(response)

        except Exception as e:
            error_msg = f"Bir hata oluştu: {e}"
            self.after(0, lambda: self._add_message("Jarvis", error_msg))
            self.after(0, lambda: self._set_status("Hata!"))

    # ══════════════════════════════════════════════════════
    #  UI HELPERS
    # ══════════════════════════════════════════════════════

    def _add_message(self, sender: str, text: str) -> None:
        timestamp = datetime.now().strftime("%H:%M")
        self._chat_box.configure(state="normal")
        self._chat_box.insert("end", f"\n[{timestamp}] {sender}:\n{text}\n")
        self._chat_box.configure(state="disabled")
        self._chat_box.see("end")

    def _set_status(self, text: str) -> None:
        self._status_label.configure(text=text)

    def _clear_chat(self) -> None:
        self._chat_box.configure(state="normal")
        self._chat_box.delete("1.0", "end")
        self._chat_box.configure(state="disabled")
        self._brain.reset_memory()

    def _on_close(self) -> None:
        self._listener.stop()
        try:
            from automations.browser import _browser
            if _browser:
                _browser.close()
        except Exception:
            pass
        self.destroy()
