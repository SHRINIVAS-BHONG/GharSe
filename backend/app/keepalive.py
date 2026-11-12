import asyncio
import logging
import os
import httpx

logger = logging.getLogger("keepalive")

async def start_keepalive_pinger(interval_seconds: int = 300):
    """
    Periodically pings the Render backend public URL every interval_seconds (default 5 min = 300s)
    to prevent Render's 15-minute free-tier inactivity shutdown.
    """
    ping_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("BACKEND_PING_URL") or "https://gharse-o7uk.onrender.com"
    health_url = f"{ping_url.rstrip('/')}/api/health"
    
    logger.info(f"Keep-alive self-pinger scheduled for {health_url} (interval: {interval_seconds}s)")
    
    # Wait 45s before starting ping loop so service startup completes cleanly
    await asyncio.sleep(45)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                res = await client.get(health_url)
                logger.info(f"[Keep-Alive] Self-ping to {health_url} succeeded (status: {res.status_code})")
            except Exception as e:
                logger.warning(f"[Keep-Alive] Self-ping to {health_url} failed: {e}")
            
            await asyncio.sleep(interval_seconds)

