# RTSP Multi-View - Minimalist Multi-Stream Linux GUI

Aplikasi GUI Linux minimalis, elegan, dan berkinerja tinggi untuk menampilkan **4, 6, atau 12 stream RTSP IP Camera / CCTV** secara bersamaan dalam tata letak kisi (*clean grid*).

Dibangun dengan **Python 3**, **PyQt5**, dan **FFmpeg** dengan fitur pintar **Dual-Stream (102 SD saat Live Grid & 101 HD saat Fullscreen)** untuk performa decoding optimal dan hemat resource.

---

## Fitur Unggulan

- **Smart Dual-Stream Switching (102 SD vs 101 HD)**:
  - **Saat Live Grid**: Menggunakan **Stream 102** (Sub Stream SD, misal `352x288`) untuk memastikan pemutaran 4, 6, atau 12 stream berjalan sangat ringan, lancar, dan hemat bandwidth.
  - **Saat Fullscreen / Zoom Kamera**: Cukup **klik ganda (*double-click*)** pada kamera mana saja, kamera tersebut akan membesar penuh dan otomatis beralih ke **Stream 101** (Main Stream HD, misal `1280x720` / `1080p`) dengan kualitas super jernih.
  - Kamera lain otomatis dihentikan sementara saat salah satu kamera di-zoom (hemat 100% CPU!).
  - Klik ganda kembali atau tekan **Escape** untuk kembali ke grid (otomatis kembali ke Stream 102).
- **Pilihan Grid 4, 6, 12 Stream yang Rapi**:
  - **2 × 2 Grid  (4 Stream)**: 2 baris × 2 kolom.
  - **2 × 3 Grid  (6 Stream)**: 2 baris × 3 kolom.
  - **3 × 4 Grid  (12 Stream)**: 3 baris × 4 kolom.
- **Menu Dropdown Rapi & Elegan**:
  - Menu pilihan grid diatur dengan penataan teks yang rapi dan ikon panah modern.
  - Bisa diganti seketika dari menu **Klik Kanan Mouse -> Tata Letak Grid** atau dari dialog **Pengaturan Kamera (F2)**.
- **Deteksi Resolusi Otomatis**:
  - Aplikasi secara dinamis mengenali resolusi asli stream tanpa perlu memilih resolusi secara manual.
- **Transport TCP Default**:
  - Menggunakan protokol TCP untuk transmisi stabil tanpa gangguan frame rusak (*packet loss*).
- **Tombol Uji Stream Terintegrasi**:
  - Dilengkapi tombol **Uji Stream** di samping URL RTSP untuk mengecek koneksi, codec, dan resolusi seketika.
- **Auto-Reconnect & Penutupan Cepat (No-Hang)**:
  - Otomatis menyambungkan ulang jika kamera sempat offline, dan jendela langsung tertutup bersih saat di-close (~0.01 detik).

---

## Cara Menjalankan

Melalui terminal:
```bash
cd /home/aeros/Work/rtsp_viewer
./run.sh
```

Atau langsung:
```bash
python3 /home/aeros/Work/rtsp_viewer/main.py
```

---

## Tombol Pintas (*Shortcuts*) & Navigasi

- **Klik Ganda Mouse pada Video** : Beralih antara Fullscreen Kamera Tunggal (Stream 101 HD) dan Tampilan Grid (Stream 102 SD).
- **Escape** : Kembali dari fullscreen kamera tunggal ke tampilan grid.
- **F2** atau **Ctrl+,** : Buka menu Pengaturan Kamera RTSP.
- **Klik Kanan Mouse** : Buka menu konteks untuk:
  - Mengubah Tata Letak Grid (2×2, 2×3, 3×4)
  - Perbesar Kamera (Stream 101 HD) / Kembali ke Grid (Stream 102 SD)
  - Pengaturan Kamera
  - Hubungkan Ulang Semua
  - Hentikan Semua
  - Keluar
