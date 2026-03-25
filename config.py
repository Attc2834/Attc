"""
Attc Jarvis AI Assistant - Configuration
=========================================
Central configuration for API keys, paths, and settings.
"""

# ── API Keys ──────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyAkXETk_EonGb7FkjTKGWCeipxVTXoCs30"

# Picovoice (Porcupine) - Free tier key (get yours at https://console.picovoice.ai/)
PORCUPINE_ACCESS_KEY = ""

# ── Application Settings ─────────────────────────────────
APP_NAME = "Attc Jarvis"
APP_VERSION = "1.0.0"
DEFAULT_LANGUAGE = "tr"  # "tr" or "en"

# ── Voice Settings ────────────────────────────────────────
TTS_VOICES = {
    "tr": "tr-TR-AhmetNeural",
    "en": "en-GB-RyanNeural",
}
TTS_RATE = "-5%"
TTS_VOLUME = "+0%"

# ── Persona / Personality ────────────────────────────────
PERSONA = {
    "tr": {
        "title_prefix": "Bay",
        "greeting": "Emrinize amadeyim, {title} {name}.",
        "farewell": "Her zaman hizmetinizdeyim, {title} {name}.",
        "system_prompt": (
            "Sen 'Jarvis' adında, Attc markasına ait bir yapay zeka asistanısın. "
            "Kişiliğin Batman'deki Alfred Pennyworth gibidir: Son derece sadık, kibar, "
            "resmi ve yerinde ince mizah yaparsın. Kullanıcıya her zaman '{title} {name}' "
            "diye hitap edersin. Yanıtlarını kısa ve öz tut. Türkçe konuş."
        ),
    },
    "en": {
        "title_prefix": "Mr.",
        "greeting": "At your service, {title} {name}.",
        "farewell": "Always at your disposal, {title} {name}.",
        "system_prompt": (
            "You are 'Jarvis', an AI assistant belonging to the Attc brand. "
            "Your personality mirrors Alfred Pennyworth from Batman: Utterly loyal, "
            "polished, formal, and capable of dry wit when appropriate. Always address "
            "the user as '{title} {name}'. Keep responses concise. Speak in English."
        ),
    },
}

# ── User Profile ──────────────────────────────────────────
USER_NAME = "Kullanıcı"

# ── Conversation Memory ──────────────────────────────────
MEMORY_BUFFER_SIZE = 20  # Number of recent messages to keep

# ── Paths ─────────────────────────────────────────────────
WAKE_WORD_KEYWORD = "jarvis"
