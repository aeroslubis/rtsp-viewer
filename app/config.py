"""
config.py - Configuration Manager supporting Main Stream and Sub Stream URLs
Features 4, 6, and 12 RTSP Channels with distinct main (HD) and sub (SD) streams.
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
            "main_url": "",
            "sub_url": "",
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
    Intelligently fallback stream endpoint if sub_url is not explicitly provided:
    - is_fullscreen=False (Live Grid): converts 101 to 102.
    - is_fullscreen=True (Fullscreen View): converts 102 to 101.
    """
    url = url.strip()
    if not url:
        return ""

    if is_fullscreen:
        if "/102" in url:
            return url.replace("/102", "/101", 1)
        elif "subtype=1" in url:
            return url.replace("subtype=1", "subtype=0", 1)
        elif "/stream2" in url:
            return url.replace("/stream2", "/stream1", 1)
        return url
    else:
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

                # Merge saved channels
                if "channels" in saved and isinstance(saved["channels"], list):
                    for i, saved_ch in enumerate(saved["channels"]):
                        if i < MAX_CHANNELS and isinstance(saved_ch, dict):
                            config["channels"][i]["name"] = saved_ch.get("name", f"Kamera {i + 1}")
                            
                            # Support both legacy 'url' and new 'main_url'/'sub_url'
                            main_url = saved_ch.get("main_url", saved_ch.get("url", ""))
                            sub_url = saved_ch.get("sub_url", "")
                            
                            # If sub_url was empty but main_url has /101, auto-populate sub_url
                            if not sub_url and main_url and "/101" in main_url:
                                sub_url = main_url.replace("/101", "/102", 1)
                                
                            config["channels"][i]["main_url"] = main_url
                            config["channels"][i]["sub_url"] = sub_url
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
