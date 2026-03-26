"""
Attc Jarvis Termux - AI Brain (Gemini)
========================================
Gemini integration with function calling for Termux.
"""

from __future__ import annotations

import google.generativeai as genai

import config
from core.memory import ConversationMemory


TERMUX_FUNCTIONS = [
    genai.protos.FunctionDeclaration(
        name="play_media",
        description="Play a song or video on a streaming platform (Spotify, YouTube, etc.)",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "platform": genai.protos.Schema(type=genai.protos.Type.STRING, description="Platform: spotify, youtube"),
                "query": genai.protos.Schema(type=genai.protos.Type.STRING, description="Search query"),
            },
            required=["platform", "query"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="web_search",
        description="Search the web for information",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "query": genai.protos.Schema(type=genai.protos.Type.STRING, description="Search query"),
            },
            required=["query"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="open_url",
        description="Open a URL in the device browser",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "url": genai.protos.Schema(type=genai.protos.Type.STRING, description="URL to open"),
            },
            required=["url"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="set_alarm",
        description="Set an alarm or timer on the device",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "minutes": genai.protos.Schema(type=genai.protos.Type.INTEGER, description="Minutes from now"),
                "label": genai.protos.Schema(type=genai.protos.Type.STRING, description="Alarm label"),
            },
            required=["minutes"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="send_notification",
        description="Show a notification on the device",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "title": genai.protos.Schema(type=genai.protos.Type.STRING, description="Notification title"),
                "message": genai.protos.Schema(type=genai.protos.Type.STRING, description="Notification body"),
            },
            required=["title", "message"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="device_info",
        description="Get device information (battery, wifi, volume, etc.)",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "info_type": genai.protos.Schema(type=genai.protos.Type.STRING, description="One of: battery, wifi, volume, all"),
            },
            required=["info_type"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="clipboard_action",
        description="Get or set clipboard content",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "action": genai.protos.Schema(type=genai.protos.Type.STRING, description="get or set"),
                "text": genai.protos.Schema(type=genai.protos.Type.STRING, description="Text to set (only for set action)"),
            },
            required=["action"],
        ),
    ),
]


class JarvisBrain:
    """Central AI engine for Termux version."""

    def __init__(self, language: str = "tr", user_name: str = "Kullanıcı") -> None:
        self._language = language
        self._user_name = user_name
        self._memory = ConversationMemory(max_size=config.MEMORY_BUFFER_SIZE)

        genai.configure(api_key=config.GEMINI_API_KEY)

        self._tool = genai.protos.Tool(function_declarations=TERMUX_FUNCTIONS)
        self._model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=[self._tool],
            system_instruction=self._build_system_prompt(),
        )
        self._chat = self._model.start_chat(history=[])

    def set_language(self, lang: str) -> None:
        self._language = lang
        self._model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=[self._tool],
            system_instruction=self._build_system_prompt(),
        )
        self._chat = self._model.start_chat(history=self._memory.get_history())

    def set_user_name(self, name: str) -> None:
        self._user_name = name

    def think(self, user_input: str) -> tuple[str, dict | None]:
        """Process input. Returns (response_text, function_call_dict_or_None)."""
        self._memory.add("user", user_input)

        response = self._chat.send_message(user_input)

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if fn := part.function_call:
                    args = dict(fn.args)
                    self._memory.add("model", f"[Function: {fn.name}({args})]")
                    return fn.name, args

        text = response.text
        self._memory.add("model", text)
        return text, None

    def reset_memory(self) -> None:
        self._memory.clear()
        self._chat = self._model.start_chat(history=[])

    def _build_system_prompt(self) -> str:
        persona = config.PERSONA[self._language]
        title = persona["title_prefix"]
        prompt = persona["system_prompt"].format(title=title, name=self._user_name)
        # Add Termux context
        prompt += (
            "\n\nKullanıcı bir Android cihazda Termux üzerinden seninle konuşuyor. "
            "Cihaz üzerinde bildirim gönderme, URL açma, alarm kurma, pano (clipboard) "
            "işlemleri, cihaz bilgisi sorgulama gibi işlemler yapabilirsin."
        )
        return prompt
