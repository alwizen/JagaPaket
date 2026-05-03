# Warehouse Packing Proof Recording System (Jaga Paket)

Sistem Perekaman Bukti Packing yang efisien dan andal untuk memastikan setiap paket yang dikirim memiliki bukti video yang valid.

## 🚀 Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database**: MySQL / MariaDB (via SQLAlchemy & `aiomysql`)
- **Frontend**: Tailwind CSS, HTMX, Alpine.js (via CDN)
- **Templating**: Jinja2
- **Environment**: `python-dotenv` & Pydantic Settings

---

## 🛠️ Setup Proyek

### 1. Persiapan Environment

Pastikan Python 3.10+ dan MySQL/MariaDB sudah terinstall.

```bash
git clone https://github.com/USERNAME/recorderd.git
cd recorderd
python3 -m venv venv
source venv/bin/activate  # (atau venv/bin/activate.fish untuk user fish)
pip install -r requirements.txt
```

### 2. Konfigurasi Database (.env)

Aplikasi menggunakan konfigurasi modular. Buat file `.env` di root folder:

```ini
# Database Configuration
DB_USER=root
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=3306
DB_NAME=recorderd

# Storage Configuration
VIDEO_STORAGE_PATH=./videos
```

_Catatan: Jika `.env` tidak ada, sistem akan default menggunakan SQLite `recorderd.db`._

### 3. Menjalankan Aplikasi

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Akses di: `http://localhost:8000`

---

## ✨ Fitur Utama

- **Admin Dashboard**: Ringkasan statistik perekaman harian, mingguan, dan bulanan.
- **Advanced Recorder**: Perekaman bukti packing dengan barcode/invoice trigger dan upload otomatis.
- **Global Search**: Cari video berdasarkan Nomor Pesanan (INV) langsung dari navbar di halaman mana pun.
- **Recording History**: Daftar lengkap seluruh rekaman dengan fitur preview dan download.
- **Dark/Light Mode**: Dukungan tema visual yang dinamis sesuai preferensi pengguna.
- **Modular Config**: Pengaturan kredensial yang aman melalui environment variables.

---

## 📖 Panduan Penggunaan

Untuk instruksi mendetail mengenai cara mengoperasikan sistem oleh operator dan admin, silakan baca:
👉 **[USER_GUIDE.md](./USER_GUIDE.md)**

---

## 🔑 Default Login

Saat pertama kali dijalankan, sistem membuat akun default:

- **Username**: `admin`
- **Password**: `admin123`

---

_Developed with ❤️ for efficient logistics._
