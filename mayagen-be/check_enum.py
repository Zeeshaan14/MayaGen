import asyncio
from app.database import engine
from sqlalchemy import text

async def check():
    print("Checking Enum values...")
    async with engine.begin() as conn:
        try:
            # Check enum labels
            # enum_range returns an array of the values
            stmt = text("SELECT enum_range(NULL::jobstatus)")
            result = await conn.execute(stmt)
            print(f"Enum Definition: {result.first()}")
        except Exception as e:
            print(f"Error reading enum: {e}")

        try:
            # Check what's in the table
            stmt = text("SELECT id, status FROM image")
            result = await conn.execute(stmt)
            rows = result.fetchall()
            print(f"Image Table Rows: {rows}")
        except Exception as e:
            print(f"Error reading rows: {e}")

if __name__ == "__main__":
    asyncio.run(check())
