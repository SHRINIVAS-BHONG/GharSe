from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.database import get_db
from app.schemas.review import ReviewCreateRequest
from app.middleware.auth import get_current_user
from app.models.mongo_utils import serialize_doc, serialize_docs, parse_object_id
from app.utils.cache import cache

router = APIRouter(tags=["Reviews"])

@router.post("/api/reviews", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_review(
    payload: ReviewCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    order_id = parse_object_id(payload.orderId)
    rating = payload.rating
    comment = (payload.comment or "").strip()

    if not rating or rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

    db = get_db()
    order = await db.orders.find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if str(order.get("customerId")) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You can only review your own orders.")

    if order.get("status") != "completed":
        raise HTTPException(status_code=400, detail="You can only review completed orders.")

    existing = await db.reviews.find_one({"orderId": order_id})
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this order.")

    now = datetime.now(timezone.utc)
    review_doc = {
        "customerId": ObjectId(current_user["_id"]),
        "sellerId": order["sellerId"],
        "orderId": order_id,
        "rating": rating,
        "comment": comment,
        "isDemo": False,
        "createdAt": now,
        "updatedAt": now
    }

    result = await db.reviews.insert_one(review_doc)
    review_doc["_id"] = result.inserted_id

    # Atomic update for seller rating to prevent race conditions and math drift
    await db.sellerprofiles.update_one(
        {"_id": order["sellerId"]},
        [
            {
                "$set": {
                    "ratingTotal": {"$add": [{"$ifNull": ["$ratingTotal", 0]}, rating]},
                    "ratingCount": {"$add": [{"$ifNull": ["$ratingCount", 0]}, 1]},
                    "updatedAt": now
                }
            },
            {
                "$set": {
                    "rating": {"$round": [{"$divide": ["$ratingTotal", "$ratingCount"]}, 1]}
                }
            }
        ]
    )

    # Invalidate caches
    await cache.invalidate_tags([f"seller:{order['sellerId']}", f"reviews:{order['sellerId']}", "sellers", "admin_stats"])

    return {"review": serialize_doc(review_doc)}

@router.get("/api/sellers/{id}/reviews", response_model=dict)
async def get_seller_reviews(id: str):
    cache_key = f"seller_reviews:{id}"
    cached_data = await cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    seller_id = parse_object_id(id)
    db = get_db()
    cursor = db.reviews.find({"sellerId": seller_id}).sort("createdAt", -1)
    raw_reviews = await cursor.to_list(length=100)

    # Batch customer lookup to eliminate N+1 queries
    customer_ids = list({r["customerId"] for r in raw_reviews if r.get("customerId")})
    customer_docs = await db.users.find({"_id": {"$in": customer_ids}}).to_list(length=len(customer_ids)) if customer_ids else []
    customer_map = {str(c["_id"]): c for c in customer_docs}

    reviews = []
    for r in raw_reviews:
        c_id = str(r.get("customerId"))
        cust = customer_map.get(c_id)
        r_copy = dict(r)
        if cust:
            r_copy["customerId"] = {"_id": str(cust["_id"]), "name": cust.get("name")}
        reviews.append(serialize_doc(r_copy))

    response_data = {"reviews": reviews}
    await cache.set(cache_key, response_data, ttl_seconds=60, tags=[f"reviews:{id}", f"seller:{id}"])
    return response_data
