import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv()

async def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("API Key not found!")
        return

    client = genai.Client(api_key=api_key)
    
    print("Attempting to list models...")
    try:
        # Pager object, iterate to get models
        pager = client.models.list() 
        print("Available Models:")
        for model in pager:
            print(f"- {model.name} (Supported methods: {model.supported_generation_methods})")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    # The sync client methods like models.list() are sync in the new SDK?? 
    # Actually client.models.list() is sync, client.aio.models.list() might be async.
    # The error message in user request implies they are using async client.
    # Let's try the simple sync list first as it's a script.
    
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    try:
        for m in client.models.list():
            print(f"Name: {m.name} | Display: {m.display_name}")
    except Exception as e:
        print(f"Error: {e}")
