"""
Attc Jarvis - Browser Automation
==================================
Selenium/Playwright based browser control for media and web tasks.
New automation functions can be added easily by extending this module.
"""

from __future__ import annotations

import time
import urllib.parse
from typing import Callable

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


class BrowserController:
    """Controls a Chromium browser for media playback and web automation."""

    def __init__(self) -> None:
        self._playwright = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    # ── Lifecycle ─────────────────────────────────────────

    def launch(self) -> None:
        if not HAS_PLAYWRIGHT:
            raise RuntimeError("Playwright is not installed. Run: playwright install chromium")
        if self._browser:
            return
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=False)
        self._page = self._browser.new_page()

    def close(self) -> None:
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        self._page = None

    def _ensure_page(self) -> Page:
        if not self._page or self._page.is_closed():
            self.launch()
        return self._page

    # ── Media Functions ───────────────────────────────────

    def play_media(self, platform: str, query: str) -> str:
        """Play media on the given platform."""
        platform = platform.lower().strip()
        if platform in ("youtube", "yt"):
            return self._play_youtube(query)
        elif platform in ("spotify",):
            return self._play_spotify(query)
        else:
            return self._play_youtube(query)  # default fallback

    def media_control(self, action: str) -> str:
        """Control playback: pause, resume, next, previous, stop."""
        page = self._ensure_page()
        url = page.url.lower()

        action = action.lower().strip()

        if "youtube" in url:
            return self._youtube_control(page, action)
        elif "spotify" in url:
            return self._spotify_control(page, action)
        else:
            return f"No active media session found for action: {action}"

    def web_search(self, query: str) -> str:
        """Perform a Google search."""
        page = self._ensure_page()
        encoded = urllib.parse.quote_plus(query)
        page.goto(f"https://www.google.com/search?q={encoded}")
        page.wait_for_load_state("domcontentloaded")
        return f"Searched for: {query}"

    def open_website(self, url: str) -> str:
        """Navigate to a URL."""
        page = self._ensure_page()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        return f"Opened: {url}"

    # ── Platform-specific implementations ─────────────────

    def _play_youtube(self, query: str) -> str:
        page = self._ensure_page()
        encoded = urllib.parse.quote_plus(query)
        page.goto(f"https://www.youtube.com/results?search_query={encoded}")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        # Click the first video result
        try:
            first_video = page.locator("ytd-video-renderer a#video-title").first
            first_video.click()
            page.wait_for_load_state("domcontentloaded")
            return f"Playing on YouTube: {query}"
        except Exception:
            return f"Could not play: {query}"

    def _play_spotify(self, query: str) -> str:
        page = self._ensure_page()
        encoded = urllib.parse.quote_plus(query)
        page.goto(f"https://open.spotify.com/search/{encoded}")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        try:
            # Click the first play button in search results
            play_btn = page.locator('[data-testid="play-button"]').first
            play_btn.click()
            return f"Playing on Spotify: {query}"
        except Exception:
            return f"Could not play on Spotify: {query}. You may need to log in."

    def _youtube_control(self, page: Page, action: str) -> str:
        actions_map = {
            "pause": "document.querySelector('video')?.pause()",
            "resume": "document.querySelector('video')?.play()",
            "stop": "document.querySelector('video')?.pause()",
            "next": "document.querySelector('.ytp-next-button')?.click()",
            "previous": "window.history.back()",
        }
        js = actions_map.get(action)
        if js:
            page.evaluate(js)
            return f"YouTube: {action} executed."
        return f"Unknown action: {action}"

    def _spotify_control(self, page: Page, action: str) -> str:
        actions_map = {
            "pause": '[data-testid="control-button-playpause"]',
            "resume": '[data-testid="control-button-playpause"]',
            "next": '[data-testid="control-button-skip-forward"]',
            "previous": '[data-testid="control-button-skip-back"]',
            "stop": '[data-testid="control-button-playpause"]',
        }
        selector = actions_map.get(action)
        if selector:
            try:
                page.locator(selector).first.click()
                return f"Spotify: {action} executed."
            except Exception:
                return f"Spotify: could not execute {action}."
        return f"Unknown action: {action}"


# ── Dispatch function called by the Brain ─────────────────

_browser: BrowserController | None = None


def get_browser() -> BrowserController:
    global _browser
    if _browser is None:
        _browser = BrowserController()
    return _browser


def execute_function(name: str, args: dict) -> str:
    """Execute a browser automation function by name."""
    browser = get_browser()

    dispatch = {
        "play_media": lambda: browser.play_media(args.get("platform", "youtube"), args.get("query", "")),
        "media_control": lambda: browser.media_control(args.get("action", "")),
        "web_search": lambda: browser.web_search(args.get("query", "")),
        "open_website": lambda: browser.open_website(args.get("url", "")),
    }

    handler = dispatch.get(name)
    if handler:
        try:
            browser.launch()
            return handler()
        except Exception as e:
            return f"Automation error: {e}"
    return f"Unknown function: {name}"
