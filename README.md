# AI RPP Generator Backend (FastAPI + Gemini)

Backend service untuk generate **Modul Ajar (RPP) Kurikulum Merdeka** secara otomatis menggunakan Google Gemini AI. Dirancang untuk dikonsumsi oleh Frontend Next.js.

## 🚀 Persiapan

### 1. Prasyarat
- Python 3.11 atau lebih baru
- API Key Google Gemini (Dapatkan di [Google AI Studio](https://aistudio.google.com/))

### 2. Instalasi

1.  Masuk ke folder backend:
    ```bash
    cd backend
    ```

2.  Buat Virtual Environment (opsional tapi disarankan):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Setup Environment Variable:
    - Buka file `.env`.
    - Isi `GEMINI_API_KEY` dengan API Key Anda.

## 🏃‍♂️ Menjalankan Server

Jalankan perintah berikut:

```bash
uvicorn app.main:app --reload
```

Server akan berjalan di `http://localhost:8000`.
Dokumentasi API (Swagger UI) bisa diakses di `http://localhost:8000/docs`.

## 🔌 API Integration (Next.js Example)

### Endpoint
`POST http://localhost:8000/api/rpp/generate`

### Contoh Fetch di Next.js

```typescript
const generateRPP = async (formData) => {
  const response = await fetch('http://localhost:8000/api/rpp/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jenjang: "SMA",
      kelas: "10",
      mapel: "Biologi",
      fase: "E",
      topik: "Keanekaragaman Hayati",
      alokasi_waktu: "2 x 45 menit",
      tujuan_pembelajaran: "Peserta didik dapat mengidentifikasi tipe keanekaragaman hayati",
      profil_pelajar_pancasila: ["Bernalar Kritis"],
      model_pembelajaran: "Discovery Learning",
      media: ["Lingkungan Sekolah", "Video"],
      penilaian: ["Formatif"]
    }),
  });

  const data = await response.json();
  console.log(data); // { status: "success", data: { rpp_markdown: "..." } }
}
```

## 📂 Struktur Project

```
backend/
├── app/
│   ├── main.py            # Entry point & CORS
│   ├── config.py          # Env loader
│   ├── gemini_client.py   # AI Client
│   ├── prompts/           # Prompt Engineering
│   ├── schemas/           # Pydantic Models (Validation)
│   ├── routes/            # API Endpoints
│   └── services/          # Business Logic
├── .env                   # API Keys (Jangan commit file ini!)
├── requirements.txt       # Dependencies
└── README.md              # Dokumentasi
```
