# RTSP Multi-View - Minimalist Multi-Stream Linux GUI

Aplikasi GUI Linux minimalis, elegan, dan berkinerja tinggi untuk menampilkan **4, 6, atau 12 stream RTSP IP Camera / CCTV** secara bersamaan dalam tata letak kisi (*clean grid*).

Dibangun dengan **Python 3**, **PyQt5**, dan **FFmpeg** dengan dukungan **URL Main Stream (101 HD) dan URL Sub Stream (102 SD)** untuk performa decoding optimal dan hemat resource.

---

## Fitur Unggulan

- **Input Terpisah URL Main Stream & Sub Stream**:
  - **URL Main Stream (101 / HD)**: Digunakan saat mode Fullscreen / Zoom kamera tunggal untuk resolusi tinggi yang tajam. Dilengkapi tombol **Uji Main**.
  - **URL Sub Stream (102 / SD)**: Digunakan saat mode Live Grid (4, 6, 12 kamera) untuk menghemat bandwidth jaringan dan penggunaan CPU. Dilengkapi tombol **Uji Sub**.
  - **Auto-Suggest**: Jika URL Main Stream diisi dengan `/101`, input Sub Stream otomatis merekomendasikan `/102`.
- **Pilihan Grid 4, 6, 12 Stream yang Rapi**:
  - **2 × 2 Grid  (4 Stream)**: 2 baris × 2 kolom.
  - **2 × 3 Grid  (6 Stream)**: 2 baris × 3 kolom.
  - **3 × 4 Grid  (12 Stream)**: 3 baris × 4 kolom.
- **Menu Dropdown Rapi & Elegan**:
  - Menu pilihan grid diatur rapi dengan ikon panah modern.
  - Bisa diganti seketika dari menu **Klik Kanan Mouse -> Tata Letak Grid** atau dari dialog **Pengaturan Kamera (F2)**.
- **Deteksi Resolusi Otomatis**:
  - Aplikasi secara dinamis mengenali resolusi asli stream tanpa perlu memilih resolusi manual.
- **Transport TCP Default**:
  - Menggunakan protokol TCP untuk transmisi stabil tanpa gangguan frame rusak (*packet loss*).
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

- **Klik Ganda Mouse pada Video** : Beralih antara Fullscreen Kamera Tunggal (Main Stream 101 HD) dan Tampilan Grid (Sub Stream 102 SD).
- **Escape** : Kembali dari fullscreen kamera tunggal ke tampilan grid.
- **F2** atau **Ctrl+,** : Buka menu Pengaturan Kamera RTSP.
- **Klik Kanan Mouse** : Buka menu konteks untuk:
  - Mengubah Tata Letak Grid (2×2, 2×3, 3×4)
  - Perbesar Kamera (Main Stream 101 HD) / Kembali ke Grid (Sub Stream 102 SD)
  - Pengaturan Kamera
  - Hubungkan Ulang Semua
  - Hentikan Semua
  - Keluar
