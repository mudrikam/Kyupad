# Pinout ESP32-S3 Zero Super Mini untuk Macropad Grid 4x4

Macropad grid 4x4 menggunakan 16 tombol yang dihubungkan dalam konfigurasi matriks (4 baris x 4 kolom). Setiap tombol terhubung di antara satu pin baris dan satu pin kolom. ESP32-S3 Zero Super Mini menyediakan lebih banyak GPIO dan performa yang lebih tinggi untuk macropad yang responsif.

## Hal Penting dari Chip ESP32-S3 Zero Super Mini

ESP32-S3 Zero Super Mini adalah board berbasis chip ESP32-S3. Berikut fitur penting yang relevan untuk macropad:

- **Banyak GPIO**: Tersedia lebih banyak GPIO (hingga 20+ pin) untuk input/output, sangat cukup untuk kebutuhan macropad grid dan ekspansi fitur.
- **Dual-core Xtensa**: Prosesor dual-core Xtensa LX7 32-bit dengan clock hingga 240 MHz, respons sangat cepat untuk pembacaan tombol dan multitasking.
- **Memori Besar**: 512KB SRAM + 8MB PSRAM external, sangat cukup untuk firmware macropad kompleks dan buffer data.
- **Dukungan Interface**: Mendukung I2C, SPI, UART, PWM, ADC, serta WiFi dan BLE 5.0 untuk komunikasi nirkabel yang lebih stabil.
- **USB Native**: USB OTG native support, memudahkan HID implementation dan programming.
- **Low Power**: Konsumsi daya rendah dengan berbagai sleep mode, ideal untuk perangkat portable.
- **Bluetooth HID Optimized**: ESP32-S3 memiliki dukungan Bluetooth HID yang lebih baik dan stabil dibanding ESP32-C3.

Fitur-fitur ini membuat ESP32-S3 Zero Super Mini pilihan TERBAIK untuk proyek macropad Bluetooth HID yang membutuhkan banyak input, responsivitas tinggi, dan konektivitas stabil.

## Mengapa ESP32-S3 Zero Super Mini Sangat Cocok untuk Bluetooth HID Macropad?

**YA, ESP32-S3 Zero Super Mini SANGAT COCOK dan bahkan LEBIH BAIK dari ESP32-C3 untuk Bluetooth HID macropad!**

### Keunggulan ESP32-S3 untuk Bluetooth HID:

1. **Bluetooth 5.0 Native Support**: ESP32-S3 memiliki dukungan Bluetooth 5.0 yang lebih stabil dan konsumsi daya lebih rendah.

2. **Dual-Core Performance**: Dengan dual-core, satu core bisa menangani scanning matrix tombol, sementara core lainnya menangani komunikasi Bluetooth HID - menghasilkan responsivitas yang jauh lebih baik.

3. **USB Native**: ESP32-S3 memiliki USB OTG native, sehingga bisa berfungsi sebagai USB HID dan Bluetooth HID secara bersamaan (dual-mode).

4. **Memori Lebih Besar**: 512KB SRAM + 8MB PSRAM memberikan ruang lebih untuk buffer macro kompleks dan multiple HID profiles.

5. **GPIO Lebih Banyak**: Lebih banyak pin untuk ekspansi fitur seperti LED RGB, rotary encoder, atau layar OLED.

6. **Power Management Lebih Baik**: Sleep mode yang lebih efisien untuk battery life yang lebih lama.

### Perbandingan ESP32-C3 vs ESP32-S3 untuk Macropad:

| Fitur | ESP32-C3 Super Mini | ESP32-S3 Zero Super Mini |
|-------|---------------------|---------------------------|
| CPU | Single RISC-V 160MHz | Dual Xtensa 240MHz |
| RAM | 400KB | 512KB + 8MB PSRAM |
| Bluetooth | BLE 5.0 | BLE 5.0 (lebih stabil) |
| USB | USB Serial/JTAG | USB OTG Native |
| GPIO | ~10 pins | 20+ pins |
| HID Performance | Baik | Sangat Baik |
| Multi-tasking | Terbatas | Excellent |
| Battery Life | Baik | Sangat Baik |
| **Rekomendasi** | ✅ Cocok | 🏆 **TERBAIK** |

### Kesimpulan:
**ESP32-S3 Zero Super Mini adalah pilihan SUPERIOR untuk Bluetooth HID macropad!** Lebih responsif, lebih stabil, dan lebih banyak fitur untuk project macropad yang advanced.

## Modul TP4056 dan Ilustrasi Baterai

Untuk membuat macropad portabel, dapat ditambahkan modul TP4056 sebagai charger baterai Li-ion/LiPo. Modul TP4056 berfungsi untuk mengisi baterai secara aman melalui port micro USB dan menyediakan proteksi overcharge/overdischarge.

### Skema Koneksi TP4056 dan Baterai

```
+-------------------+      +-------------------+      +-------------------+
|   USB Power IN    | ---> |   TP4056 Charger  | ---> |   Baterai Li-ion  |
+-------------------+      +-------------------+      +-------------------+
                                   |  OUT+   |------> VCC ESP32-S3
                                   |  OUT-   |------> GND ESP32-S3
```

- **B+** dan **B-** pada TP4056 dihubungkan ke baterai.
- **OUT+** dan **OUT-** pada TP4056 dihubungkan ke VCC dan GND ESP32-S3 Zero Super Mini.
- **Micro USB** pada TP4056 digunakan untuk charging.

### Ilustrasi Sederhana

```
[USB]---[TP4056]---[Baterai Li-ion]
             |         |
           OUT+      B+
           OUT-      B-
             |         |
         VCC ESP32   GND ESP32
```

**Catatan:** Pastikan baterai yang digunakan sesuai spesifikasi (umumnya 3.7V Li-ion/LiPo), dan koneksi OUT+ serta OUT- dari TP4056 langsung ke ESP32-S3 Zero Super Mini untuk suplai daya.

## ILUSTRASI JALUR KABEL LENGKAP - UNTUK PEMULA

Berikut adalah ilustrasi jalur kabel yang sangat detail. Setiap GPIO di ESP32-C3 hanya muncul SEKALI (seperti di board fisik), dan jalur kabel dapat diikuti dari awal sampai akhir tanpa putus.

### Daftar Pin ESP32-S3 Zero Super Mini yang Digunakan:
```
ESP32-S3 ZERO SUPER MINI BOARD
┌─────────────────────────┐
│ GPIO1  ──── (untuk ROW1) │
│ GPIO2  ──── (untuk ROW2) │
│ GPIO3  ──── (untuk ROW3) │
│ GPIO4  ──── (untuk ROW4) │
│ GPIO5  ──── (untuk COL1) │
│ GPIO6  ──── (untuk COL2) │
│ GPIO7  ──── (untuk COL3) │
│ GPIO8  ──── (untuk COL4) │
│ GPIO9  ──── (LED Status) │
│ GPIO10 ──── (Extra/Future)│
└─────────────────────────┘
```

### Jalur Kabel Komplet dengan Diode dan Tombol (dengan arah diode ASCII):

```
ESP32-S3 BOARD                    GRID MACROPAD 4x4                    ESP32-S3 BOARD

GPIO1 ────────┬──|>|──[Tombol1]─────────────── GPIO5
              │
              ├──|>|──[Tombol2]─────────────── GPIO6
              │
              ├──|>|──[Tombol3]─────────────── GPIO7
              │
              └──|>|──[Tombol4]─────────────── GPIO8

GPIO2 ────────┬──|>|──[Tombol5]─────────────── GPIO5
              │
              ├──|>|──[Tombol6]─────────────── GPIO6
              │
              ├──|>|──[Tombol7]─────────────── GPIO7
              │
              └──|>|──[Tombol8]─────────────── GPIO8

GPIO3 ────────┬──|>|──[Tombol9]─────────────── GPIO5
              │
              ├──|>|──[Tombol10]────────────── GPIO6
              │
              ├──|>|──[Tombol11]────────────── GPIO7
              │
              └──|>|──[Tombol12]────────────── GPIO8

GPIO4 ────────┬──|>|──[Tombol13]────────────── GPIO5
              │
              ├──|>|──[Tombol14]────────────── GPIO6
              │
              ├──|>|──[Tombol15]────────────── GPIO7
              │
              └──|>|──[Tombol16]────────────── GPIO8
```

Keterangan arah diode:
- `──|>|──` : Anoda di kiri (baris/GPIO), katoda di kanan (tombol/kolom). Arus dari kiri ke kanan.
- **Anoda** adalah ujung diode tempat arus listrik masuk (biasanya terhubung ke sumber/positif).
- **Katoda** adalah ujung diode tempat arus keluar (biasanya terhubung ke beban/negatif).

Penjelasan ditambahkan agar pemula memahami peran anoda dan katoda pada diode, sehingga arah pemasangan diode tidak salah.

### Penjelasan Detail Jalur Kabel (Untuk yang Benar-benar Pemula):

**BARIS 1 (ROW 1):**
- Kabel dari GPIO1 bercabang menjadi 4:
  - Cabang 1: GPIO1 ──|>|── Tombol1 ── GPIO5
  - Cabang 2: GPIO1 ──|>|── Tombol2 ── GPIO6  
  - Cabang 3: GPIO1 ──|>|── Tombol3 ── GPIO7
  - Cabang 4: GPIO1 ──|>|── Tombol4 ── GPIO8

**BARIS 2 (ROW 2):**
- Kabel dari GPIO2 bercabang menjadi 4:
  - Cabang 1: GPIO2 ──|>|── Tombol5 ── GPIO5
  - Cabang 2: GPIO2 ──|>|── Tombol6 ── GPIO6
  - Cabang 3: GPIO2 ──|>|── Tombol7 ── GPIO7
  - Cabang 4: GPIO2 ──|>|── Tombol8 ── GPIO8

**BARIS 3 (ROW 3):**
- Kabel dari GPIO3 bercabang menjadi 4:
  - Cabang 1: GPIO3 ──|>|── Tombol9 ── GPIO5
  - Cabang 2: GPIO3 ──|>|── Tombol10 ── GPIO6
  - Cabang 3: GPIO3 ──|>|── Tombol11 ── GPIO7
  - Cabang 4: GPIO3 ──|>|── Tombol12 ── GPIO8

**BARIS 4 (ROW 4):**
- Kabel dari GPIO4 bercabang menjadi 4:
  - Cabang 1: GPIO4 ──|>|── Tombol13 ── GPIO5
  - Cabang 2: GPIO4 ──|>|── Tombol14 ── GPIO6
  - Cabang 3: GPIO4 ──|>|── Tombol15 ── GPIO7
  - Cabang 4: GPIO4 ──|>|── Tombol16 ── GPIO8

### Visualisasi Grid Tombol dengan Posisi Fisik:

```
        COL1    COL2    COL3    COL4
        (GPIO5) (GPIO6) (GPIO7) (GPIO8)
ROW1     [1]     [2]     [3]     [4]    (GPIO1)
ROW2     [5]     [6]     [7]     [8]    (GPIO2)  
ROW3     [9]    [10]    [11]    [12]    (GPIO3)
ROW4    [13]    [14]    [15]    [16]    (GPIO4)
```

### Tabel Jalur Kabel Per Tombol:

| Tombol | Jalur Kabel Lengkap |
|--------|---------------------|
| 1      | GPIO1 ──|>|── Tombol1 ── GPIO5 |
| 2      | GPIO1 ──|>|── Tombol2 ── GPIO6 |
| 3      | GPIO1 ──|>|── Tombol3 ── GPIO7 |
| 4      | GPIO1 ──|>|── Tombol4 ── GPIO8 |
| 5      | GPIO2 ──|>|── Tombol5 ── GPIO5 |
| 6      | GPIO2 ──|>|── Tombol6 ── GPIO6 |
| 7      | GPIO2 ──|>|── Tombol7 ── GPIO7 |
| 8      | GPIO2 ──|>|── Tombol8 ── GPIO8 |
| 9      | GPIO3 ──|>|── Tombol9 ── GPIO5 |
| 10     | GPIO3 ──|>|── Tombol10 ── GPIO6 |
| 11     | GPIO3 ──|>|── Tombol11 ── GPIO7 |
| 12     | GPIO3 ──|>|── Tombol12 ── GPIO8 |
| 13     | GPIO4 ──|>|── Tombol13 ── GPIO5 |
| 14     | GPIO4 ──|>|── Tombol14 ── GPIO6 |
| 15     | GPIO4 ──|>|── Tombol15 ── GPIO7 |
| 16     | GPIO4 ──|>|── Tombol16 ── GPIO8 |

## Penjelasan Mengapa GPIO Muncul Beberapa Kali di Kolom

Ketika Anda melihat GPIO5, GPIO6, GPIO7, GPIO8 muncul berulang di kolom, itu karena:

1. **GPIO5-GPIO8 adalah pin KOLOM** yang digunakan bersama oleh beberapa tombol
2. **Di board fisik**, Anda hanya melihat 1 pin GPIO5, tapi pin ini **dikabel ke 4 tombol berbeda** (tombol 1, 5, 9, 13)
3. **Sama seperti colokan listrik di rumah** - 1 colokan bisa digunakan oleh beberapa peralatan dengan cara memakai stop kontak

**Jadi praktisnya:**
- 1 pin GPIO5 di board → dikabel ke 4 tempat (tombol 1, 5, 9, 13)
- 1 pin GPIO6 di board → dikabel ke 4 tempat (tombol 2, 6, 10, 14)  
- 1 pin GPIO7 di board → dikabel ke 4 tempat (tombol 3, 7, 11, 15)
- 1 pin GPIO8 di board → dikabel ke 4 tempat (tombol 4, 8, 12, 16)

## Cara Kerja Scanning Tombol

1. **Aktifkan GPIO1** (baris 1), baca semua kolom GPIO5-GPIO8
2. **Aktifkan GPIO2** (baris 2), baca semua kolom GPIO5-GPIO8  
3. **Aktifkan GPIO3** (baris 3), baca semua kolom GPIO5-GPIO8
4. **Aktifkan GPIO4** (baris 4), baca semua kolom GPIO5-GPIO8

## Catatan

- Pin GPIO dapat diganti sesuai kebutuhan, pastikan tidak bentrok dengan fungsi lain (misal, I2C/UART/SPI jika digunakan).
- Gunakan resistor pull-up/pull-down jika diperlukan untuk kestabilan pembacaan.
- Pastikan setiap tombol memiliki diode untuk mencegah ghosting.
- **Diode sangat penting** - tanpa diode, menekan beberapa tombol bersamaan bisa menghasilkan deteksi tombol palsu (ghosting).

## Mulai dari Sederhana: Daftar Bahan yang Perlu Dibeli

- Modul utama:
  - [ ] ESP32-S3 Zero Super Mini
  - [ ] Modul TP4056 (charger baterai Li-ion/LiPo)
  - [ ] PCB grid 4x4 (atau protoboard untuk latihan)
- Komponen tombol:
  - [ ] Switch/tombol sebanyak 16 buah
  - [ ] Keycap sebanyak 16 buah
  - [ ] Diode kecil (misal 1N4148) sebanyak 16 buah
- Koneksi dan wiring:
  - [ ] Kabel jumper/wiring secukupnya
  - [ ] Header pin (male/female) untuk koneksi ke board
- Daya:
  - [ ] Baterai Li-ion/LiPo 3.7V (jika ingin portabel)
  - [ ] Kabel USB-C (untuk power dan programming ESP32-S3)
- Perakitan:
  - [ ] Solder & soldering iron (untuk penyambungan komponen)
  - [ ] Double tape/spacer/mounting (untuk menempel/memasang PCB dan komponen)
  - [ ] Alat potong/kupas kabel (wire stripper/cutter)
- Opsional:
  - [ ] Resistor pull-up/pull-down (jika diperlukan)
  - [ ] Case/enclosure untuk macropad
  - [ ] Stiker/label tombol

## Fitur-fitur

- [ ] Keymap Editable via GUI (keymap tombol bisa diubah dengan aplikasi GUI, tanpa modifikasi kode manual)
- [ ] Keymap Web Editor (keymap dapat diedit melalui antarmuka web dari browser perangkat yang terhubung)
- [ ] Mapping ke JSON (konfigurasi keymap dan pengaturan lain dapat disimpan/dibaca dari file JSON)
- [ ] Auto Sleep & Wake (macropad otomatis tidur saat idle dan aktif saat ada aktivitas)
- [ ] Indikator LED (misal untuk status koneksi, charging, atau feedback tombol)
- [ ] Reset/boot button (memudahkan reset atau masuk mode flash)
- [ ] Firmware update via USB/web (memudahkan upgrade firmware tanpa bongkar perangkat)
- [ ] Mode test tombol (fitur untuk cek semua tombol berfungsi saat perakitan)