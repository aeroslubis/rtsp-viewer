# RTSP Multi-View - Minimalist 4-Stream Linux GUI

Aplikasi GUI Linux minimalis, elegan, dan berkinerja tinggi untuk menampilkan **4 stream RTSP IP Camera / CCTV** secara bersamaan dalam tata letak kisi 2x2 (*clean grid*).

Dibangun dengan **Python 3**, **PyQt5**, dan **FFmpeg** dengan decoding *low-latency* hemat CPU serta ikon vektor SVG modern.

---

## Fitur Utama

- **Tampilan Bersih & Minimalis (2x2 Grid)**:
  - Murni 4 kotak stream video tanpa top bar, status bar, maupun tombol-tombol yang mengganggu.
  - Pembatas 2px yang rapi antar kotak video.
  - Label nama kamera dan resolusi asli stream (*auto-detected*) ditampilkan secara halus di pojok kiri atas setiap video.
- **Deteksi Resolusi Otomatis**:
  - Aplikasi secara dinamis mendeteksi resolusi video kamera (1280x720, 1080p, 4K, dll.) langsung dari data frame.
- **Transport TCP Default**:
  - Otomatis menggunakan protokol TCP untuk menjamin koneksi RTSP stabil tanpa *packet loss* atau garis abu-abu.
- **Menu Pengaturan Rapi & Modern**:
  - Tampilan dialog ramping berbasis tab berikon untuk setiap kamera.
  - Tombol **🔍 Uji Stream** berada tepat sejajar di samping input URL stream untuk memverifikasi koneksi seketika.
- **Ikon Vektor Modern**:
  - Dilengkapi ikon SVG berkualitas tinggi untuk tab kamera, tombol aksi, menu klik kanan, dan launcher desktop.
- **Auto-Reconnect**:
  - Otomatis menyambungkan ulang jika kamera atau koneksi jaringan sempat terputus.

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

## Tombol Pintas (*Shortcuts*)

- **F2** atau **Ctrl+,** : Buka menu Pengaturan Kamera RTSP.
- **Klik Kanan Mouse** : Buka menu konteks berikon (Pengaturan, Hubungkan Ulang, Hentikan, Keluar).
