"""
config.py - Simplified Configuration Manager for 4 RTSP Channels
Defaults strictly to TCP for maximum stability and low latency.
"""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "rtsp_viewer"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "channels": [
        {
            "id": 0,
            "name": "Kamera 1",
            "url": "",
            "auto_connect": True
        },
        {
            "id": 1,
            "name": "Kamera 2",
            "url": "",
            "auto_connect": True
        },
        {
            "id": 2,
            "name": "Kamera 3",
            "url": "",
            "auto_connect": True
        },
        {
            "id": 3,
            "name": "Kamera 4",
            "url": "",
            "auto_connect": True
        }
    ],
    "general": {
        "auto_reconnect": True,
        "reconnect_interval_sec": 4
    }
}


def load_config() -> dict:
    """Load configuration from file, or return default."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config = dict(DEFAULT_CONFIG)
                if "channels" in saved and len(saved["channels"]) == 4:
                    config["channels"] = saved["channels"]
                if "general" in saved:
                    config["general"].update(saved["general"])
                return config
    except Exception as e:
        print(f"[Config] Memuat default karena: {e}")
    return dict(DEFAULT_CONFIG)


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
