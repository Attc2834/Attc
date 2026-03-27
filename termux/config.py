"""
Attc Jarvis - Termux Configuration
====================================
Central configuration for the Termux-compatible version.
"""

# ── API Keys ──────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyAkXETk_EonGb7FkjTKGWCeipxVTXoCs30"

# ── Application ───────────────────────────────────────────
APP_NAME = "Attc Jarvis"
APP_VERSION = "1.0.0-termux"
DEFAULT_LANGUAGE = "tr"

# ── Voice Settings ────────────────────────────────────────
TTS_VOICES = {
    "tr": "tr-TR-AhmetNeural",
    "en": "en-GB-RyanNeural",
}
TTS_RATE = "-5%"
TTS_VOLUME = "+0%"

# Termux audio settings
RECORDING_DURATION = 7       # seconds per listen cycle
RECORDING_SAMPLE_RATE = 16000
RECORDING_CHANNELS = 1

# ── Persona ───────────────────────────────────────────────
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
MEMORY_BUFFER_SIZE = 20

# ── Wake Word ─────────────────────────────────────────────
WAKE_WORD_KEYWORD = "jarvis"
