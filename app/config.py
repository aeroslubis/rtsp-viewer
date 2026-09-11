"""
config.py - Configuration Manager supporting 4, 6, and 12 RTSP Channels
Defaults strictly to TCP for maximum stability and low latency.
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
                    # Validate stream_count
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
