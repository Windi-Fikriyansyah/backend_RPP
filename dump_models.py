import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    with open("models_list.txt", "w") as f:
        for m in client.models.list():
            f.write(f"{m.name}\n")
    print("Done writing models_list.txt")
except Exception as e:
    with open("models_list.txt", "w") as f:
        f.write(f"Error: {e}")
