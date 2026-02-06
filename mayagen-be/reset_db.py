import asyncio
from sqlalchemy import text
from app.database import engine
# Import models so they are registered in metadata
from app.models import User, Image, BatchJob, SQLModel

async def reset_database():
    async with engine.begin() as conn:
        print("1. Dropping existing tables...")
        await conn.run_sync(SQLModel.metadata.drop_all)
        
        print("2. Cleaning up Enum types...")
        # Force drop enum types to ensure new values (pending -> queued) are picked up
        await conn.execute(text("DROP TYPE IF EXISTS jobstatus CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS batchjobstatus CASCADE"))
        
        print("3. Recreating tables...")
        await conn.run_sync(SQLModel.metadata.create_all)
        
        print("✅ Database reset successfully! Schema is now up to date.")

if __name__ == "__main__":
    try:
        asyncio.run(reset_database())
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
