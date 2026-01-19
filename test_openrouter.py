
import asyncio
from app.gemini_client import gemini_client
import os
from dotenv import load_dotenv

load_dotenv()

async def test_openrouter():
    print("Testing OpenRouter Connection...")
    print(f"API Key present: {bool(os.getenv('OPENROUTER_API_KEY'))}")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Skipping actual request because OPENROUTER_API_KEY is missing.")
        return

    try:
        response = await gemini_client.generate_content("Hello, introduce yourself briefly.")
        print("\nResponse from OpenRouter:")
        print(response)
    except Exception as e:
        print(f"\nError occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
