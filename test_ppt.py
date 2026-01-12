import asyncio
import json
from app.services.ppt_service import PPTService

async def test_ppt():
    test_data = {
        "judul_materi": "Mengenal Ungkapan Sapaan",
        "slides": [
            {
                "judul_slide": "Selamat Pagi",
                "konten": ["Sapa teman dengan ramah", "Gunakan senyum"],
                "keyword_visual": "greeting",
                "instruksi_guru": "Ajak siswa praktik"
            }
        ]
    }
    try:
        print("Testing PPT Generation...")
        result = await PPTService.generate_ppt(test_data)
        with open("debug_test.pptx", "wb") as f:
            f.write(result.getbuffer())
        print("Success! debug_test.pptx created.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_ppt())
