import asyncio
from sqlalchemy import text
from app.database import get_session_context

async def debug_query():
    print("🔍 Connecting to database...")
    async with get_session_context() as session:
        print("\n--- RAW TABLE DATA ---")
        result = await session.execute(text("SELECT id, status, created_at FROM image ORDER BY id"))
        rows = result.fetchall()
        print(f"Total Rows: {len(rows)}")
        for row in rows:
            print(f"ID: {row.id} | Status: '{row.status}' (Type: {type(row.status)}) | Created: {row.created_at}")
            
        print("\n--- TESTING WORKER QUERY ---")
        # Exact query from worker.py
        query = text("SELECT id FROM image WHERE status = 'queued'")
        result = await session.execute(query)
        matches = result.fetchall()
        print(f"Query 'WHERE status = ''queued''' matches {len(matches)} rows.")
        if matches:
            print(f"Matched IDs: {[r.id for r in matches]}")
        else:
            print("❌ No matches found for lowercase 'queued'.")
            
        # Test Uppercase
        query_upper = text("SELECT id FROM image WHERE status = 'QUEUED'")
        result = await session.execute(query_upper)
        matches_upper = result.fetchall()
        print(f"Query 'WHERE status = ''QUEUED''' matches {len(matches_upper)} rows.")

        # Test Case Insensitive
        query_ci = text("SELECT id FROM image WHERE status::text ILIKE 'queued'")
        result = await session.execute(query_ci)
        matches_ci = result.fetchall()
        print(f"Query 'WHERE status ILIKE ''queued''' matches {len(matches_ci)} rows.")

if __name__ == "__main__":
    try:
        asyncio.run(debug_query())
    except Exception as e:
        print(f"Error: {e}")
