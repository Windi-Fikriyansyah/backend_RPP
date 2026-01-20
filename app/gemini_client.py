import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Deprecated, keep for reference or legacy
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
    # Use OpenRouter model ID for Gemini 2.5 Flash
    # GEMINI_MODEL = "gemini-2.5-flash" 
    GEMINI_MODEL = "google/gemini-2.5-flash" 

class GeminiClient:
    def __init__(self):
        if not Config.OPENROUTER_API_KEY:
            print("Warning: OPENROUTER_API_KEY not set")
            self.client = None
        else:
            # Initialize AsyncOpenAI client pointing to OpenRouter
            self.client = AsyncOpenAI(
                api_key=Config.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )



    # def __init__(self):
    #     if not Config.GEMINI_API_KEY:
    #         print("Warning: GEMINI_API_KEY not set")
    #         self.client = None
    #     else:
    #         # GANTI BASE_URL ke Google AI Studio (OpenAI Compatible)
    #         self.client = AsyncOpenAI(
    #             api_key=Config.GEMINI_API_KEY,
    #             base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    #         )

    async def generate_content(self, prompt: str) -> str:
        if not self.client:
             return "Error: API Key Missing (OpenRouter)"
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Use standard chat completion API
                response = await self.client.chat.completions.create(
                    model=Config.GEMINI_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Check for content in response
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content
                else:
                    return "Error: Empty response from model"

            except Exception as e:
                error_str = str(e)
                # Handle Rate Limits (429) or Server Errors (5xx)
                if ("429" in error_str or 
                    "503" in error_str or 
                    "502" in error_str or
                    "overloaded" in error_str or
                    "UNAVAILABLE" in error_str):
                    
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        print(f"OpenRouter/Gemini Busy (Attempt {attempt+1}/{max_retries}). Retrying in {wait_time}s... Error: {error_str[:100]}")
                        await asyncio.sleep(wait_time)
                        continue
                return f"Error Generating RPP: {error_str}"
        return "Error: Failed after retries (OpenRouter/Gemini System Busy)"

gemini_client = GeminiClient()
