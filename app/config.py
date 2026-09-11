"""
config.py - Configuration Manager supporting 4, 6, and 12 RTSP Channels
Features intelligent dual-stream resolution (102 for live grid, 101 for fullscreen).
"""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "rtsp_viewer"
CONFIG_FILE = CONFIG_DIR / "config.json"

MAX_CHANNELS = 12
SUPPORTED_STREAM_COUNTS = [4, 6, 12]

DEFAULT_CONFIG = {
    "channels": [
        {
            "id": i,
            "name": f"Kamera {i + 1}",
            "url": "",
            "auto_connect": True
        }
        for i in range(MAX_CHANNELS)
    ],
    "general": {
        "stream_count": 4,
        "auto_reconnect": True,
        "reconnect_interval_sec": 4
    }
}


def resolve_stream_url(url: str, is_fullscreen: bool) -> str:
    """
    Intelligently select stream endpoint:
    - is_fullscreen=False (Live Grid): uses stream 102 (Sub Stream / SD) for low CPU & bandwidth.
    - is_fullscreen=True (Fullscreen View): uses stream 101 (Main Stream / HD) for crystal clear video.
    """
    url = url.strip()
    if not url:
        return ""

    if is_fullscreen:
        # Main Stream 101 (HD)
        if "/102" in url:
            return url.replace("/102", "/101", 1)
        elif "subtype=1" in url:
            return url.replace("subtype=1", "subtype=0", 1)
        elif "/stream2" in url:
            return url.replace("/stream2", "/stream1", 1)
        return url
    else:
        # Sub Stream 102 (SD)
        if "/101" in url:
            return url.replace("/101", "/102", 1)
        elif "subtype=0" in url:
            return url.replace("subtype=0", "subtype=1", 1)
        elif "/stream1" in url:
            return url.replace("/stream1", "/stream2", 1)
        return url


def load_config() -> dict:
    """Load configuration from file, or return default. Preserves existing channels."""
    config = dict(DEFAULT_CONFIG)
    config["channels"] = [dict(ch) for ch in DEFAULT_CONFIG["channels"]]
    config["general"] = dict(DEFAULT_CONFIG["general"])

    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)

                # Merge saved general settings
                if "general" in saved:
                    config["general"].update(saved["general"])
                    sc = config["general"].get("stream_count", 4)
                    if sc not in SUPPORTED_STREAM_COUNTS:
                        config["general"]["stream_count"] = 4

                # Merge saved channels preserving existing URLs and names
                if "channels" in saved and isinstance(saved["channels"], list):
                    for i, saved_ch in enumerate(saved["channels"]):
                        if i < MAX_CHANNELS and isinstance(saved_ch, dict):
                            config["channels"][i]["name"] = saved_ch.get("name", f"Kamera {i + 1}")
                            config["channels"][i]["url"] = saved_ch.get("url", "")
                            config["channels"][i]["auto_connect"] = saved_ch.get("auto_connect", True)
                return config
    except Exception as e:
        print(f"[Config] Memuat default karena: {e}")

    return config


def save_config(config: dict) -> bool:
    """Save configuration to disk."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Config] Gagal menyimpan: {e}")
        return False
