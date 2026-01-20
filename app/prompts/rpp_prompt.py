from datetime import datetime
from app.schemas.rpp_schema import RPPRequest

def build_rpp_prompt(data: RPPRequest, db_cp_content: str = None) -> str:
    ppp_str = ", ".join(data.profil_pelajar_pancasila)
    media_str = ", ".join(data.media)
    penilaian_str = ", ".join(data.penilaian)
    
    # Dynamic Year
    current_year = datetime.now().year
    next_year = current_year + 1
    tahun_ajaran = f"{current_year}/{next_year}"

    # Logika jika CP ditemukan di Database
    cp_reference = f"REFERENSI CAPAIAN PEMBELAJARAN RESMI:\n{db_cp_content}" if db_cp_content else "Gunakan standar Kurikulum Merdeka terbaru."

    return f"""
Berperanlah sebagai Guru Profesional dan Ahli Kurikulum Merdeka Kemdikbudristek Indonesia.
Buatkan "MODUL AJAR" (bukan RPP biasa) yang lengkap dan rapi sesuai standar terbaru.

{cp_reference}

IDENTITAS:
- Guru: {data.nama_guru}
- Sekolah: {data.nama_sekolah}
- Tahun Pelajaran: {tahun_ajaran}
- Mapel: {data.mapel}
- Fase/Kelas: {data.fase} / {data.kelas} ({data.jenjang})
- Elemen: {data.elemen} (Fokus Utama Kegiatan)
- Topik: {data.topik}
- Waktu: {data.alokasi_waktu}

PARAMETER:
- Model: {data.model_pembelajaran}
- Metode: {", ".join(data.metode_pembelajaran if data.metode_pembelajaran else ["Diskusi", "Tanya Jawab"])}
- Tujuan: {data.tujuan_pembelajaran if data.tujuan_pembelajaran else "Rumuskan Tujuan Pembelajaran (TP) yang SMART berdasarkan Elemen CP di atas."}
- Profil Pancasila: {ppp_str}
- Sarana & Prasarana: {data.sarana_prasarana} (Media: {media_str})
- Karakteristik Siswa: {data.kemampuan_siswa}

INSTRUKSI KHUSUS & DIFERENSIASI:
1. FOKUS ELEMEN "{data.elemen.upper()}": Kegiatan pembelajaran WAJIB mencerminkan elemen ini. 
   - Contoh: Jika "Membaca", pastikan ada kegiatan literasi teks/visual. Jika "Menyimak", pastikan ada media audio/cerita lisan.
2. SARANA {data.sarana_prasarana.upper()}: Sesuaikan alat peraga. Jika 'Terbatas', gunakan benda sekitar.
3. KEMAMPUAN {data.kemampuan_siswa.upper()}: Berikan strategi scaffolding untuk siswa yang butuh bimbingan.

STRUKTUR OUTPUT (MARKDOWN):
# MODUL AJAR KURIKULUM MERDEKA

## I. INFORMASI UMUM

| Identitas Modul | |
| :--- | :--- |
| **Penyusun** | {data.nama_guru} |
| **Instansi** | {data.nama_sekolah} |
| **Tahun Penyusunan** | {current_year} |
| **Jenjang / Kelas** | {data.jenjang} / {data.kelas} |
| **Mata Pelajaran** | {data.mapel} |
| **Fase / Elemen** | {data.fase} / {data.elemen} |
| **Topik** | {data.topik} |
| **Alokasi Waktu** | {data.alokasi_waktu} |

A. Kompetensi Awal
B. Profil Pelajar Pancasila
C. Sarana dan Prasarana
D. Target Peserta Didik
E. Model Pembelajaran

## II. KOMPONEN INTI
A. Tujuan Pembelajaran
B. Pemahaman Bermakna
C. Pertanyaan Pemantik
D. Kegiatan Pembelajaran
   1. Kegiatan Pendahuluan & **Asesmen Awal** (Diagnostik Kognitif/Non-Kognitif singkat)
   2. Kegiatan Inti (Sintaks {data.model_pembelajaran} dengan diferensiasi sesuai elemen {data.elemen})
   3. Kegiatan Penutup (Refleksi & Kesimpulan)
E. Asesmen
   - Asesmen Formatif (Awal & Proses)
   - Asesmen Sumatif (Lingkup Materi) ({penilaian_str})
F. Pengayaan dan Remedial

## III. LAMPIRAN
A. Lembar Kerja Peserta Didik (LKPD) - *Buatkan konten spesifik sesuai elemen {data.elemen}*
B. Bahan Bacaan Guru & Peserta Didik
C. Glosarium
D. Daftar Pustaka

---

| Mengetahui, | |
| :--- | :--- |
| **Kepala Sekolah** | **Guru Mata Pelajaran** |
| | |
| | |
| | |
| **(...)** | **{data.nama_guru}** |
| NIP. .................... | NIP. .................... |

CONSTRAINT:
- GUNAKAN Bahasa Indonesia baku.
- Output Wajib Rapi dan Profesional.
- DILARANG MENGGUNAKAN blockquote (>) berlebihan.
- DILARANG MENGGUNAKAN code blocks (```) untuk teks normal.
- Gunakan Heading Markdown (## I., ## II.) untuk level Romawi.
- Gunakan Heading Markdown (### A., ### B.) untuk level Huruf Kapital.
- Gunakan list angka (1., 2.) untuk detail level ketiga.
- Gunakan bullet points ( - ) untuk detail level keempat.
- Gunakan Tabel Markdown untuk bagian Identitas di atas.
- DILARANG menggunakan format LaTeX (seperti $\\text{{...}}$) ataupun simbol dollar ($).
- DILARANG menggunakan `\\underline`, `\\hspace`, atau perintah LaTeX lainnya.
- Tuliskan rumus matematika dengan angka dan simbol biasa. Contoh: "20 - ... = 12" (JANGAN gunakan format $...$).
- Untuk titik-titik isian, gunakan garis bawah panjang manual "__________" atau titik-titik "...".

STRICT OUTPUT RULES:
1. LANGSUNG mulai dengan Header Markdown "# MODUL AJAR...".
2. DILARANG KERAS memberikan kata pengantar, basa-basi, atau kalimat pembuka seperti "Tentu", "Berikut adalah", "Baik", "Saya akan berperan", dll.
3. Output harus murni konten Modul Ajar tanpa teks tambahan apapun.
4. Gunakan bullet points ( - ) atau penomoran ( 1. ) untuk daftar, jangan gunakan simbol aneh.
"""
