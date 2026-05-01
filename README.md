# Warehouse Packing Proof Recording System

## Prasyarat

- Python 3
- MariaDB (opsional, bisa menggunakan SQLite untuk testing)
- Git

## Setup Proyek di Komputer Baru (Clone)

### 1. Clone Repository dari GitHub

```bash
git clone https://github.com/USERNAME/recorderd.git
cd recorderd
```

(Ganti `USERNAME` dengan username GitHub Anda)

### 2. Buat Virtual Environment

Untuk Fish shell:
```bash
python3 -m venv venv
source venv/bin/activate.fish
```

Untuk Bash:
```bash
python3 -m venv venv
source venv/bin/activate
```

Untuk Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. (Opsional) Setup Database Environment

Jika Anda ingin menggunakan MariaDB, buat file `.env` di root folder:

```
DATABASE_URL=mysql+aiomysql://root:password_anda@localhost:3306/recorderd
```

Atau biarkan default SQLite untuk development/testing.

---

## Cara Menjalankan Aplikasi

Setelah setup selesai, ikuti langkah berikut untuk menjalankan aplikasi:

1. **Aktifkan Virtual Environment:**
   Jika Anda menggunakan fish shell:

   ```bash
   source venv/bin/activate.fish
   ```

   Atau untuk bash biasa:

   ```bash
   source venv/bin/activate
   ```

2. **Konfigurasi Database (Penting):**
   Secara default, saat ini program disetting untuk menggunakan **SQLite** (di file `recorderd.db`) agar langsung bisa dites.
   Jika Anda ingin menggunakan **MariaDB** untuk production, buka file `config.py` lalu ubah URL database Anda menjadi seperti ini:

   ```python
   DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+aiomysql://root:password_anda@localhost:3306/recorderd")
   ```

3. **Jalankan Server (Backend):**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Akses Dashboard (Di Komputer Client / Windows):**
   Buka Google Chrome lalu akses ke IP Server Backend. Jika di testing lokal, buka:
   👉 `http://localhost:8000`

## Kredensial Bawaan (Default Login)

Aplikasi akan membuat satu pengguna administrator saat dijalankan untuk pertama kalinya.

- **Username:** `admin`
- **Password:** `admin123`

## Menjalankan Chrome Kiosk Mode (Di Workstation Windows)

Untuk mengunci layar khusus aplikasi packing di Windows, buat sebuah Shortcut Google Chrome dan ubah target / properties-nya menjadi seperti ini:

```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk http://IP_SERVER_LINUX:8000/
```

Barcode Scanner Anda yang berbasis colok USB otomatis akan me-trigger mode rekam ketika input terdeteksi (sebagai script _keyboard wedge_ di latar belakang). Untuk berhenti, tekan ekstrak tombol `F8`.
