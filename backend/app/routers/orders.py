from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.database import get_db, get_client
from app.config import settings
from app.schemas.order import OrderCreateRequest, OrderStatusUpdateRequest
from app.middleware.auth import get_current_user
from app.models.mongo_utils import serialize_doc, serialize_docs, parse_object_id
from app.utils.order_number import generate_order_number

from app.utils.cache import cache

router = APIRouter(prefix="/api/orders", tags=["Orders"])

VALID_TRANSITIONS = {
    "placed": ["accepted", "rejected"],
    "accepted": ["preparing", "cancelled"],
    "preparing": ["ready", "cancelled"],
    "ready": ["out_for_delivery", "completed"],
    "out_for_delivery": ["completed"],
    "completed": [],
    "rejected": [],
    "cancelled": [],
}

async def get_commission_percent() -> float:
    cached_val = await cache.get("platform_commission")
    if cached_val is not None:
        return float(cached_val)

    db = get_db()
    config = await db.platformconfigs.find_one({"key": "singleton"})
    if not config:
        commission = float(settings.DEFAULT_COMMISSION_PERCENT)
        await db.platformconfigs.insert_one({
            "key": "singleton",
            "commissionPercent": commission,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        })
        await cache.set("platform_commission", commission, ttl_seconds=300, tags=["platform_config"])
        return commission
    commission = float(config.get("commissionPercent", settings.DEFAULT_COMMISSION_PERCENT))
    await cache.set("platform_commission", commission, ttl_seconds=300, tags=["platform_config"])
    return commission

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    listing_id = parse_object_id(payload.listingId)
    qty = payload.quantity
    fulfillment_type = payload.fulfillmentType

    if not qty or qty < 1:
        raise HTTPException(status_code=400, detail="Quantity must be a whole number of at least 1.")

    if fulfillment_type not in ["pickup", "delivery"]:
        raise HTTPException(status_code=400, detail="Invalid fulfillment type.")

    db = get_db()
    client = get_client()
    
    listing = await db.foodlistings.find_one({"_id": listing_id})
    if not listing or listing.get("status") != "active":
        raise HTTPException(status_code=404, detail="This food is no longer available.")

    seller_profile = await db.sellerprofiles.find_one({"_id": listing["sellerId"]})
    if not seller_profile:
        raise HTTPException(status_code=404, detail="Seller profile not found.")

    if str(seller_profile["userId"]) == str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You cannot order your own food.")

    if fulfillment_type == "pickup" and not listing.get("pickupAvailable"):
        raise HTTPException(status_code=400, detail="Pickup is not available for this listing.")

    if fulfillment_type == "delivery" and not listing.get("deliveryAvailable"):
        raise HTTPException(status_code=400, detail="Delivery is not available for this listing.")

    commission_percent = await get_commission_percent()
    subtotal = float(listing.get("price", 0)) * qty
    delivery_fee = float(listing.get("deliveryFee", 0)) if fulfillment_type == "delivery" else 0.0
    total = subtotal + delivery_fee
    commission_amount = round((subtotal * commission_percent) / 100.0)
    seller_earnings = subtotal - commission_amount

    order_number = await generate_order_number()
    now = datetime.now(timezone.utc)

    order_doc = {
        "orderNumber": order_number,
        "customerId": ObjectId(current_user["_id"]),
        "sellerId": seller_profile["_id"],
        "items": [
            {
                "listingId": listing["_id"],
                "name": listing.get("name"),
                "price": listing.get("price"),
                "quantity": qty
            }
        ],
        "subtotal": subtotal,
        "deliveryFee": delivery_fee,
        "total": total,
        "fulfillmentType": fulfillment_type,
        "deliveryLocality": (payload.deliveryLocality or "").strip() if fulfillment_type == "delivery" else "",
        "contactPhone": (payload.contactPhone or "").strip(),
        "status": "placed",
        "rejectionReason": "",
        "paymentMethod": payload.paymentMethod or "cash",
        "paymentStatus": "pending" if payload.paymentMethod == "upi" else "cash_on_fulfillment",
        "platformCommissionPercent": commission_percent,
        "platformCommissionAmount": commission_amount,
        "sellerEarnings": seller_earnings,
        "isDemo": False,
        "createdAt": now,
        "updatedAt": now
    }

    try:
        async with await client.start_session() as session:
            async with session.start_transaction():
                updated_listing = await db.foodlistings.find_one_and_update(
                    {
                        "_id": listing_id,
                        "remainingQuantity": {"$gte": qty},
                        "status": "active"
                    },
                    [
                        {
                            "$set": {
                                "remainingQuantity": {"$subtract": ["$remainingQuantity", qty]}
                            }
                        },
                        {
                            "$set": {
                                "status": {
                                    "$cond": [{"$lte": ["$remainingQuantity", 0]}, "soldout", "active"]
                                }
                            }
                        }
                    ],
                    return_document=True,
                    session=session
                )

                if not updated_listing:
                    raise HTTPException(
                        status_code=409,
                        detail="Not enough portions remaining."
                    )

                result = await db.orders.insert_one(order_doc, session=session)
                order_doc["_id"] = result.inserted_id
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Failed to process order.")

    # Invalidate cache tags
    await cache.invalidate_tags(["orders", "admin_stats", "foods", f"seller:{seller_profile['_id']}"])

    return {"order": serialize_doc(order_doc)}

@router.get("", response_model=dict)
async def list_orders(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    filter_query = {}

    if current_user.get("role") == "customer":
        filter_query["customerId"] = ObjectId(current_user["_id"])
    elif current_user.get("role") == "seller":
        seller_profile = await db.sellerprofiles.find_one({"userId": ObjectId(current_user["_id"])})
        if not seller_profile:
            raise HTTPException(status_code=403, detail="Seller profile not found.")
        filter_query["sellerId"] = seller_profile["_id"]

    if status:
        filter_query["status"] = status

    limit = min(max(1, limit), 200)
    skip = max(0, (page - 1) * limit)

    cursor = db.orders.find(filter_query).sort("createdAt", -1).skip(skip)
    raw_orders = await cursor.to_list(length=limit)

    if not raw_orders:
        return {"orders": [], "page": page, "limit": limit}

    # Batch lookups to completely eliminate N+1 queries
    customer_ids = list({o["customerId"] for o in raw_orders if o.get("customerId")})
    seller_ids = list({o["sellerId"] for o in raw_orders if o.get("sellerId")})

    customer_docs = await db.users.find({"_id": {"$in": customer_ids}}).to_list(length=len(customer_ids)) if customer_ids else []
    customer_map = {str(c["_id"]): c for c in customer_docs}

    seller_docs = await db.sellerprofiles.find({"_id": {"$in": seller_ids}}).to_list(length=len(seller_ids)) if seller_ids else []
    seller_map = {str(s["_id"]): s for s in seller_docs}

    seller_user_ids = list({s["userId"] for s in seller_docs if s.get("userId")})
    seller_user_docs = await db.users.find({"_id": {"$in": seller_user_ids}}).to_list(length=len(seller_user_ids)) if seller_user_ids else []
    seller_user_map = {str(u["_id"]): u for u in seller_user_docs}

    populated_orders = []
    for order in raw_orders:
        c_id = str(order.get("customerId"))
        s_id = str(order.get("sellerId"))

        customer_doc = customer_map.get(c_id)
        seller_doc = seller_map.get(s_id)

        order_copy = dict(order)
        if customer_doc:
            order_copy["customerId"] = {
                "_id": str(customer_doc["_id"]),
                "name": customer_doc.get("name"),
                "locality": customer_doc.get("locality"),
                "phone": customer_doc.get("phone")
            }
        if seller_doc:
            seller_data = dict(seller_doc)
            su_id = str(seller_doc.get("userId"))
            seller_user_doc = seller_user_map.get(su_id)
            if seller_user_doc:
                seller_data["userId"] = {
                    "_id": str(seller_user_doc["_id"]),
                    "name": seller_user_doc.get("name"),
                    "locality": seller_user_doc.get("locality"),
                    "phone": seller_user_doc.get("phone")
                }
            order_copy["sellerId"] = seller_data

        populated_orders.append(serialize_doc(order_copy))

    return {"orders": populated_orders, "page": page, "limit": limit}

@router.get("/{id}", response_model=dict)
async def get_order_by_id(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    order_id = parse_object_id(id)
    db = get_db()
    order = await db.orders.find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    seller_profile = None
    if current_user.get("role") == "seller":
        seller_profile = await db.sellerprofiles.find_one({"userId": ObjectId(current_user["_id"])})

    is_owner_customer = current_user.get("role") == "customer" and str(order.get("customerId")) == str(current_user["_id"])
    is_owner_seller = seller_profile and str(order.get("sellerId")) == str(seller_profile["_id"])

    if not is_owner_customer and not is_owner_seller and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="You do not have access to this order.")

    customer_doc = await db.users.find_one({"_id": order.get("customerId")})
    seller_doc = await db.sellerprofiles.find_one({"_id": order.get("sellerId")})
    seller_user_doc = None
    if seller_doc:
        seller_user_doc = await db.users.find_one({"_id": seller_doc.get("userId")})

    order_copy = dict(order)
    if customer_doc:
        order_copy["customerId"] = {
            "_id": str(customer_doc["_id"]),
            "name": customer_doc.get("name"),
            "locality": customer_doc.get("locality"),
            "phone": customer_doc.get("phone")
        }
    if seller_doc:
        seller_data = dict(seller_doc)
        if seller_user_doc:
            seller_data["userId"] = {
                "_id": str(seller_user_doc["_id"]),
                "name": seller_user_doc.get("name"),
                "locality": seller_user_doc.get("locality"),
                "phone": seller_user_doc.get("phone")
            }
        order_copy["sellerId"] = seller_data

    return {"order": serialize_doc(order_copy)}

@router.put("/{id}/status", response_model=dict)
async def update_order_status(
    id: str,
    payload: OrderStatusUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    order_id = parse_object_id(id)
    new_status = payload.status
    rejection_reason = payload.rejectionReason or ""

    db = get_db()
    order = await db.orders.find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    seller_profile = await db.sellerprofiles.find_one({"userId": ObjectId(current_user["_id"])})
    is_seller_owner = seller_profile and str(order.get("sellerId")) == str(seller_profile["_id"])
    is_customer_owner = str(order.get("customerId")) == str(current_user["_id"])
    
    current_status = order.get("status")

    if is_customer_owner and new_status == "cancelled" and current_status == "placed":
        pass # Allow customer to cancel
    elif is_seller_owner:
        pass # Seller can update statuses
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to update this order's status.")

    allowed_next = VALID_TRANSITIONS.get(current_status, [])
    if new_status not in allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f'Cannot move order from "{current_status}" to "{new_status}".'
        )

    if new_status == "rejected" and not rejection_reason:
        raise HTTPException(status_code=400, detail="A reason is required to reject an order.")

    now = datetime.now(timezone.utc)
    set_dict = {
        "status": new_status,
        "updatedAt": now
    }

    # If rejected or cancelled, restore stock to listings
    if new_status in ["rejected", "cancelled"]:
        for item in order.get("items", []):
            item_listing_id = item.get("listingId")
            item_qty = item.get("quantity", 0)
            if item_listing_id and item_qty > 0:
                await db.foodlistings.update_one(
                    {"_id": ObjectId(item_listing_id) if not isinstance(item_listing_id, ObjectId) else item_listing_id},
                    {
                        "$inc": {"remainingQuantity": item_qty},
                        "$set": {"status": "active", "updatedAt": now}
                    }
                )
        set_dict["rejectionReason"] = rejection_reason

    if new_status == "completed":
        if order.get("paymentMethod") == "cash":
            set_dict["paymentStatus"] = "cash_on_fulfillment"
        elif order.get("paymentMethod") == "upi":
            set_dict["paymentStatus"] = "paid"
        if seller_profile:
            await db.sellerprofiles.update_one(
                {"_id": seller_profile["_id"]},
                {"$inc": {"totalOrders": 1}, "$set": {"updatedAt": now}}
            )

    updated_order = await db.orders.find_one_and_update(
        {"_id": order_id},
        {"$set": set_dict},
        return_document=True
    )

    # Invalidate caches
    await cache.invalidate_tags(["orders", "admin_stats", "foods", f"seller:{seller_profile['_id']}"])

    return {"order": serialize_doc(updated_order)}
