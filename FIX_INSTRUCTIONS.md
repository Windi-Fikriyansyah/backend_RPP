# Instruksi Perbaikan Startup

Saya mendeteksi 2 error utama saat Anda menjalankan server:

## 1. Module `google-genai` Missing
**Status**: Sedang saya install otomatis di background.
**Tindakan**: Tunggu terminal selesai melakukan instalasi.
Jika masih error, jalankan manual:
```bash
pip install google-genai
```

## 2. Salah Password Database
**Log Error**: `asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "postgres"`
**Tindakan**:
1. Buka file `backend/.env`.
2. Cari baris `DATABASE_URL`.
3. Ganti password default `password` dengan password PostgreSQL Anda yang sebenarnya.
   Contoh: `postgresql+asyncpg://postgres:Rahasia123@localhost/rpp_dp`

---------------------------------------

Setelah 2 hal di atas beres, jalankan ulang:
```bash
uvicorn app.main:app --reload
```
