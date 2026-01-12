import asyncio
import sys
import os

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db
# Import Models to register them with Base
from app.models import user, curriculum, rpp_data, payment

async def main():
    print("Initializing Database Tables...")
    try:
        await init_db()
        print("✅ Tables Created Successfully (including saved_rpps).")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    asyncio.run(main())
