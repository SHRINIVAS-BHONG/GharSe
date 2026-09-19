import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db_instance = Database()

async def connect_db():
    logger.info(f"Connecting to MongoDB at {settings.MONGO_URI} with connection pooling...")
    db_instance.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
        minPoolSize=settings.MONGO_MIN_POOL_SIZE,
        maxIdleTimeMS=settings.MONGO_MAX_IDLE_TIME_MS,
        waitQueueTimeoutMS=settings.MONGO_WAIT_QUEUE_TIMEOUT_MS,
        connectTimeoutMS=settings.MONGO_CONNECT_TIMEOUT_MS,
        serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
    )
    # Extract DB name from URI or default to "gharse"
    db_name = "gharse"
    try:
        uri_parts = settings.MONGO_URI.split("/")
        if len(uri_parts) > 3 and uri_parts[3].split("?")[0]:
            db_name = uri_parts[3].split("?")[0]
    except Exception:
        pass
    db_instance.db = db_instance.client[db_name]
    logger.info(f"Connected to MongoDB database '{db_name}' (Pool: {settings.MONGO_MIN_POOL_SIZE}-{settings.MONGO_MAX_POOL_SIZE} connections)")
    await init_indexes()

async def close_db():
    if db_instance.client:
        logger.info("Closing MongoDB connection pool...")
        db_instance.client.close()

async def init_indexes():
    """Create comprehensive MongoDB indexes for high-throughput queries"""
    db = db_instance.db
    if db is None:
        return
    try:
        # Users indexes
        await db.users.create_index("email", unique=True, sparse=True)
        await db.users.create_index("phone", unique=True, sparse=True)
        await db.users.create_index("role")
        await db.users.create_index([("createdAt", -1)])

        # SellerProfile indexes
        await db.sellerprofiles.create_index("userId", unique=True)
        await db.sellerprofiles.create_index([("verificationStatus", 1), ("createdAt", -1)])
        await db.sellerprofiles.create_index([("rating", -1)])

        # FoodListing indexes
        await db.foodlistings.create_index([("status", 1), ("remainingQuantity", 1), ("date", 1)])
        await db.foodlistings.create_index([("status", 1), ("date", 1), ("mealType", 1)])
        await db.foodlistings.create_index([("sellerId", 1), ("status", 1)])
        await db.foodlistings.create_index("sellerId")
        await db.foodlistings.create_index([("createdAt", -1)])
        await db.foodlistings.create_index("price")

        # Orders indexes
        await db.orders.create_index("orderNumber", unique=True)
        await db.orders.create_index([("customerId", 1), ("createdAt", -1)])
        await db.orders.create_index([("sellerId", 1), ("createdAt", -1)])
        await db.orders.create_index([("status", 1), ("createdAt", -1)])
        await db.orders.create_index([("createdAt", -1)])

        # Reviews indexes
        await db.reviews.create_index("orderId", unique=True)
        await db.reviews.create_index([("sellerId", 1), ("createdAt", -1)])
        await db.reviews.create_index([("customerId", 1), ("createdAt", -1)])

        # Complaints indexes
        await db.complaints.create_index([("customerId", 1), ("createdAt", -1)])
        await db.complaints.create_index([("sellerId", 1), ("createdAt", -1)])
        await db.complaints.create_index([("status", 1), ("createdAt", -1)])

        # PlatformConfig singleton index
        await db.platformconfigs.create_index("key", unique=True)

        # Waitlist collection indexes
        await db.waitlist.create_index("email", unique=True, sparse=True)
        await db.waitlist.create_index("phone", unique=True, sparse=True)
        await db.waitlist.create_index([("role", 1), ("createdAt", -1)])
        logger.info("MongoDB high-performance indexes verified.")
    except Exception as e:
        logger.warning(f"Failed to create some indexes: {e}")

def get_db() -> AsyncIOMotorDatabase:
    return db_instance.db

def get_client() -> AsyncIOMotorClient:
    return db_instance.client
