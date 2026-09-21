import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/gharse")
db_name = "gharse"
try:
    uri_parts = MONGO_URI.split("/")
    if len(uri_parts) > 3 and uri_parts[3].split("?")[0]:
        db_name = uri_parts[3].split("?")[0]
except Exception:
    pass

async def verify_all():
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[db_name]
    
    result = await db.sellerprofiles.update_many(
        {"verificationStatus": {"$ne": "verified"}},
        {"$set": {"verificationStatus": "verified"}}
    )
    print(f"Updated {result.modified_count} sellers to 'verified' status in database '{db_name}'.")
    
if __name__ == "__main__":
    asyncio.run(verify_all())
