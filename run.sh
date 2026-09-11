#!/usr/bin/env bash
# Launcher script for RTSP Multi-View

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"

# Check for ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "[Error] FFmpeg tidak ditemukan! Harap pasang ffmpeg terlebih dahulu."
    exit 1
fi

python3 "$SCRIPT_DIR/main.py" "$@"
