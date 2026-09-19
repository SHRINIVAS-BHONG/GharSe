import os
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from app.database import get_db

router = APIRouter(prefix="/api/waitlist", tags=["Waitlist & Real Server CSV Tracking"])

# Data directory on the server
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REGISTRATIONS_CSV = DATA_DIR / "registrations.csv"
LINK_CLICKS_CSV = DATA_DIR / "link_clicks.csv"

# Initialize CSV headers if files don't exist yet
if not REGISTRATIONS_CSV.exists():
    with open(REGISTRATIONS_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "RegistrationID",
            "TimestampUTC",
            "Name",
            "Contact",
            "Role",
            "LocalityOrCampus",
            "DietaryPreference",
            "FavoriteDishOrSpecialty",
            "ExtraCapacityOrBudget",
            "ReferralOrSource",
            "ClientIP",
            "UserAgent"
        ])

if not LINK_CLICKS_CSV.exists():
    with open(LINK_CLICKS_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "TimestampUTC",
            "Source",
            "ReferralCode",
            "PageUrl",
            "ClientIP",
            "UserAgent"
        ])


class WaitlistRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    contact: str = Field(..., min_length=5, max_length=120)  # Phone or email
    role: str = Field(default="eater", description="'eater' or 'cook'")
    localityOrCampus: str = Field(..., min_length=2, max_length=120)
    dietaryPreference: Optional[str] = "veg"
    favoriteDishOrSpecialty: Optional[str] = ""
    approxBudgetOrPortions: Optional[str] = ""
    sourceOrRef: Optional[str] = ""


class LinkClickRequest(BaseModel):
    source: Optional[str] = "direct"
    referralCode: Optional[str] = ""
    pageUrl: Optional[str] = ""


def get_real_registration_count() -> int:
    if not REGISTRATIONS_CSV.exists():
        return 0
    try:
        with open(REGISTRATIONS_CSV, mode="r", encoding="utf-8") as f:
            # count lines minus header
            lines = sum(1 for line in f if line.strip())
            return max(0, lines - 1)
    except Exception:
        return 0


def get_real_clicks_count() -> int:
    if not LINK_CLICKS_CSV.exists():
        return 0
    try:
        with open(LINK_CLICKS_CSV, mode="r", encoding="utf-8") as f:
            lines = sum(1 for line in f if line.strip())
            return max(0, lines - 1)
    except Exception:
        return 0


@router.post("")
async def register_waitlist(payload: WaitlistRegisterRequest, request: Request):
    """
    Appends real registration to server CSV and returns real queue number.
    Zero mock numbers. Real server file on computer.
    """
    name = payload.name.strip()
    contact = payload.contact.strip()
    role = payload.role.strip().lower()
    locality = payload.localityOrCampus.strip()
    dietary = payload.dietaryPreference or "veg"
    specialty = payload.favoriteDishOrSpecialty or ""
    capacity_budget = payload.approxBudgetOrPortions or ""
    source = payload.sourceOrRef or "direct"

    now_iso = datetime.now(timezone.utc).isoformat()
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Determine real queue number from actual rows in CSV
    current_count = get_real_registration_count()
    queue_number = f"#GS-{current_count + 1:04d}"

    # Append to real server CSV file
    try:
        with open(REGISTRATIONS_CSV, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                queue_number,
                now_iso,
                name,
                contact,
                role,
                locality,
                dietary,
                specialty,
                capacity_budget,
                source,
                client_ip,
                user_agent
            ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record in server CSV: {str(e)}")

    # Also save to MongoDB if active (non-blocking with quick timeout)
    db = get_db()
    if db is not None:
        try:
            import asyncio
            await asyncio.wait_for(
                db.waitlist.insert_one({
                    "queueNumber": queue_number,
                    "timestamp": now_iso,
                    "name": name,
                    "contact": contact,
                    "role": role,
                    "localityOrCampus": locality,
                    "dietaryPreference": dietary,
                    "favoriteDishOrSpecialty": specialty,
                    "approxBudgetOrPortions": capacity_budget,
                    "sourceOrRef": source,
                    "clientIp": client_ip,
                    "userAgent": user_agent
                }),
                timeout=0.8
            )
        except Exception:
            pass

    total_real_registered = current_count + 1

    return {
        "success": True,
        "queueNumber": queue_number,
        "name": name,
        "role": role,
        "localityOrCampus": locality,
        "totalRealRegistered": total_real_registered,
        "message": f"Successfully registered in server CSV as {queue_number}"
    }


@router.post("/track-click")
async def track_link_click(payload: LinkClickRequest, request: Request):
    """
    Logs actual link clicks (e.g. from Netlify URL, WhatsApp, posters) into server CSV.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    try:
        with open(LINK_CLICKS_CSV, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                now_iso,
                payload.source or "direct",
                payload.referralCode or "",
                payload.pageUrl or "",
                client_ip,
                user_agent
            ])
    except Exception:
        pass

    return {"status": "ok", "totalClicks": get_real_clicks_count()}


@router.get("/stats")
async def get_real_waitlist_stats():
    """
    Returns REAL, authentic counts directly calculated from server CSV files.
    No simulated numbers, no fake mocks.
    """
    total_reg = get_real_registration_count()
    total_clicks = get_real_clicks_count()

    # Calculate real roles breakdown by reading registrations.csv
    eaters = 0
    cooks = 0
    recent_entries = []

    if REGISTRATIONS_CSV.exists():
        try:
            with open(REGISTRATIONS_CSV, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                all_rows = list(reader)
                for r in all_rows:
                    if r.get("Role", "").lower() == "cook":
                        cooks += 1
                    else:
                        eaters += 1
                
                # Get last 10 real entries
                for r in reversed(all_rows[-10:]):
                    recent_entries.append({
                        "id": r.get("RegistrationID", ""),
                        "timestamp": r.get("TimestampUTC", ""),
                        "name": r.get("Name", ""),
                        "role": r.get("Role", ""),
                        "locality": r.get("LocalityOrCampus", ""),
                        "contact": r.get("Contact", ""),
                        "source": r.get("ReferralOrSource", "direct")
                    })
        except Exception:
            pass

    conversion_rate = round((total_reg / total_clicks * 100), 1) if total_clicks > 0 else 0.0

    return {
        "totalRegistrations": total_reg,
        "totalClicks": total_clicks,
        "conversionRate": f"{conversion_rate}%",
        "eatersCount": eaters,
        "cooksCount": cooks,
        "csvFilePath": str(REGISTRATIONS_CSV),
        "recentEntries": recent_entries
    }


@router.get("/download-csv")
async def download_registrations_csv():
    """
    Directly streams the authentic server CSV file to the browser.
    """
    if not REGISTRATIONS_CSV.exists():
        raise HTTPException(status_code=404, detail="No registrations CSV file found on server yet.")

    return FileResponse(
        path=str(REGISTRATIONS_CSV),
        filename=f"GharSe_Real_Registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        media_type="text/csv"
    )


@router.get("/download-clicks-csv")
async def download_clicks_csv():
    """
    Directly streams the link clicks CSV file from the server.
    """
    if not LINK_CLICKS_CSV.exists():
        raise HTTPException(status_code=404, detail="No link clicks CSV file found on server yet.")

    return FileResponse(
        path=str(LINK_CLICKS_CSV),
        filename=f"GharSe_Real_Link_Clicks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        media_type="text/csv"
    )
