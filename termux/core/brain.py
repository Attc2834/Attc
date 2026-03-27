"""
Attc Jarvis Termux - AI Brain (Gemini)
========================================
Gemini integration with function calling for Termux.
Uses the new google-genai SDK.
"""

from __future__ import annotations

from google import genai
from google.genai import types

import config
from core.memory import ConversationMemory


# ── Function declarations ─────────────────────────────────

TERMUX_TOOLS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="play_media",
            description="Play a song or video on a streaming platform (Spotify, YouTube, etc.)",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "platform": types.Schema(type=types.Type.STRING, description="Platform: spotify, youtube"),
                    "query": types.Schema(type=types.Type.STRING, description="Search query"),
                },
                required=["platform", "query"],
            ),
        ),
        types.FunctionDeclaration(
            name="web_search",
            description="Search the web for information",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(type=types.Type.STRING, description="Search query"),
                },
                required=["query"],
            ),
        ),
        types.FunctionDeclaration(
            name="open_url",
            description="Open a URL in the device browser",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "url": types.Schema(type=types.Type.STRING, description="URL to open"),
                },
                required=["url"],
            ),
        ),
        types.FunctionDeclaration(
            name="set_alarm",
            description="Set an alarm or timer on the device",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "minutes": types.Schema(type=types.Type.INTEGER, description="Minutes from now"),
                    "label": types.Schema(type=types.Type.STRING, description="Alarm label"),
                },
                required=["minutes"],
            ),
        ),
        types.FunctionDeclaration(
            name="send_notification",
            description="Show a notification on the device",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "title": types.Schema(type=types.Type.STRING, description="Notification title"),
                    "message": types.Schema(type=types.Type.STRING, description="Notification body"),
                },
                required=["title", "message"],
            ),
        ),
        types.FunctionDeclaration(
            name="device_info",
            description="Get device information (battery, wifi, volume, etc.)",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "info_type": types.Schema(type=types.Type.STRING, description="One of: battery, wifi, volume, all"),
                },
                required=["info_type"],
            ),
        ),
        types.FunctionDeclaration(
            name="clipboard_action",
            description="Get or set clipboard content",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "action": types.Schema(type=types.Type.STRING, description="get or set"),
                    "text": types.Schema(type=types.Type.STRING, description="Text to set (only for set action)"),
                },
                required=["action"],
            ),
        ),
    ]
)


class JarvisBrain:
    """Central AI engine for Termux version."""

    def __init__(self, language: str = "tr", user_name: str = "Kullanıcı") -> None:
        self._language = language
        self._user_name = user_name
        self._memory = ConversationMemory(max_size=config.MEMORY_BUFFER_SIZE)

        self._client = genai.Client(api_key=config.GEMINI_API_KEY)
        self._start_chat()

    def set_language(self, lang: str) -> None:
        self._language = lang
        self._start_chat()

    def set_user_name(self, name: str) -> None:
        self._user_name = name
        self._start_chat()

    def think(self, user_input: str) -> tuple[str, dict | None]:
        """Process input. Returns (response_text, function_call_dict_or_None)."""
        self._memory.add("user", user_input)

        response = self._chat.send_message(user_input)

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fn = part.function_call
                    args = dict(fn.args) if fn.args else {}
                    self._memory.add("model", f"[Function: {fn.name}({args})]")
                    return fn.name, args

        text = response.text
        self._memory.add("model", text)
        return text, None

    def reset_memory(self) -> None:
        self._memory.clear()
        self._start_chat()

    def _start_chat(self) -> None:
        self._chat = self._client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=self._build_system_prompt(),
                tools=[TERMUX_TOOLS],
            ),
        )

    def _build_system_prompt(self) -> str:
        persona = config.PERSONA[self._language]
        title = persona["title_prefix"]
        prompt = persona["system_prompt"].format(title=title, name=self._user_name)
        prompt += (
            "\n\nKullanıcı bir Android cihazda Termux üzerinden seninle konuşuyor. "
            "Cihaz üzerinde bildirim gönderme, URL açma, alarm kurma, pano (clipboard) "
            "işlemleri, cihaz bilgisi sorgulama gibi işlemler yapabilirsin."
        )
        return prompt
