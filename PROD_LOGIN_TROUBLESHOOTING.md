# Production Login Troubleshooting Guide

## Problem: "Login failed due to server error" pada Production

### Root Causes yang Sering Terjadi

1. **Database Connection Error** (PALING UMUM)
   - DATABASE_URL tidak correct
   - MySQL/MariaDB server unreachable dari production
   - User credentials salah
   - Database tidak exist

2. **JWT Secret Mismatch**
   - JWT_SECRET di production berbeda dengan lokal
   - Token creation gagal

3. **User Data Tidak Exist**
   - Admin user tidak dibuat
   - Database migration gagal

---

## Quick Diagnostics

### 1. Test Database Connection
```bash
curl http://<production-url>/api/health
```
**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "project": "Warehouse Packing Proof Recording System"
}
```

### 2. Check Production Logs
```bash
# Lihat application logs
tail -f /var/log/recorderd/app.log

# Cari database errors
grep -i "database error" /var/log/recorderd/app.log
grep -i "connection" /var/log/recorderd/app.log
```

### 3. Verify Environment Variables (Production Server)
```bash
# Check if DATABASE_URL is set correctly
echo $DATABASE_URL

# Check if JWT_SECRET is set
echo $JWT_SECRET
```

---

## Step-by-Step Troubleshooting

### Step 1: Verify Database Connection
SSH ke production server dan test:
```bash
# Test MySQL connection
mysql -h localhost -u root -p -e "USE recorderd; SELECT * FROM users LIMIT 1;"
```

**If Connection Fails:**
- Check if MySQL service is running
- Verify database credentials di environment variables
- Check firewall rules jika database di server terpisah

### Step 2: Check If Database Schema Exists
```bash
mysql -h localhost -u root -p -e "USE recorderd; DESCRIBE users;"
```

**If Table Doesn't Exist:**
- Restart application agar auto-create tables
- Atau jalankan manual migration

### Step 3: Verify Admin User Exists
```bash
mysql -h localhost -u root -p -e "USE recorderd; SELECT username, role FROM users WHERE role='SUPER_ADMIN';"
```

**If No Admin User:**
1. Option A: Restart app agar auto-create admin user
2. Option B: Manually insert user:
```sql
INSERT INTO users (name, username, password_hash, role) 
VALUES ('Admin', 'admin', '$2b$12$...bcrypt_hash...', 'SUPER_ADMIN');
```

### Step 4: Test Login Endpoint Directly
```bash
# Test dengan curl
curl -X POST http://<production-url>/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

---

## Environment Variables Checklist

Add to production `.env` atau set di systemd:

```bash
# Required Variables
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/recorderd
JWT_SECRET=your-secret-key-here-change-in-production

# Optional
VIDEO_STORAGE_PATH=/var/recorderd/videos
```

**PENTING:** 
- JWT_SECRET harus SAMA antara lokal dan production
- DATABASE_URL harus point ke correct database server

---

## Deployment Checklist

- [ ] Database MySQL/MariaDB sudah running
- [ ] Database `recorderd` sudah exist
- [ ] Database credentials correct
- [ ] Environment variables (.env) sudah set
- [ ] JWT_SECRET sudah diganti (jangan gunakan default "super-secret-key-replace-in-production")
- [ ] Application bisa connect ke database (check `/api/health`)
- [ ] Admin user terbuat otomatis atau sudah di-seed
- [ ] Login bisa dengan admin/admin123

---

## Logs untuk Debug

Setelah update code, logs akan lebih informatif:

```
INFO: Database tables created successfully
INFO: Default admin user created
INFO: Application started successfully
ERROR: Database initialization error - ...detail...
ERROR: Database connection error during login
```

Lihat logs untuk exact error message.

---

## Production Deployment Command

```bash
# Build & Deploy
pip install -r requirements.txt
# Atau dengan PM2/Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Dengan environment
DATABASE_URL=mysql+aiomysql://root:password@host:3306/recorderd \
JWT_SECRET=your-production-secret \
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
