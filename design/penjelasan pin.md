# Pinout ESP32-C3 Super Mini untuk Macropad Grid 4x4

Macropad grid 4x4 menggunakan 16 tombol yang dihubungkan dalam konfigurasi matriks (4 baris x 4 kolom). Setiap tombol terhubung di antara satu pin baris dan satu pin kolom. ESP32-C3 Super Mini menyediakan cukup banyak GPIO untuk menghubungkan semua baris dan kolom secara langsung.

## Hal Penting dari Chip ESP32-C3 Super Mini

ESP32-C3 Super Mini adalah board berbasis chip ESP32-C3. Berikut fitur penting yang relevan untuk macropad:

- **Banyak GPIO**: Tersedia cukup GPIO (umumnya 10 pin) untuk input/output, cukup untuk kebutuhan macropad grid.
- **RISC-V Single-core**: Prosesor RISC-V 32-bit dengan clock hingga 160 MHz, respons cepat untuk pembacaan tombol.
- **Memori Internal**: 400KB SRAM, cukup untuk firmware macropad dan pengolahan data tombol.
- **Dukungan Interface**: Mendukung I2C, SPI, UART, PWM, ADC, serta WiFi dan BLE untuk komunikasi nirkabel.
- **Low Power**: Konsumsi daya rendah, cocok untuk perangkat yang selalu aktif.

Fitur-fitur ini membuat ESP32-C3 Super Mini sangat cocok untuk proyek macropad yang membutuhkan banyak input dan konektivitas.

## Modul TP4056 dan Ilustrasi Baterai

Untuk membuat macropad portabel, dapat ditambahkan modul TP4056 sebagai charger baterai Li-ion/LiPo. Modul TP4056 berfungsi untuk mengisi baterai secara aman melalui port micro USB dan menyediakan proteksi overcharge/overdischarge.

### Skema Koneksi TP4056 dan Baterai

```
+-------------------+      +-------------------+      +-------------------+
|   USB Power IN    | ---> |   TP4056 Charger  | ---> |   Baterai Li-ion  |
+-------------------+      +-------------------+      +-------------------+
                                   |  OUT+   |------> VCC ESP32-C3
                                   |  OUT-   |------> GND ESP32-C3
```

- **B+** dan **B-** pada TP4056 dihubungkan ke baterai.
- **OUT+** dan **OUT-** pada TP4056 dihubungkan ke VCC dan GND ESP32-C3 Super Mini.
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

**Catatan:** Pastikan baterai yang digunakan sesuai spesifikasi (umumnya 3.7V Li-ion/LiPo), dan koneksi OUT+ serta OUT- dari TP4056 langsung ke ESP32-C3 Super Mini untuk suplai daya.

## ILUSTRASI JALUR KABEL LENGKAP - UNTUK PEMULA

Berikut adalah ilustrasi jalur kabel yang sangat detail. Setiap GPIO di ESP32-C3 hanya muncul SEKALI (seperti di board fisik), dan jalur kabel dapat diikuti dari awal sampai akhir tanpa putus.

### Daftar Pin ESP32-C3 Super Mini yang Digunakan:
```
ESP32-C3 SUPER MINI BOARD
┌─────────────────────────┐
│ GPIO2 ──── (untuk ROW1) │
│ GPIO3 ──── (untuk ROW2) │
│ GPIO4 ──── (untuk ROW3) │
│ GPIO5 ──── (untuk ROW4) │
│ GPIO6 ──── (untuk COL1) │
│ GPIO7 ──── (untuk COL2) │
│ GPIO8 ──── (untuk COL3) │
│ GPIO9 ──── (untuk COL4) │
└─────────────────────────┘
```

### Jalur Kabel Komplet dengan Diode dan Tombol (dengan arah diode ASCII):

```
ESP32-C3 BOARD                    GRID MACROPAD 4x4                    ESP32-C3 BOARD

GPIO2 ────────┬──|>|──[Tombol1]─────────────── GPIO6
              │
              ├──|>|──[Tombol2]─────────────── GPIO7
              │
              ├──|>|──[Tombol3]─────────────── GPIO8
              │
              └──|>|──[Tombol4]─────────────── GPIO9

GPIO3 ────────┬──|>|──[Tombol5]─────────────── GPIO6
              │
              ├──|>|──[Tombol6]─────────────── GPIO7
              │
              ├──|>|──[Tombol7]─────────────── GPIO8
              │
              └──|>|──[Tombol8]─────────────── GPIO9

GPIO4 ────────┬──|>|──[Tombol9]─────────────── GPIO6
              │
              ├──|>|──[Tombol10]────────────── GPIO7
              │
              ├──|>|──[Tombol11]────────────── GPIO8
              │
              └──|>|──[Tombol12]────────────── GPIO9

GPIO5 ────────┬──|>|──[Tombol13]────────────── GPIO6
              │
              ├──|>|──[Tombol14]────────────── GPIO7
              │
              ├──|>|──[Tombol15]────────────── GPIO8
              │
              └──|>|──[Tombol16]────────────── GPIO9
```

Keterangan arah diode:
- `──|>|──` : Anoda di kiri (baris/GPIO), katoda di kanan (tombol/kolom). Arus dari kiri ke kanan.
- **Anoda** adalah ujung diode tempat arus listrik masuk (biasanya terhubung ke sumber/positif).
- **Katoda** adalah ujung diode tempat arus keluar (biasanya terhubung ke beban/negatif).

Penjelasan ditambahkan agar pemula memahami peran anoda dan katoda pada diode, sehingga arah pemasangan diode tidak salah.

### Penjelasan Detail Jalur Kabel (Untuk yang Benar-benar Pemula):

**BARIS 1 (ROW 1):**
- Kabel dari GPIO2 bercabang menjadi 4:
  - Cabang 1: GPIO2 ──|>|── Tombol1 ── GPIO6
  - Cabang 2: GPIO2 ──|>|── Tombol2 ── GPIO7  
  - Cabang 3: GPIO2 ──|>|── Tombol3 ── GPIO8
  - Cabang 4: GPIO2 ──|>|── Tombol4 ── GPIO9

**BARIS 2 (ROW 2):**
- Kabel dari GPIO3 bercabang menjadi 4:
  - Cabang 1: GPIO3 ──|>|── Tombol5 ── GPIO6
  - Cabang 2: GPIO3 ──|>|── Tombol6 ── GPIO7
  - Cabang 3: GPIO3 ──|>|── Tombol7 ── GPIO8
  - Cabang 4: GPIO3 ──|>|── Tombol8 ── GPIO9

**BARIS 3 (ROW 3):**
- Kabel dari GPIO4 bercabang menjadi 4:
  - Cabang 1: GPIO4 ──|>|── Tombol9 ── GPIO6
  - Cabang 2: GPIO4 ──|>|── Tombol10 ── GPIO7
  - Cabang 3: GPIO4 ──|>|── Tombol11 ── GPIO8
  - Cabang 4: GPIO4 ──|>|── Tombol12 ── GPIO9

**BARIS 4 (ROW 4):**
- Kabel dari GPIO5 bercabang menjadi 4:
  - Cabang 1: GPIO5 ──|>|── Tombol13 ── GPIO6
  - Cabang 2: GPIO5 ──|>|── Tombol14 ── GPIO7
  - Cabang 3: GPIO5 ──|>|── Tombol15 ── GPIO8
  - Cabang 4: GPIO5 ──|>|── Tombol16 ── GPIO9

### Visualisasi Grid Tombol dengan Posisi Fisik:

```
        COL1    COL2    COL3    COL4
        (GPIO6) (GPIO7) (GPIO8) (GPIO9)
ROW1     [1]     [2]     [3]     [4]    (GPIO2)
ROW2     [5]     [6]     [7]     [8]    (GPIO3)  
ROW3     [9]    [10]    [11]    [12]    (GPIO4)
ROW4    [13]    [14]    [15]    [16]    (GPIO5)
```

### Tabel Jalur Kabel Per Tombol:

| Tombol | Jalur Kabel Lengkap |
|--------|---------------------|
| 1      | GPIO2 ──|>|── Tombol1 ── GPIO6 |
| 2      | GPIO2 ──|>|── Tombol2 ── GPIO7 |
| 3      | GPIO2 ──|>|── Tombol3 ── GPIO8 |
| 4      | GPIO2 ──|>|── Tombol4 ── GPIO9 |
| 5      | GPIO3 ──|>|── Tombol5 ── GPIO6 |
| 6      | GPIO3 ──|>|── Tombol6 ── GPIO7 |
| 7      | GPIO3 ──|>|── Tombol7 ── GPIO8 |
| 8      | GPIO3 ──|>|── Tombol8 ── GPIO9 |
| 9      | GPIO4 ──|>|── Tombol9 ── GPIO6 |
| 10     | GPIO4 ──|>|── Tombol10 ── GPIO7 |
| 11     | GPIO4 ──|>|── Tombol11 ── GPIO8 |
| 12     | GPIO4 ──|>|── Tombol12 ── GPIO9 |
| 13     | GPIO5 ──|>|── Tombol13 ── GPIO6 |
| 14     | GPIO5 ──|>|── Tombol14 ── GPIO7 |
| 15     | GPIO5 ──|>|── Tombol15 ── GPIO8 |
| 16     | GPIO5 ──|>|── Tombol16 ── GPIO9 |

## Penjelasan Mengapa GPIO Muncul Beberapa Kali di Kolom

Ketika Anda melihat GPIO6, GPIO7, GPIO8, GPIO9 muncul berulang di kolom, itu karena:

1. **GPIO6-GPIO9 adalah pin KOLOM** yang digunakan bersama oleh beberapa tombol
2. **Di board fisik**, Anda hanya melihat 1 pin GPIO6, tapi pin ini **dikabel ke 4 tombol berbeda** (tombol 1, 5, 9, 13)
3. **Sama seperti colokan listrik di rumah** - 1 colokan bisa digunakan oleh beberapa peralatan dengan cara memakai stop kontak

**Jadi praktisnya:**
- 1 pin GPIO6 di board → dikabel ke 4 tempat (tombol 1, 5, 9, 13)
- 1 pin GPIO7 di board → dikabel ke 4 tempat (tombol 2, 6, 10, 14)  
- 1 pin GPIO8 di board → dikabel ke 4 tempat (tombol 3, 7, 11, 15)
- 1 pin GPIO9 di board → dikabel ke 4 tempat (tombol 4, 8, 12, 16)

## Cara Kerja Scanning Tombol

1. **Aktifkan GPIO2** (baris 1), baca semua kolom GPIO6-GPIO9
2. **Aktifkan GPIO3** (baris 2), baca semua kolom GPIO6-GPIO9  
3. **Aktifkan GPIO4** (baris 3), baca semua kolom GPIO6-GPIO9
4. **Aktifkan GPIO5** (baris 4), baca semua kolom GPIO6-GPIO9

## Catatan

- Pin GPIO dapat diganti sesuai kebutuhan, pastikan tidak bentrok dengan fungsi lain (misal, I2C/UART/SPI jika digunakan).
- Gunakan resistor pull-up/pull-down jika diperlukan untuk kestabilan pembacaan.
- Pastikan setiap tombol memiliki diode untuk mencegah ghosting.
- **Diode sangat penting** - tanpa diode, menekan beberapa tombol bersamaan bisa menghasilkan deteksi tombol palsu (ghosting).

## Mulai dari Sederhana: Daftar Bahan yang Perlu Dibeli

- Modul utama:
  - [ ] ESP32-C3 Super Mini
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
  - [ ] Kabel micro USB / Type C (untuk power dan programming ESP32-C3)
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