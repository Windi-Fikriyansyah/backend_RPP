import asyncio
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app.database import engine, Base
from app.models import user, curriculum, rpp_data, payment

async def fix_db():
    print("Fixing Database Schema...")
    async with engine.begin() as conn:
        # Drop tables that might be out of sync
        print("Dropping transactions and subscriptions tables...")
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn, tables=[
            Base.metadata.tables['transactions'],
            Base.metadata.tables['subscriptions']
        ]))
        
        # Recreate everything
        print("Recreating tables...")
        await conn.run_sync(Base.metadata.create_all)
        
    print("✅ Database Schema Fixed Successfully!")

if __name__ == "__main__":
    asyncio.run(fix_db())
