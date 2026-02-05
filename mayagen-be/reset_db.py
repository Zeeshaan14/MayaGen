import asyncio
from app.database import init_db, engine
from app import models # Ensure models are loaded
from sqlmodel import SQLModel
from sqlalchemy import text

async def reset_database():
    print("Resetting database...")
    async with engine.begin() as conn:
        print("Dropping schema public cascade...")
        # Forcefully drop everything
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        # await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;")) 
        # await conn.execute(text("GRANT ALL ON SCHEMA public TO public;")) 

        print("Creating all tables...")
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Database reset complete.")

if __name__ == "__main__":
    asyncio.run(reset_database())
