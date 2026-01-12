import asyncio
import json
from app.services.ppt_service import PPTService

async def test_aesthetic_ppt():
    test_data = {
        "judul_materi": "Petualangan di Hutan Tropis",
        "theme": "Alam",
        "slides": [
            {
                "judul_slide": "Selamat Datang di Hutan",
                "konten": ["Hutan adalah paru-paru dunia.", "Banyak oksigen dihasilkan di sini.", "Ayo kita jaga kelestariannya!"],
                "keyword_visual": "tropical rainforest",
                "layout_type": "highlight"
            },
            {
                "judul_slide": "Flora & Fauna",
                "konten": ["Harimau Sumatera", "Bunga Bangkai", "Orangutan"],
                "keyword_visual": "tiger",
                "layout_type": "split"
            },
            {
                "judul_slide": "Keanekaragaman Hayati",
                "konten": ["Indonesia memiliki ribuan pulau.", "Tiap pulau punya keunikan."],
                "keyword_visual": "indonesia nature",
                "layout_type": "big_image"
            }
        ]
    }
    try:
        print("Testing Aesthetic PPT Generation...")
        result = await PPTService.generate_ppt(test_data)
        with open("aesthetic_test.pptx", "wb") as f:
            f.write(result.getbuffer())
        print("Success! aesthetic_test.pptx created.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_aesthetic_ppt())
