import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    try:
        print("Fetching available models...")
        # Note: The new SDK listing might differ, we'll try the standard way
        # For google-genai, it's usually client.models.list()
        # But let's try to just use valid known models if list fails
        # Actually for google-genai:
        pager = client.models.list()
        for model in pager:
            print(f"- {model.name}")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
