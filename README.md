# RTSP Multi-View - Minimalist Multi-Stream Linux GUI

Aplikasi GUI Linux minimalis, elegan, dan berkinerja tinggi untuk menampilkan **4, 6, atau 12 stream RTSP IP Camera / CCTV** secara bersamaan dalam tata letak kisi (*clean grid*).

Dibangun dengan **Python 3**, **PyQt5**, dan **FFmpeg** dengan decoding *low-latency* hemat CPU serta ikon vektor SVG modern.

---

## Fitur Utama

- **Pilihan Grid Fleksibel (4, 6, 12 Stream)**:
  - **4 Stream (2x2 Grid)**: 2 baris x 2 kolom (tampilan standar 4 kamera).
  - **6 Stream (2x3 Grid)**: 2 baris x 3 kolom (tampilan 6 kamera format widescreen).
  - **12 Stream (3x4 Grid)**: 3 baris x 4 kolom (tampilan 12 kamera monitoring penuh).
- **Pengaturan Cepat & Praktis**:
  - Ganti layout langsung dari **Klik Kanan Mouse -> Tata Letak Grid** atau melalui dialog **Pengaturan Kamera (F2)**.
  - Jumlah tab kamera di menu pengaturan otomatis menyesuaikan dengan jumlah stream yang dipilih (4, 6, atau 12 tab).
- **Deteksi Resolusi Otomatis**:
  - Otomatis mendeteksi resolusi asli kamera (720p, 1080p, 4K, dll.) langsung dari data frame stream.
- **Transport TCP Default**:
  - Menggunakan protokol TCP untuk transmisi stabil tanpa gangguan frame rusak (*packet loss*).
- **Tombol Uji Stream Terintegrasi**:
  - Tombol **Uji Stream** dengan ikon pencarian di samping setiap URL RTSP untuk mengecek koneksi, codec, dan resolusi kamera seketika.
- **Auto-Reconnect & Clean Shutdown**:
  - Otomatis menyambungkan ulang jika kamera sempat offline, dan langsung tertutup bersih saat aplikasi di-close tanpa terminal macet.

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

## Tombol Pintas (*Shortcuts*) & Menu

- **F2** atau **Ctrl+,** : Buka menu Pengaturan Kamera RTSP.
- **Klik Kanan Mouse** : Buka menu konteks untuk:
  - Mengubah layout grid (4 Stream, 6 Stream, 12 Stream)
  - Membuka Pengaturan Kamera
  - Hubungkan Ulang Semua
  - Hentikan Semua
  - Keluar
