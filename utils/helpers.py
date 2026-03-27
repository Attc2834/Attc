"""
Attc Jarvis - Utility Helpers
"""

from __future__ import annotations

import config


def get_greeting(language: str, user_name: str) -> str:
    persona = config.PERSONA[language]
    title = persona["title_prefix"]
    return persona["greeting"].format(title=title, name=user_name)


def get_farewell(language: str, user_name: str) -> str:
    persona = config.PERSONA[language]
    title = persona["title_prefix"]
    return persona["farewell"].format(title=title, name=user_name)
