# RTSP Multi-View - Minimalist 4-Stream Linux GUI

Aplikasi GUI Linux minimalis dan berkinerja tinggi untuk menampilkan **4 stream RTSP IP Camera / CCTV** secara bersamaan dalam tata letak kisi 2x2 (*clean grid*).

Dibangun dengan **Python 3**, **PyQt5**, dan **FFmpeg** dengan decoding *low-latency* hemat CPU.

---

## Fitur Utama

- **Tampilan Bersih & Minimalis (2x2 Grid)**:
  - Murni menampilkan 4 kotak stream video tanpa top bar, toolbar, ataupun tombol-tombol yang mengganggu.
  - Label nama kamera dan resolusi stream otomatis ditampilkan secara halus di pojok kiri atas setiap video.
- **Deteksi Resolusi Otomatis**:
  - Aplikasi secara otomatis mendeteksi resolusi dan format stream (misal: 1280x720, 1920x1080, dll.) tanpa perlu memilih resolusi secara manual.
- **Pengaturan URL RTSP Simpel**:
  - Cukup **klik kanan** pada kotak kamera mana saja (atau tekan tombol **F2** / **Ctrl+,**) untuk membuka menu pengaturan.
  - Setiap kamera hanya memiliki input **Nama Kamera**, **URL RTSP**, tombol **🔍 Uji Stream**, dan pilihan **Transport (TCP/UDP)**.
- **Tombol Uji Stream Terintegrasi**:
  - Tombol **🔍 Uji Stream** terletak tepat di samping input URL stream dan langsung mendeteksi ketersediaan stream, codec, serta resolusinya.
- **Auto-Reconnect**:
  - Otomatis mencoba menyambungkan ulang jika kamera atau jaringan sempat terputus.

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

- **F2** atau **Ctrl+,** : Buka menu Pengaturan URL RTSP.
- **Klik Kanan Mouse** : Buka menu konteks (Pengaturan, Hubungkan Ulang, Hentikan, Keluar).
