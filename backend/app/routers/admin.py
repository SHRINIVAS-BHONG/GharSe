from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.database import get_db
from app.config import settings
from app.middleware.auth import require_role
from app.models.mongo_utils import serialize_doc, serialize_docs, parse_object_id
from app.schemas.admin import VerifySellerRequest, UpdateListingStatusRequest, CommissionUpdateRequest
from app.utils.cache import cache

router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(require_role("admin"))])

@router.get("/stats", response_model=dict)
async def get_admin_stats():
    cache_key = "admin_stats"
    cached_stats = await cache.get(cache_key)
    if cached_stats is not None:
        return cached_stats

    db = get_db()
    customers = await db.users.count_documents({"role": "customer"})
    sellers = await db.users.count_documents({"role": "seller"})
    pending_sellers = await db.sellerprofiles.count_documents({"verificationStatus": "pending"})
    active_listings = await db.foodlistings.count_documents({"status": "active"})
    total_orders = await db.orders.count_documents({})
    open_complaints = await db.complaints.count_documents({"status": {"$ne": "resolved"}})

    stats_result = {
        "customers": customers,
        "sellers": sellers,
        "pendingSellers": pending_sellers,
        "activeListings": active_listings,
        "totalOrders": total_orders,
        "openComplaints": open_complaints,
    }

    await cache.set(cache_key, stats_result, ttl_seconds=30, tags=["admin_stats"])
    return stats_result

@router.get("/users", response_model=dict)
async def get_users(
    role: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    db = get_db()
    query = {"role": role} if role else {}
    limit = min(max(1, limit), 200)
    skip = max(0, (page - 1) * limit)

    cursor = db.users.find(query, {"passwordHash": 0}).sort("createdAt", -1).skip(skip)
    users = await cursor.to_list(length=limit)
    return {"users": serialize_docs(users), "page": page, "limit": limit}

@router.get("/sellers", response_model=dict)
async def get_sellers(
    verificationStatus: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    db = get_db()
    query = {"verificationStatus": verificationStatus} if verificationStatus else {}
    limit = min(max(1, limit), 200)
    skip = max(0, (page - 1) * limit)

    cursor = db.sellerprofiles.find(query).sort("createdAt", -1).skip(skip)
    raw_sellers = await cursor.to_list(length=limit)

    if not raw_sellers:
        return {"sellers": [], "page": page, "limit": limit}

    # Batch lookup users to eliminate N+1 queries
    user_ids = list({s["userId"] for s in raw_sellers if s.get("userId")})
    user_docs = await db.users.find({"_id": {"$in": user_ids}}).to_list(length=len(user_ids)) if user_ids else []
    user_map = {str(u["_id"]): u for u in user_docs}

    sellers = []
    for s in raw_sellers:
        u_id = str(s.get("userId"))
        user = user_map.get(u_id)
        s_copy = dict(s)
        if user:
            s_copy["userId"] = {
                "_id": str(user["_id"]),
                "name": user.get("name"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "locality": user.get("locality"),
                "createdAt": user.get("createdAt").isoformat() if isinstance(user.get("createdAt"), datetime) else user.get("createdAt")
            }
        sellers.append(serialize_doc(s_copy))

    return {"sellers": sellers, "page": page, "limit": limit}

@router.put("/sellers/{id}/verify", response_model=dict)
async def verify_seller(id: str, payload: VerifySellerRequest):
    seller_id = parse_object_id(id)
    if payload.status not in ["verified", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid verification status.")

    db = get_db()
    set_dict = {
        "verificationStatus": payload.status,
        "updatedAt": datetime.now(timezone.utc)
    }
    if payload.notes is not None:
        set_dict["verificationNotes"] = payload.notes

    updated_seller = await db.sellerprofiles.find_one_and_update(
        {"_id": seller_id},
        {"$set": set_dict},
        return_document=True
    )
    if not updated_seller:
        raise HTTPException(status_code=404, detail="Seller not found.")

    # Invalidate cache
    await cache.invalidate_tags(["admin_stats", "sellers", f"seller:{seller_id}"])

    return {"seller": serialize_doc(updated_seller)}

@router.get("/listings", response_model=dict)
async def get_listings(
    page: int = 1,
    limit: int = 50
):
    db = get_db()
    limit = min(max(1, limit), 200)
    skip = max(0, (page - 1) * limit)

    cursor = db.foodlistings.find({}).sort("createdAt", -1).skip(skip)
    raw_listings = await cursor.to_list(length=limit)

    if not raw_listings:
        return {"listings": [], "page": page, "limit": limit}

    # Batch lookup sellers and seller user profiles
    seller_ids = list({l["sellerId"] for l in raw_listings if l.get("sellerId")})
    seller_docs = await db.sellerprofiles.find({"_id": {"$in": seller_ids}}).to_list(length=len(seller_ids)) if seller_ids else []
    seller_map = {str(s["_id"]): s for s in seller_docs}

    user_ids = list({s["userId"] for s in seller_docs if s.get("userId")})
    user_docs = await db.users.find({"_id": {"$in": user_ids}}).to_list(length=len(user_ids)) if user_ids else []
    user_map = {str(u["_id"]): u for u in user_docs}

    listings = []
    for l in raw_listings:
        s_id = str(l.get("sellerId"))
        seller = seller_map.get(s_id)
        l_copy = dict(l)
        if seller:
            u_id = str(seller.get("userId"))
            user = user_map.get(u_id)
            seller_copy = dict(seller)
            if user:
                seller_copy["userId"] = {"_id": str(user["_id"]), "name": user.get("name")}
            l_copy["sellerId"] = seller_copy
        listings.append(serialize_doc(l_copy))

    return {"listings": listings, "page": page, "limit": limit}

@router.put("/listings/{id}/status", response_model=dict)
async def update_listing_status(id: str, payload: UpdateListingStatusRequest):
    listing_id = parse_object_id(id)
    if payload.status not in ["active", "hidden", "expired", "soldout"]:
        raise HTTPException(status_code=400, detail="Invalid status.")

    db = get_db()
    updated_listing = await db.foodlistings.find_one_and_update(
        {"_id": listing_id},
        {"$set": {"status": payload.status, "updatedAt": datetime.now(timezone.utc)}},
        return_document=True
    )
    if not updated_listing:
        raise HTTPException(status_code=404, detail="Listing not found.")

    # Invalidate cache
    await cache.invalidate_tags(["admin_stats", "foods", f"food:{listing_id}"])

    return {"listing": serialize_doc(updated_listing)}

@router.get("/orders", response_model=dict)
async def get_admin_orders(
    page: int = 1,
    limit: int = 50
):
    db = get_db()
    limit = min(max(1, limit), 200)
    skip = max(0, (page - 1) * limit)

    cursor = db.orders.find({}).sort("createdAt", -1).skip(skip)
    raw_orders = await cursor.to_list(length=limit)

    if not raw_orders:
        return {"orders": [], "page": page, "limit": limit}

    # Batch lookup customers, sellers, and seller users
    customer_ids = list({o["customerId"] for o in raw_orders if o.get("customerId")})
    seller_ids = list({o["sellerId"] for o in raw_orders if o.get("sellerId")})

    customer_docs = await db.users.find({"_id": {"$in": customer_ids}}).to_list(length=len(customer_ids)) if customer_ids else []
    customer_map = {str(c["_id"]): c for c in customer_docs}

    seller_docs = await db.sellerprofiles.find({"_id": {"$in": seller_ids}}).to_list(length=len(seller_ids)) if seller_ids else []
    seller_map = {str(s["_id"]): s for s in seller_docs}

    seller_user_ids = list({s["userId"] for s in seller_docs if s.get("userId")})
    seller_user_docs = await db.users.find({"_id": {"$in": seller_user_ids}}).to_list(length=len(seller_user_ids)) if seller_user_ids else []
    seller_user_map = {str(u["_id"]): u for u in seller_user_docs}

    orders = []
    for o in raw_orders:
        c_id = str(o.get("customerId"))
        s_id = str(o.get("sellerId"))

        cust = customer_map.get(c_id)
        seller = seller_map.get(s_id)

        o_copy = dict(o)
        if cust:
            o_copy["customerId"] = {"_id": str(cust["_id"]), "name": cust.get("name")}
        if seller:
            su_id = str(seller.get("userId"))
            user = seller_user_map.get(su_id)
            seller_copy = dict(seller)
            if user:
                seller_copy["userId"] = {"_id": str(user["_id"]), "name": user.get("name")}
            o_copy["sellerId"] = seller_copy
        orders.append(serialize_doc(o_copy))

    return {"orders": orders, "page": page, "limit": limit}

@router.get("/complaints", response_model=dict)
async def get_admin_complaints(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    db = get_db()
    query = {"status": status} if status else {}
    limit = min(max(1, limit), 200)
    skip = max(0, (page - 1) * limit)

    cursor = db.complaints.find(query).sort("createdAt", -1).skip(skip)
    raw_complaints = await cursor.to_list(length=limit)

    if not raw_complaints:
        return {"complaints": [], "page": page, "limit": limit}

    # Batch lookup customers, orders, sellers, and seller users
    customer_ids = list({c["customerId"] for c in raw_complaints if c.get("customerId")})
    order_ids = list({c["orderId"] for c in raw_complaints if c.get("orderId")})
    seller_ids = list({c["sellerId"] for c in raw_complaints if c.get("sellerId")})

    customer_docs = await db.users.find({"_id": {"$in": customer_ids}}).to_list(length=len(customer_ids)) if customer_ids else []
    customer_map = {str(c["_id"]): c for c in customer_docs}

    order_docs = await db.orders.find({"_id": {"$in": order_ids}}).to_list(length=len(order_ids)) if order_ids else []
    order_map = {str(o["_id"]): o for o in order_docs}

    seller_docs = await db.sellerprofiles.find({"_id": {"$in": seller_ids}}).to_list(length=len(seller_ids)) if seller_ids else []
    seller_map = {str(s["_id"]): s for s in seller_docs}

    seller_user_ids = list({s["userId"] for s in seller_docs if s.get("userId")})
    seller_user_docs = await db.users.find({"_id": {"$in": seller_user_ids}}).to_list(length=len(seller_user_ids)) if seller_user_ids else []
    seller_user_map = {str(u["_id"]): u for u in seller_user_docs}

    complaints = []
    for c in raw_complaints:
        c_id = str(c.get("customerId"))
        ord_id = str(c.get("orderId"))
        s_id = str(c.get("sellerId"))

        cust = customer_map.get(c_id)
        ord_doc = order_map.get(ord_id)
        seller = seller_map.get(s_id)

        c_copy = dict(c)
        if cust:
            c_copy["customerId"] = {
                "_id": str(cust["_id"]),
                "name": cust.get("name"),
                "phone": cust.get("phone"),
                "email": cust.get("email")
            }
        if ord_doc:
            c_copy["orderId"] = serialize_doc(ord_doc)
        if seller:
            su_id = str(seller.get("userId"))
            user = seller_user_map.get(su_id)
            seller_copy = dict(seller)
            if user:
                seller_copy["userId"] = {"_id": str(user["_id"]), "name": user.get("name")}
            c_copy["sellerId"] = seller_copy
        complaints.append(serialize_doc(c_copy))

    return {"complaints": complaints, "page": page, "limit": limit}

@router.put("/complaints/{id}", response_model=dict)
async def update_complaint(id: str, payload: dict):
    complaint_id = parse_object_id(id)
    db = get_db()
    set_dict = {"updatedAt": datetime.now(timezone.utc)}
    if "status" in payload:
        set_dict["status"] = payload["status"]
    if "resolution" in payload:
        set_dict["resolution"] = payload["resolution"]

    updated = await db.complaints.find_one_and_update(
        {"_id": complaint_id},
        {"$set": set_dict},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    # Invalidate cache
    await cache.invalidate_tags(["admin_stats"])

    return {"complaint": serialize_doc(updated)}

@router.get("/commission", response_model=dict)
async def get_commission():
    cached_val = await cache.get("platform_commission")
    if cached_val is not None:
        return {"commissionPercent": float(cached_val)}

    db = get_db()
    config = await db.platformconfigs.find_one({"key": "singleton"})
    if not config:
        commission = float(settings.DEFAULT_COMMISSION_PERCENT)
        await cache.set("platform_commission", commission, ttl_seconds=300, tags=["platform_config"])
        return {"commissionPercent": commission}
    commission = float(config.get("commissionPercent", settings.DEFAULT_COMMISSION_PERCENT))
    await cache.set("platform_commission", commission, ttl_seconds=300, tags=["platform_config"])
    return {"commissionPercent": commission}

@router.put("/commission", response_model=dict)
async def set_commission(payload: CommissionUpdateRequest):
    val = float(payload.commissionPercent)
    if val < 0 or val > 100:
        raise HTTPException(status_code=400, detail="Commission must be a number between 0 and 100.")

    db = get_db()
    now = datetime.now(timezone.utc)
    config = await db.platformconfigs.find_one_and_update(
        {"key": "singleton"},
        {
            "$set": {
                "commissionPercent": val,
                "updatedAt": now
            },
            "$setOnInsert": {
                "key": "singleton",
                "createdAt": now
            }
        },
        upsert=True,
        return_document=True
    )

    # Invalidate cache
    await cache.invalidate_tags(["platform_config"])

    return {"commissionPercent": float(config.get("commissionPercent", val))}
