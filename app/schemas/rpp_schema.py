from pydantic import BaseModel, Field
from typing import List, Optional

class RPPRequest(BaseModel):
    # Identitas
    nama_guru: str = "Guru"
    nama_sekolah: str = "Sekolah"
    jenjang: str = Field(..., example="SD")
    kelas: str = Field(..., example="4")
    mapel: str = Field(..., example="Matematika")
    fase: str = Field(..., example="B")
    elemen: str = Field(..., example="Bilangan") # New Field
    topik: str = Field(..., example="Pecahan")
    alokasi_waktu: str = Field(..., example="2 JP")
    
    # Parameter
    tujuan_pembelajaran: Optional[str] = Field(None)
    profil_pelajar_pancasila: List[str] = Field(...)
    model_pembelajaran: str = Field(...)
    metode_pembelajaran: List[str] = Field(default=["Diskusi", "Tanya Jawab"]) # NEW
    media: List[str] = Field(default=[])
    penilaian: List[str] = Field(default=[])

    # Diferensiasi
    kemampuan_siswa: str = "Rata-rata"
    sarana_prasarana: str = "Terbatas"

class RPPData(BaseModel):
    rpp_markdown: str
    rpp_json: Optional[dict] = None

class RPPResponse(BaseModel):
    status: str = "success"
    data: RPPData
