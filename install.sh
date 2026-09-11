#!/usr/bin/env bash
# ==============================================================================
# install.sh - Installer & Desktop Integrator for RTSP Multi-View
# ==============================================================================

set -e

# ANSI Color formatting
GREEN='\033[0;32m'
SKY='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="RTSP Multi-View"
DESKTOP_FILENAME="rtsp-viewer.desktop"
CMD_NAME="rtsp-viewer"

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
APPS_DIR="$DATA_HOME/applications"
BIN_DIR="$HOME/.local/bin"
ICON_SCALABLE_DIR="$DATA_HOME/icons/hicolor/scalable/apps"
ICON_256_DIR="$DATA_HOME/icons/hicolor/256x256/apps"

show_help() {
    echo -e "${SKY}Penggunaan:${NC}"
    echo "  ./install.sh             Pasang aplikasi ke menu desktop dan ~/.local/bin"
    echo "  ./install.sh --uninstall Hapus aplikasi dari menu desktop dan ~/.local/bin"
    echo "  ./install.sh --help      Tampilkan panduan ini"
}

check_dependencies() {
    echo -e "${SKY}[1/4] Memeriksa dependensi sistem...${NC}"
    local missing=0

    # 1. Python 3
    if command -v python3 &>/dev/null; then
        local py_ver
        py_ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
        echo -e "  ${GREEN}✓${NC} Python $py_ver ditemukan"
    else
        echo -e "  ${RED}✗ Python 3 tidak ditemukan!${NC}"
        missing=1
    fi

    # 2. FFmpeg
    if command -v ffmpeg &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} FFmpeg ditemukan"
    else
        echo -e "  ${RED}✗ FFmpeg tidak ditemukan!${NC}"
        missing=1
    fi

    # 3. PyQt5
    if python3 -c "import PyQt5" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} PyQt5 modul Python ditemukan"
    else
        echo -e "  ${YELLOW}⚠ Modul PyQt5 belum terpasang untuk python3!${NC}"
        echo -e "    Pasang paket PyQt5 melalui package manager distro Anda:"
        echo -e "    - Arch / Manjaro : ${SKY}sudo pacman -S python-pyqt5${NC}"
        echo -e "    - Ubuntu / Debian: ${SKY}sudo apt install python3-pyqt5${NC}"
        echo -e "    - Fedora         : ${SKY}sudo dnf install python3-qt5${NC}"
        missing=1
    fi

    if [ "$missing" -ne 0 ]; then
        echo -e "${YELLOW}[Peringatan] Beberapa dependensi belum terpenuhi. Pastikan dependensi terpasang sebelum menjalankan aplikasi.${NC}\n"
    else
        echo -e "  ${GREEN}Semua dependensi utama terpenuhi!${NC}\n"
    fi
}

install_app() {
    echo -e "${SKY}========================================${NC}"
    echo -e "${SKY}   Memasang $APP_NAME   ${NC}"
    echo -e "${SKY}========================================${NC}\n"

    check_dependencies

    # Pastikan file script executable
    chmod +x "$APP_DIR/run.sh" "$APP_DIR/main.py"

    echo -e "${SKY}[2/4] Menyiapkan direktori tujuan...${NC}"
    mkdir -p "$APPS_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$ICON_SCALABLE_DIR"
    mkdir -p "$ICON_256_DIR"

    echo -e "${SKY}[3/4] Memasang ikon dan launcher desktop...${NC}"
    # Copy icons
    if [ -f "$APP_DIR/assets/icons/app_icon.svg" ]; then
        cp -f "$APP_DIR/assets/icons/app_icon.svg" "$ICON_SCALABLE_DIR/rtsp-viewer.svg"
    fi
    if [ -f "$APP_DIR/assets/app_icon.png" ]; then
        cp -f "$APP_DIR/assets/app_icon.png" "$ICON_256_DIR/rtsp-viewer.png"
    fi

    # Generate Desktop file with current resolved paths
    cat << DESKTOP_EOF > "$APPS_DIR/$DESKTOP_FILENAME"
[Desktop Entry]
Type=Application
Name=$APP_NAME
GenericName=CCTV RTSP Monitor
Comment=Linux GUI minimalis untuk menampilkan stream RTSP IP Camera
Exec=$APP_DIR/run.sh
Icon=rtsp-viewer
Terminal=false
Categories=AudioVideo;Video;Network;
Keywords=rtsp;cctv;ipcam;camera;stream;dahua;imou;hikvision;tapo;
StartupNotify=true
DESKTOP_EOF
    chmod +x "$APPS_DIR/$DESKTOP_FILENAME"

    echo -e "${SKY}[4/4] Memasang perintah '$CMD_NAME' ke $BIN_DIR...${NC}"
    # Create bin runner wrapper
    cat << RUNNER_EOF > "$BIN_DIR/$CMD_NAME"
#!/usr/bin/env bash
exec "$APP_DIR/run.sh" "\$@"
RUNNER_EOF
    chmod +x "$BIN_DIR/$CMD_NAME"

    # Refresh desktop database
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$APPS_DIR" 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -q -t "$DATA_HOME/icons/hicolor" 2>/dev/null || true
    fi

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}   Pemasangan Berhasil!   ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "Aplikasi sekarang dapat dijalankan dengan cara:"
    echo -e "  1. Dari Menu Aplikasi Linux / App Launcher (Cari: '${SKY}$APP_NAME${NC}')"
    echo -e "  2. Dari terminal: ketik ${SKY}$CMD_NAME${NC}"
    echo -e "  3. Langsung: ${SKY}./run.sh${NC}\n"

    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo -e "${YELLOW}[Catatan] Direktori $BIN_DIR belum ada di \$PATH Anda.${NC}"
        echo -e "Tambahkan baris berikut ke ~/.bashrc atau ~/.zshrc agar perintah '${CMD_NAME}' bisa dipanggil langsung:"
        echo -e "  ${SKY}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}\n"
    fi
}

uninstall_app() {
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}   Menghapus Pemasangan $APP_NAME   ${NC}"
    echo -e "${YELLOW}========================================${NC}\n"

    rm -f "$APPS_DIR/$DESKTOP_FILENAME"
    rm -f "$BIN_DIR/$CMD_NAME"
    rm -f "$ICON_SCALABLE_DIR/rtsp-viewer.svg"
    rm -f "$ICON_256_DIR/rtsp-viewer.png"

    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$APPS_DIR" 2>/dev/null || true
    fi

    echo -e "${GREEN}✓ File desktop, shortcut perintah, dan ikon berhasil dihapus.${NC}\n"
}

case "$1" in
    --uninstall|-u)
        uninstall_app
        ;;
    --help|-h)
        show_help
        ;;
    *)
        install_app
        ;;
esac
