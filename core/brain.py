"""
Attc Jarvis - AI Brain (Gemini Integration)
=============================================
Handles communication with Google Gemini API including function calling.
Uses the new google-genai SDK.
"""

from __future__ import annotations

from google import genai
from google.genai import types

import config
from core.memory import ConversationMemory


# ── Function declarations for Gemini Function Calling ─────

PLAY_MEDIA_FUNC = types.FunctionDeclaration(
    name="play_media",
    description=(
        "Play a song or video on a streaming platform. "
        "Use this when the user asks to play music, a song, or a video. "
        "Examples: 'Spotify'dan Müslüm Gürses çal', 'YouTube'da lofi müzik aç'"
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "platform": types.Schema(
                type=types.Type.STRING,
                description="Platform name: 'spotify' or 'youtube'. Default to 'youtube' if not specified.",
            ),
            "query": types.Schema(
                type=types.Type.STRING,
                description="The song, artist, or video to search for",
            ),
        },
        required=["platform", "query"],
    ),
)

MEDIA_CONTROL_FUNC = types.FunctionDeclaration(
    name="media_control",
    description=(
        "Control currently playing media. "
        "Use this when the user says: 'durdur/pause', 'devam et/resume', "
        "'sonraki/next', 'önceki/previous', 'kapat/stop'"
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "action": types.Schema(
                type=types.Type.STRING,
                description="One of: pause, resume, next, previous, stop",
            ),
        },
        required=["action"],
    ),
)

WEB_SEARCH_FUNC = types.FunctionDeclaration(
    name="web_search",
    description=(
        "Search the web via Google. "
        "Use when user asks to search, look up, or find information online."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description="The search query",
            ),
        },
        required=["query"],
    ),
)

OPEN_WEBSITE_FUNC = types.FunctionDeclaration(
    name="open_website",
    description=(
        "Open a specific website URL in the browser. "
        "Use when user says 'open google.com', 'go to twitter', etc."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "url": types.Schema(
                type=types.Type.STRING,
                description="The URL to open (e.g. 'google.com', 'https://twitter.com')",
            ),
        },
        required=["url"],
    ),
)

BROWSER_TOOLS = types.Tool(
    function_declarations=[
        PLAY_MEDIA_FUNC,
        MEDIA_CONTROL_FUNC,
        WEB_SEARCH_FUNC,
        OPEN_WEBSITE_FUNC,
    ]
)


class JarvisBrain:
    """Central AI engine backed by Gemini with function calling."""

    def __init__(self, language: str = "tr", user_name: str = "Kullanıcı") -> None:
        self._language = language
        self._user_name = user_name
        self._memory = ConversationMemory(max_size=config.MEMORY_BUFFER_SIZE)

        self._client = genai.Client(api_key=config.GEMINI_API_KEY)
        self._chat = None
        self._start_chat()

    # ── Public API ────────────────────────────────────────

    def set_language(self, lang: str) -> None:
        self._language = lang
        self._start_chat()
        # Replay memory into new chat
        for msg in self._memory.get_history():
            role = msg["role"]
            text = msg["parts"][0]
            if role == "user":
                try:
                    self._chat.send_message(text)
                except Exception:
                    pass

    def set_user_name(self, name: str) -> None:
        self._user_name = name
        self._start_chat()

    def think(self, user_input: str) -> tuple[str, dict | None]:
        """
        Process user input synchronously.
        Returns (text_response, None) for text answers.
        Returns (function_name, args_dict) for function calls.
        """
        self._memory.add("user", user_input)

        response = self._chat.send_message(user_input)

        # Check for function calls
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fn = part.function_call
                    args = dict(fn.args) if fn.args else {}
                    self._memory.add("model", f"[Function: {fn.name}({args})]")
                    return fn.name, args

        # Regular text response
        text = response.text
        self._memory.add("model", text)
        return text, None

    def reset_memory(self) -> None:
        self._memory.clear()
        self._start_chat()

    # ── Private ───────────────────────────────────────────

    def _start_chat(self) -> None:
        self._chat = self._client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=self._build_system_prompt(),
                tools=[BROWSER_TOOLS],
            ),
        )

    def _build_system_prompt(self) -> str:
        persona = config.PERSONA[self._language]
        title = persona["title_prefix"]
        return persona["system_prompt"].format(title=title, name=self._user_name)
