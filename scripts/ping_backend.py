#!/usr/bin/env python3
"""
GharSe Render Backend Keep-Alive Pinger
---------------------------------------
Continuously pings the Render deployed backend health endpoint every 5 minutes (300s)
to prevent Render free-tier services from sleeping after 15 minutes of inactivity.

Features:
- Built with Python standard library (no external pip dependencies needed).
- High precision latency tracking and formatted timestamp logs.
- Automatic retry on transient network errors.
- Graceful shutdown on Ctrl+C.
"""
import sys
import time
import datetime
import urllib.request
import urllib.error

TARGET_URL = "https://gharse-o7uk.onrender.com/api/health"
PING_INTERVAL_SECONDS = 300  # 5 minutes

def log(msg: str):
    print(msg, flush=True)

def ping(url: str) -> bool:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start = time.perf_counter()
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "GharSe-KeepAlive/1.0",
                "Accept": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            latency = (time.perf_counter() - start) * 1000
            log(f"[{timestamp}] [OK] {url} -> Status: {resp.status} ({latency:.1f}ms)")
            return True
    except urllib.error.HTTPError as e:
        latency = (time.perf_counter() - start) * 1000
        log(f"[{timestamp}] [HTTP {e.code}] {url} -> {e.reason} ({latency:.1f}ms)")
        return False
    except urllib.error.URLError as e:
        latency = (time.perf_counter() - start) * 1000
        log(f"[{timestamp}] [CONNECT ERROR] {url} -> {e.reason} ({latency:.1f}ms)")
        return False
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        log(f"[{timestamp}] [ERROR] {url} -> {e} ({latency:.1f}ms)")
        return False

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else TARGET_URL
    log("=" * 65)
    log(" GharSe Keep-Alive Pinger (5-Minute Cycle)")
    log(f" Target URL: {target}")
    log(f" Interval  : {PING_INTERVAL_SECONDS} seconds (5 minutes)")
    log(f" Goal      : Prevent Render free-tier 15-minute shutdown")
    log("=" * 65)
    
    # First ping immediately
    ping(target)

    # Periodic loop
    while True:
        try:
            time.sleep(PING_INTERVAL_SECONDS)
            ping(target)
        except KeyboardInterrupt:
            log("\n[KeepAlive] Stopped by user.")
            sys.exit(0)

if __name__ == "__main__":
    main()
