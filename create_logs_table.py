from app.database import engine, Base
from app.models.rpp_data import GenerationLog
import asyncio

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=[GenerationLog.__table__])
    print("GenerationLog table created successfully!")

if __name__ == "__main__":
    asyncio.run(create_table())
