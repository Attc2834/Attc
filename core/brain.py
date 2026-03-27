"""
Attc Jarvis - AI Brain (Gemini Integration)
=============================================
Handles communication with Google Gemini API including function calling.
"""

from __future__ import annotations

import google.generativeai as genai

import config
from core.memory import ConversationMemory


# ── Function declarations for Gemini Function Calling ─────

BROWSER_FUNCTIONS = [
    genai.protos.FunctionDeclaration(
        name="play_media",
        description=(
            "Play a song or video on a streaming platform. "
            "Use this when the user asks to play music, a song, or a video. "
            "Examples: 'Spotify'dan Müslüm Gürses çal', 'YouTube'da lofi müzik aç', 'play some jazz'"
        ),
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "platform": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Platform name: 'spotify' or 'youtube'. Default to 'youtube' if not specified.",
                ),
                "query": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The song, artist, or video to search for",
                ),
            },
            required=["platform", "query"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="media_control",
        description=(
            "Control currently playing media. "
            "Use this when the user says: 'durdur/pause', 'devam et/resume', "
            "'sonraki/next', 'önceki/previous', 'kapat/stop'"
        ),
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "action": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="One of: pause, resume, next, previous, stop",
                ),
            },
            required=["action"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="web_search",
        description=(
            "Search the web via Google. "
            "Use when user asks to search, look up, or find information online."
        ),
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "query": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The search query",
                ),
            },
            required=["query"],
        ),
    ),
    genai.protos.FunctionDeclaration(
        name="open_website",
        description=(
            "Open a specific website URL in the browser. "
            "Use when user says 'open google.com', 'go to twitter', etc."
        ),
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "url": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The URL to open (e.g. 'google.com', 'https://twitter.com')",
                ),
            },
            required=["url"],
        ),
    ),
]


class JarvisBrain:
    """Central AI engine backed by Gemini with function calling."""

    def __init__(self, language: str = "tr", user_name: str = "Kullanıcı") -> None:
        self._language = language
        self._user_name = user_name
        self._memory = ConversationMemory(max_size=config.MEMORY_BUFFER_SIZE)

        genai.configure(api_key=config.GEMINI_API_KEY)

        self._tool = genai.protos.Tool(function_declarations=BROWSER_FUNCTIONS)
        self._rebuild_model()

    # ── Public API ────────────────────────────────────────

    def set_language(self, lang: str) -> None:
        self._language = lang
        self._rebuild_model()
        self._chat = self._model.start_chat(history=self._memory.get_history())

    def set_user_name(self, name: str) -> None:
        self._user_name = name
        self._rebuild_model()
        self._chat = self._model.start_chat(history=self._memory.get_history())

    def think(self, user_input: str) -> tuple[str, dict | None]:
        """
        Process user input synchronously.
        Returns (text_response, None) for text answers.
        Returns (function_name, args_dict) for function calls.
        """
        self._memory.add("user", user_input)

        response = self._chat.send_message(user_input)

        # Check for function calls
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if fn := part.function_call:
                    args = dict(fn.args)
                    self._memory.add("model", f"[Function: {fn.name}({args})]")
                    return fn.name, args

        # Regular text response
        text = response.text
        self._memory.add("model", text)
        return text, None

    def reset_memory(self) -> None:
        self._memory.clear()
        self._chat = self._model.start_chat(history=[])

    # ── Private ───────────────────────────────────────────

    def _rebuild_model(self) -> None:
        self._model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=[self._tool],
            system_instruction=self._build_system_prompt(),
        )
        self._chat = self._model.start_chat(history=[])

    def _build_system_prompt(self) -> str:
        persona = config.PERSONA[self._language]
        title = persona["title_prefix"]
        return persona["system_prompt"].format(title=title, name=self._user_name)
