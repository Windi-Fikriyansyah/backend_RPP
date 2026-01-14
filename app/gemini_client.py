import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
    # Gunakan gemini-2.0-flash (Tersedia di list model Anda, 1.5 tidak ditemukan)
    GEMINI_MODEL = "gemini-2.5-flash" 

class GeminiClient:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not set")
            self.client = None
        else:
            # Tetap gunakan Client, tapi kita panggil versi aio (async) nanti
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)

    async def generate_content(self, prompt: str) -> str:
        if not self.client:
             return "Error: API Key Missing"
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Perbaikan: Gunakan self.client.aio untuk mendukung await
                # Gunakan model dari Config
                response = await self.client.aio.models.generate_content(
                    model=Config.GEMINI_MODEL,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                # Handle Quota (Rate Limit) OR Server Overload (503)
                if ("429" in error_str or 
                    "RESOURCE_EXHAUSTED" in error_str or 
                    "503" in error_str or 
                    "overloaded" in error_str or
                    "UNAVAILABLE" in error_str):
                    
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        print(f"Gemini Busy/Overloaded (Attempt {attempt+1}/{max_retries}). Retrying in {wait_time}s... Error: {error_str[:100]}")
                        await asyncio.sleep(wait_time)
                        continue
                return f"Error Generating RPP: {error_str}"
        return "Error: Failed after retries (Gemini System Busy)"

gemini_client = GeminiClient()
