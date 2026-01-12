import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("--- START MODEL LIST ---")
    for m in client.models.list():
        if "gemini" in m.name and "flash" in m.name:
            print(f"Model: {m.name}")
    print("--- END MODEL LIST ---")
except Exception as e:
    print(f"Error: {e}")
