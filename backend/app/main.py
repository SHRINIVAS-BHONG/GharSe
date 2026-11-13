import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pymongo.errors import DuplicateKeyError

from app.config import settings
from app.database import connect_db, close_db
from app.middleware.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    duplicate_key_exception_handler,
    generic_exception_handler
)
from app.routers import auth, foods, orders, sellers, reviews, complaints, admin, waitlist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure uploads directory exists
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing GharSe backend service...")
    import asyncio
    await connect_db()

    # Background async initialization (non-blocking so Uvicorn binds immediately!)
    async def background_init():
        try:
            await asyncio.sleep(2)
            from app.services.seed_data import seed_all_foods
            await seed_all_foods(force=False)
        except Exception as e:
            logger.warning(f"Background seed initialization non-fatal error: {e}")

    asyncio.create_task(background_init())

    # Keep-alive background task to prevent Render 15-minute free-tier idle shutdown
    keepalive_task = None
    if os.getenv("RENDER") or os.getenv("RENDER_EXTERNAL_URL") or os.getenv("ENABLE_SELF_PING", "false").lower() == "true":
        from app.keepalive import start_keepalive_pinger
        keepalive_task = asyncio.create_task(start_keepalive_pinger(interval_seconds=300))
        logger.info("Keep-alive self-ping background worker active (5 min interval)")

    yield
    # Shutdown
    if keepalive_task:
        keepalive_task.cancel()
    logger.info("Shutting down GharSe backend service...")
    await close_db()

app = FastAPI(
    title="GharSe API",
    description="Hyperlocal home-cooked food marketplace API",
    version="1.0.0",
    lifespan=lifespan
)

import time
from fastapi.middleware.gzip import GZipMiddleware

# CORS Middleware
origins = [
    settings.CLIENT_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000"
]

# GZip Compression for payloads > 500 bytes (saves 70-80% payload bandwidth)
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.onrender\.com|http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Process Time & Latency Profiling Middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

# Global Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DuplicateKeyError, duplicate_key_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Serve uploaded static files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Root & Health check routes for uptime monitors & keep-alive pinger
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"status": "ok", "service": "gharse-backend"}

@app.api_route("/health", methods=["GET", "HEAD"])
async def root_health():
    return {"status": "ok", "service": "gharse-backend"}

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok", "service": "gharse-backend"}

# Register Routers
app.include_router(auth.router)
app.include_router(foods.router)
app.include_router(orders.router)
app.include_router(sellers.router)
app.include_router(reviews.router)
app.include_router(complaints.router)
app.include_router(admin.router)
app.include_router(waitlist.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
