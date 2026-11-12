import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    from app.database import connect_db, close_db
    from app.services.seed_data import seed_all_foods
    
    print("Connecting to database...")
    await connect_db()
    
    print("Starting marketplace seeding (15 Gurgaon/Sohna + 100 All India)...")
    res = await seed_all_foods(force=True)
    print("Seed result:", res)
    
    await close_db()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(main())
