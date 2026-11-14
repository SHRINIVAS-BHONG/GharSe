from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from bson import ObjectId
from app.config import settings
from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, MeResponse, SendEmailRequest, ResetEmailPasswordRequest, VerifyEmailRequest, ResendVerificationRequest
from app.utils.security import hash_password, verify_password, sign_token
from app.middleware.auth import get_current_user
from app.models.mongo_utils import serialize_doc
from app.services.email_service import send_reset_code, verify_reset_code, send_verification_code, verify_email_code, _dispatch_smtp_email

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, background_tasks: BackgroundTasks):
    try:
        name = (payload.name or "").strip()
        email = (payload.email or "").strip().lower()
        password = payload.password or ""
        role = payload.role

        if not name or not password or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name, email, and password are required."
            )

        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters."
            )

        if role not in ["customer", "seller"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role for self-registration."
            )

        db = get_db()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is currently connecting. Please try again in a few seconds."
            )
        
        existing = await db.users.find_one({"email": email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists."
            )

        now = datetime.now(timezone.utc)
        password_hash = hash_password(password)

        # In pilot mode or when SMTP is not configured, auto-verify so users are not blocked
        auto_verify = not bool(settings.SMTP_USER and settings.SMTP_PASSWORD)

        user_doc = {
            "name": name,
            "email": email,
            "phone": (payload.phone or "").strip() or None,
            "passwordHash": password_hash,
            "role": role,
            "locality": (payload.locality or "").strip() if payload.locality else None,
            "approximateLocation": payload.approximateLocation.dict() if payload.approximateLocation else None,
            "foodPreferences": payload.foodPreferences or [],
            "isVerified": auto_verify,
            "isDemo": False,
            "createdAt": now,
            "updatedAt": now
        }

        result = await db.users.insert_one(user_doc)
        user_id = result.inserted_id
        user_doc["_id"] = user_id
        user_doc.pop("passwordHash", None)

        seller_profile_doc = None
        if role == "seller":
            seller_profile_doc = {
                "userId": user_id,
                "bio": (payload.bio or "").strip(),
                "categories": payload.categories or [],
                "verificationStatus": "pending",
                "verificationNotes": "",
                "profilePhoto": "",
                "deliveryRadiusKm": payload.deliveryRadiusKm or 2.0,
                "pickupAvailable": payload.pickupAvailable if payload.pickupAvailable is not None else True,
                "deliveryAvailable": payload.deliveryAvailable if payload.deliveryAvailable is not None else False,
                "rating": 0.0,
                "ratingCount": 0,
                "totalOrders": 0,
                "isDemo": False,
                "createdAt": now,
                "updatedAt": now
            }
            sp_result = await db.sellerprofiles.insert_one(seller_profile_doc)
            seller_profile_doc["_id"] = sp_result.inserted_id

        if not auto_verify:
            background_tasks.add_task(send_verification_code, email)
        
        return {
            "message": "Account created successfully." if auto_verify else "Account created. Please verify your email.",
            "email": email,
            "isVerified": auto_verify
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {type(e).__name__} - {str(e)}")

@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    email = (payload.email or "").strip().lower()
    password = payload.password or ""

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required."
        )

    db = get_db()
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email. Please sign up first."
        )

    if user.get("isVerified") is False and (settings.SMTP_USER and settings.SMTP_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified."
        )

    if not verify_password(password, user.get("passwordHash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again or click Forgot Password."
        )

    seller_profile = None
    if user.get("role") == "seller":
        seller_profile = await db.sellerprofiles.find_one({"userId": user["_id"]})

    user_id = str(user["_id"])
    role = user.get("role", "customer")
    token = sign_token(user_id, role)

    user_clean = dict(user)
    user_clean.pop("passwordHash", None)

    return {
        "token": token,
        "user": serialize_doc(user_clean),
        "sellerProfile": serialize_doc(seller_profile)
    }

@router.get("/me", response_model=MeResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    seller_profile = None
    if current_user.get("role") == "seller":
        seller_profile = await db.sellerprofiles.find_one({"userId": ObjectId(current_user["_id"])})

    return {
        "user": current_user,
        "sellerProfile": serialize_doc(seller_profile)
    }

@router.post("/forgot-password/send-email")
async def handle_send_email(payload: SendEmailRequest, background_tasks: BackgroundTasks):
    email = (payload.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email required.")
        
    db = get_db()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found with this email.")
        
    background_tasks.add_task(send_reset_code, email)
    return {"message": "Reset code sent successfully. Please check your email inbox."}

@router.post("/forgot-password/reset")
async def handle_reset_password(payload: ResetEmailPasswordRequest):
    email = (payload.email or "").strip().lower()
    code = (payload.code or "").strip()
    new_password = payload.newPassword or ""
    
    if not email or not code or not new_password:
        raise HTTPException(status_code=400, detail="Missing required fields.")
        
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
        
    if not await verify_reset_code(email, code):
        raise HTTPException(status_code=401, detail="Invalid or expired reset code.")
        
    db = get_db()
    password_hash = hash_password(new_password)
    
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"passwordHash": password_hash}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
        
    return {"message": "Password reset successfully. You can now log in."}

@router.post("/verify-email", response_model=AuthResponse)
async def handle_verify_email(payload: VerifyEmailRequest):
    email = (payload.email or "").strip().lower()
    code = (payload.code or "").strip()

    if not email or not code:
        raise HTTPException(status_code=400, detail="Email and code are required.")

    if not await verify_email_code(email, code):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code.")

    db = get_db()
    user = await db.users.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    await db.users.update_one({"_id": user["_id"]}, {"$set": {"isVerified": True}})
    
    # Update the local dictionary to reflect the db change
    user["isVerified"] = True

    seller_profile = None
    if user.get("role") == "seller":
        seller_profile = await db.sellerprofiles.find_one({"userId": user["_id"]})

    user_id = str(user["_id"])
    role = user.get("role", "customer")
    token = sign_token(user_id, role)

    user_clean = dict(user)
    user_clean.pop("passwordHash", None)

    return {
        "token": token,
        "user": serialize_doc(user_clean),
        "sellerProfile": serialize_doc(seller_profile)
    }

@router.post("/resend-verification")
async def handle_resend_verification(payload: ResendVerificationRequest, background_tasks: BackgroundTasks):
    email = (payload.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")

    db = get_db()
    user = await db.users.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if user.get("isVerified"):
        return {"message": "Email is already verified."}

    background_tasks.add_task(send_verification_code, email)
    return {"message": "Verification code resent successfully."}

@router.get("/get-otp")
async def get_otp(email: str):
    """Retrieve active verification OTP for an email."""
    email = email.strip().lower()
    db = get_db()
    if db is not None:
        rec = await db.verification_codes.find_one({"email": email, "type": "verification"})
        if rec:
            return {"email": email, "code": rec.get("code"), "expiresAt": str(rec.get("expiresAt"))}
    return {"error": "No OTP found for this email"}

@router.get("/debug-smtp")
async def debug_smtp(to: str = "bhongshrinivasm24@gmail.com"):
    """Diagnose port accessibility and SMTP delivery directly on Render."""
    import socket
    report = {}
    for p in [587, 465, 25]:
        try:
            s = socket.create_connection(("smtp.gmail.com", p), timeout=4)
            s.close()
            report[f"port_{p}"] = "SUCCESS"
        except Exception as e:
            report[f"port_{p}"] = f"FAILED: {type(e).__name__} ({e})"
    
    try:
        ok = _dispatch_smtp_email(to, "GharSe SMTP Diagnostic", "123456", "verification")
        report["send_result"] = ok
    except Exception as e:
        report["send_result"] = f"EXCEPTION: {type(e).__name__} ({e})"

    return report
