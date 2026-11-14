import random
import logging
import smtplib
import asyncio
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)

# In-memory store fallback for verification codes
email_reset_codes = {}
email_verification_codes = {}

def _dispatch_resend(to_email: str, subject: str, html_content: str, plain_text: str) -> bool:
    """Send transactional email via Resend HTTPS API (Port 443, never blocked)."""
    if not settings.RESEND_API_KEY:
        return False
    try:
        import urllib.request
        import json
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "GharSe-Backend/1.0"
        }
        payload = {
            "from": "GharSe <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": plain_text
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status in (200, 201):
                logger.info(f"Email dispatched via Resend HTTPS to {to_email}")
                return True
    except Exception as e:
        logger.warning(f"Resend HTTPS failed for {to_email}: {e}")
    return False

def _dispatch_brevo(to_email: str, subject: str, html_content: str, plain_text: str) -> bool:
    """Send transactional email via Brevo HTTPS API (Port 443, no domain requirement)."""
    if not settings.BREVO_API_KEY:
        return False
    try:
        import urllib.request
        import json
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": settings.BREVO_API_KEY,
            "Content-Type": "application/json",
            "User-Agent": "GharSe-Backend/1.0"
        }
        sender_email = settings.SMTP_USER or "noreply@gharse.app"
        payload = {
            "sender": {"name": "GharSe", "email": sender_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content,
            "textContent": plain_text
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status in (200, 201):
                logger.info(f"Email dispatched via Brevo HTTPS to {to_email}")
                return True
    except Exception as e:
        logger.warning(f"Brevo HTTPS failed for {to_email}: {e}")
    return False

def _dispatch_smtp_email(to_email: str, subject: str, code: str, purpose: str = "verification") -> bool:
    """Synchronous email dispatcher executed in a background thread."""
    heading = "Verify your email address" if purpose == "verification" else "Reset your password"
    email_subject = f"{code} is your GharSe verification code" if purpose == "verification" else f"{code} is your GharSe password reset code"
    subtext = (
        "Thank you for joining GharSe! Please enter this 6-digit code on the verification screen to activate your account."
        if purpose == "verification"
        else "We received a request to reset your password. Enter this 6-digit code to choose a new password."
    )

    plain_text = f"""Hello,

Your GharSe {purpose} code is: {code}

{subtext}

This code expires in 15 minutes. If you did not request this, please ignore this email.

Warm regards,
The GharSe Team
https://gharse-frontend.onrender.com
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #FBF8F3; margin: 0; padding: 20px; }}
    .container {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1px solid #EADBCE; padding: 36px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); }}
    .header {{ text-align: center; margin-bottom: 24px; }}
    .logo {{ font-size: 28px; font-weight: 800; color: #1E3D2F; letter-spacing: -0.5px; }}
    .tagline {{ font-size: 13px; color: #8F7761; margin-top: 4px; }}
    .title {{ font-size: 20px; font-weight: 700; color: #1E221E; margin-bottom: 12px; }}
    .desc {{ font-size: 14px; color: #5B615B; line-height: 1.6; margin-bottom: 24px; }}
    .code-box {{ background: #FFF9ED; border: 2px dashed #E28F2A; border-radius: 14px; padding: 20px; text-align: center; margin: 24px 0; }}
    .code {{ font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #1E3D2F; font-family: 'Courier New', Courier, monospace; }}
    .expiry {{ font-size: 12px; color: #A0722C; margin-top: 8px; font-weight: 500; }}
    .footer {{ margin-top: 32px; padding-top: 20px; border-top: 1px solid #F0E6D8; font-size: 12px; color: #9B9C9B; line-height: 1.5; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">GharSe</div>
      <div class="tagline">Ghar ka khana, aapke paas</div>
    </div>
    <div class="title">{heading}</div>
    <div class="desc">{subtext}</div>
    <div class="code-box">
      <div class="code">{code}</div>
      <div class="expiry">⏱ Valid for 15 minutes · One-time use</div>
    </div>
    <div class="footer">
      If you did not request this email, no action is needed.<br>
      © {datetime.now(timezone.utc).year} GharSe Technologies. All rights reserved.
    </div>
  </div>
</body>
</html>"""

    # 1. First priority: Resend HTTPS API (Port 443)
    if _dispatch_resend(to_email, email_subject, html_content, plain_text):
        return True

    # 2. Second priority: Brevo HTTPS API (Port 443)
    if _dispatch_brevo(to_email, email_subject, html_content, plain_text):
        return True

    # 3. Third priority: SMTP (Port 587/465, works on local or unblocked hosts)
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(f"SMTP not configured. Mock code for {to_email}: {code}")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = f"GharSe <{settings.SMTP_USER}>"
    msg["To"] = to_email
    msg["Subject"] = email_subject
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=4.0)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Verification email sent via port 587 to {to_email}")
        return True
    except Exception as e587:
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=4.0)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            logger.info(f"Verification email sent via port 465 SSL to {to_email}")
            return True
        except Exception as e465:
            logger.warning(f"SMTP ports 587 and 465 failed for {to_email}: {e465}")
            return False

async def send_verification_code(email: str) -> str:
    """Generates 6-digit OTP, stores in DB & in-memory, sends branded HTML email."""
    email = email.strip().lower()
    code = f"{random.randint(100000, 999999)}"
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=15)

    db = get_db()
    if db is not None:
        try:
            await db.verification_codes.update_one(
                {"email": email, "type": "verification"},
                {"$set": {"code": code, "expiresAt": expires_at, "createdAt": now}},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to persist verification code in MongoDB: {e}")

    email_verification_codes[email] = (code, expires_at)
    await asyncio.to_thread(_dispatch_smtp_email, email, "GharSe Verification Code", code, "verification")
    return code

async def verify_email_code(email: str, code: str) -> bool:
    """Validates 6-digit OTP from MongoDB or in-memory fallback."""
    email = email.strip().lower()
    code = code.strip()
    now = datetime.now(timezone.utc)

    db = get_db()
    if db is not None:
        try:
            record = await db.verification_codes.find_one({"email": email, "type": "verification", "code": code})
            if record:
                exp = record.get("expiresAt")
                if exp:
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    if now <= exp:
                        await db.verification_codes.delete_one({"_id": record["_id"]})
                        email_verification_codes.pop(email, None)
                        return True
        except Exception as e:
            logger.warning(f"Error checking MongoDB verification code: {e}")

    # Memory fallback
    if email in email_verification_codes:
        mem_code, mem_exp = email_verification_codes[email]
        if mem_code == code and now <= mem_exp:
            email_verification_codes.pop(email, None)
            return True

    return False

async def send_reset_code(email: str) -> str:
    """Generates 6-digit password reset code, stores in DB & memory, sends email."""
    email = email.strip().lower()
    code = f"{random.randint(100000, 999999)}"
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=15)

    db = get_db()
    if db is not None:
        try:
            await db.verification_codes.update_one(
                {"email": email, "type": "reset"},
                {"$set": {"code": code, "expiresAt": expires_at, "createdAt": now}},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to persist reset code in MongoDB: {e}")

    email_reset_codes[email] = (code, expires_at)
    await asyncio.to_thread(_dispatch_smtp_email, email, "GharSe Password Reset Code", code, "reset")
    return code

async def verify_reset_code(email: str, code: str) -> bool:
    """Validates 6-digit reset code from MongoDB or in-memory fallback."""
    email = email.strip().lower()
    code = code.strip()
    now = datetime.now(timezone.utc)

    db = get_db()
    if db is not None:
        try:
            record = await db.verification_codes.find_one({"email": email, "type": "reset", "code": code})
            if record:
                exp = record.get("expiresAt")
                if exp:
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    if now <= exp:
                        await db.verification_codes.delete_one({"_id": record["_id"]})
                        email_reset_codes.pop(email, None)
                        return True
        except Exception as e:
            logger.warning(f"Error checking MongoDB reset code: {e}")

    # Memory fallback
    if email in email_reset_codes:
        mem_code, mem_exp = email_reset_codes[email]
        if mem_code == code and now <= mem_exp:
            email_reset_codes.pop(email, None)
            return True

    return False
