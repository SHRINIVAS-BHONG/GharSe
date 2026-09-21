import random
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)

# In-memory store for email reset codes. In production, use Redis or MongoDB.
email_reset_codes = {}
email_verification_codes = {}

def send_reset_code(email: str):
    """
    Generates a 6-digit code and sends an email via SMTP.
    """
    code = str(random.randint(100000, 999999))
    email_reset_codes[email] = code
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP_USER or SMTP_PASSWORD not configured. Printing code to console instead.")
        logger.info("=" * 40)
        logger.info(f"MOCK EMAIL SENT TO: {email}")
        logger.info(f"SUBJECT: Your Password Reset Code")
        logger.info(f"BODY: Use this 6-digit code to reset your password: {code}")
        logger.info("=" * 40)
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = email
        msg['Subject'] = "GharSe - Password Reset Code"
        
        body = f"Hello,\n\nUse this 6-digit code to reset your password on GharSe:\n\n{code}\n\nThis code will expire shortly.\n\nThanks,\nThe GharSe Team"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Reset code email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")
        # In a real app we might want to raise an HTTPException here, but for now we'll just log it.

def verify_reset_code(email: str, code: str) -> bool:
    """
    Verifies the reset code for a given email.
    """
    stored_code = email_reset_codes.get(email)
    if stored_code and stored_code == code:
        del email_reset_codes[email] # Expire code after use
        return True
    return False

def send_verification_code(email: str):
    """
    Generates a 6-digit code and sends an email via SMTP for account verification.
    """
    code = str(random.randint(100000, 999999))
    email_verification_codes[email] = code
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP_USER or SMTP_PASSWORD not configured. Printing verification code to console instead.")
        logger.info("=" * 40)
        logger.info(f"MOCK VERIFICATION EMAIL SENT TO: {email}")
        logger.info(f"SUBJECT: Welcome to GharSe! Verify your email")
        logger.info(f"BODY: Use this 6-digit code to verify your account: {code}")
        logger.info("=" * 40)
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = email
        msg['Subject'] = "Welcome to GharSe! Verify your email"
        
        body = f"Hello,\n\nWelcome to GharSe! Please use this 6-digit code to verify your email address:\n\n{code}\n\nThanks,\nThe GharSe Team"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Verification code email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")

def verify_email_code(email: str, code: str) -> bool:
    """
    Verifies the email verification code for a given email.
    """
    stored_code = email_verification_codes.get(email)
    if stored_code and stored_code == code:
        del email_verification_codes[email] # Expire code after use
        return True
    return False
