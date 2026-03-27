"""
Attc Jarvis AI Assistant
=========================
Premium AI desktop assistant branded for Attc.

Usage:
    python main.py
"""

from ui.app import AttcJarvisApp


def main() -> None:
    app = AttcJarvisApp()
    app.mainloop()


if __name__ == "__main__":
    main()
