from app.schemas.rpp_schema import RPPRequest, RPPResponse, RPPData
from app.prompts.rpp_prompt import build_rpp_prompt
from app.gemini_client import gemini_client

class RppService:
    @staticmethod
    async def generate_rpp(request_data: RPPRequest) -> RPPResponse:
        # 1. Build Prompt
        prompt = build_rpp_prompt(request_data)

        # 2. Call AI
        generated_text = await gemini_client.generate_content(prompt)

        # 3. Format Response
        # Di sini kita bisa menambahkan parsing lebih lanjut jika ingin memisahkan JSON structure
        # Untuk sekarang kita kirim Markdown raw sesuai request user.
        
        return RPPResponse(
            status="success",
            data=RPPData(
                rpp_markdown=generated_text,
                rpp_json={
                    # Placeholder jika nanti ingin parsing markdown ke JSON object terstruktur
                    "meta": {
                        "mapel": request_data.mapel,
                        "kelas": request_data.kelas
                    }
                }
            )
        )
