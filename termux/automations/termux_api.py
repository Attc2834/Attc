"""
Attc Jarvis Termux - Device Automation
========================================
Leverages Termux-API for native Android functionality:
  - URL/app opening
  - Notifications
  - Clipboard
  - Device info (battery, wifi, etc.)
  - Media playback via intent

Easily extensible: add new functions and register them in execute_function().
"""

from __future__ import annotations

import json
import subprocess
import urllib.parse


def play_media(platform: str, query: str) -> str:
    """Open a media search in the default browser / app."""
    platform = platform.lower().strip()

    if platform in ("youtube", "yt"):
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
    elif platform in ("spotify",):
        encoded = urllib.parse.quote_plus(query)
        url = f"https://open.spotify.com/search/{encoded}"
    else:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"

    return open_url(url)


def web_search(query: str) -> str:
    """Perform a Google search in the browser."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    return open_url(url)


def open_url(url: str) -> str:
    """Open a URL using termux-open-url (opens in default browser)."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        subprocess.run(["termux-open-url", url], capture_output=True, timeout=5)
        return f"Açıldı: {url}"
    except FileNotFoundError:
        # Fallback: use am (Android Activity Manager)
        try:
            subprocess.run(
                ["am", "start", "-a", "android.intent.action.VIEW", "-d", url],
                capture_output=True,
                timeout=5,
            )
            return f"Açıldı: {url}"
        except Exception as e:
            return f"URL açılamadı: {e}"
    except Exception as e:
        return f"Hata: {e}"


def set_alarm(minutes: int, label: str = "Jarvis Alarm") -> str:
    """Set a timer/alarm via Termux notification (simple approach)."""
    try:
        # Schedule a notification after N minutes using `at` or simple approach
        seconds = minutes * 60
        subprocess.Popen(
            ["bash", "-c", f'sleep {seconds} && termux-notification --title "Jarvis Alarm" --content "{label}"'],
        )
        return f"Alarm kuruldu: {minutes} dakika sonra — {label}"
    except Exception as e:
        return f"Alarm kurulamadı: {e}"


def send_notification(title: str, message: str) -> str:
    """Show an Android notification via Termux-API."""
    try:
        subprocess.run(
            ["termux-notification", "--title", title, "--content", message],
            capture_output=True,
            timeout=5,
        )
        return f"Bildirim gönderildi: {title}"
    except FileNotFoundError:
        return "termux-notification bulunamadı. 'pkg install termux-api' çalıştırın."
    except Exception as e:
        return f"Bildirim hatası: {e}"


def device_info(info_type: str) -> str:
    """Get device information via Termux-API."""
    info_type = info_type.lower().strip()

    results = []

    if info_type in ("battery", "all"):
        results.append(_get_battery_info())

    if info_type in ("wifi", "all"):
        results.append(_get_wifi_info())

    if info_type in ("volume", "all"):
        results.append(_get_volume_info())

    return "\n".join(results) if results else "Bilinmeyen bilgi türü."


def clipboard_action(action: str, text: str = "") -> str:
    """Get or set clipboard content."""
    action = action.lower().strip()

    if action == "get":
        try:
            result = subprocess.run(
                ["termux-clipboard-get"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            content = result.stdout.strip()
            return f"Panodaki metin: {content}" if content else "Pano boş."
        except Exception as e:
            return f"Pano okunamadı: {e}"

    elif action == "set":
        try:
            subprocess.run(
                ["termux-clipboard-set", text],
                capture_output=True,
                timeout=5,
            )
            return f"Panoya kopyalandı: {text[:50]}..."
        except Exception as e:
            return f"Panoya yazılamadı: {e}"

    return f"Bilinmeyen pano işlemi: {action}"


# ── Helper functions ──────────────────────────────────────

def _get_battery_info() -> str:
    try:
        result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        data = json.loads(result.stdout)
        pct = data.get("percentage", "?")
        status = data.get("status", "?")
        return f"Batarya: %{pct} ({status})"
    except Exception:
        return "Batarya bilgisi alınamadı."


def _get_wifi_info() -> str:
    try:
        result = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True, timeout=5)
        data = json.loads(result.stdout)
        ssid = data.get("ssid", "?")
        rssi = data.get("rssi", "?")
        return f"WiFi: {ssid} (Sinyal: {rssi} dBm)"
    except Exception:
        return "WiFi bilgisi alınamadı."


def _get_volume_info() -> str:
    try:
        result = subprocess.run(["termux-volume"], capture_output=True, text=True, timeout=5)
        data = json.loads(result.stdout)
        lines = []
        for stream in data:
            name = stream.get("stream", "?")
            vol = stream.get("volume", "?")
            mx = stream.get("max_volume", "?")
            lines.append(f"  {name}: {vol}/{mx}")
        return "Ses Seviyeleri:\n" + "\n".join(lines)
    except Exception:
        return "Ses bilgisi alınamadı."


# ── Function Dispatch ─────────────────────────────────────

def execute_function(name: str, args: dict) -> str:
    """Execute a Termux automation function by name."""
    dispatch = {
        "play_media": lambda: play_media(args.get("platform", "youtube"), args.get("query", "")),
        "web_search": lambda: web_search(args.get("query", "")),
        "open_url": lambda: open_url(args.get("url", "")),
        "set_alarm": lambda: set_alarm(int(args.get("minutes", 5)), args.get("label", "Jarvis Alarm")),
        "send_notification": lambda: send_notification(args.get("title", "Jarvis"), args.get("message", "")),
        "device_info": lambda: device_info(args.get("info_type", "all")),
        "clipboard_action": lambda: clipboard_action(args.get("action", "get"), args.get("text", "")),
    }

    handler = dispatch.get(name)
    if handler:
        try:
            return handler()
        except Exception as e:
            return f"Otomasyon hatası: {e}"
    return f"Bilinmeyen fonksiyon: {name}"
