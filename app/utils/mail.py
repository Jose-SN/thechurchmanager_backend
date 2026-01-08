
import smtplib
import ssl
from email.mime.text import MIMEText
import logging
import asyncio

from fastapi import HTTPException

from app.core.config import settings

# Get environment variables safely
EMAIL = settings.GMAIL_USERNAME
PASSWORD = settings.GMAIL_PASS

# SMTP Configuration for Gmail
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Amazon SES Configuration from .env
SES_SMTP_SERVER = getattr(settings, 'SES_SMTP_SERVER', '')
SES_SMTP_PORT = getattr(settings, 'SES_SMTP_PORT', 587)
SES_SMTP_USERNAME = getattr(settings, 'SES_SMTP_USERNAME', '')
SES_SMTP_PASSWORD = getattr(settings, 'SES_SMTP_PASSWORD', '')
SES_FROM_EMAIL = getattr(settings, 'SES_FROM_EMAIL', '')

if not EMAIL or not PASSWORD:
    logging.warning("⚠️ Missing GMAIL_USERNAME or GMAIL_PASS environment variables")

def test_smtp_connection():
    """Test SMTP connection and login at startup"""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(str(EMAIL), str(PASSWORD))
        logging.info("✅ Gmail SMTP connection successful")
        print("✅ Gmail SMTP connection successful")
        return True
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"❌ Gmail SMTP authentication failed: {e}"
        logging.error(error_msg)
        print(error_msg)
        # print("\n📧 Gmail Authentication Solution:")
        # print("⚠️  Google has DEPRECATED 'Less secure app access' (disabled May 2022)")
        # print("✅ You MUST use an App Password instead:")
        # print("\n📝 Steps to Generate App Password:")
        # print("1. Enable 2-Step Verification (if not already enabled):")
        # print("   https://myaccount.google.com/security")
        # print("2. Generate App Password:")
        # print("   https://myaccount.google.com/apppasswords")
        # print("   - Select 'Mail' as the app")
        # print("   - Select 'Other' and name it 'The Church Manager'")
        # print("   - Click 'Generate'")
        # print("3. Copy the 16-character password (no spaces)")
        # print("4. Update your .env file:")
        # print("   GMAIL_PASS=your-16-character-app-password")
        # print("\n💡 Note: You cannot use your regular Gmail password anymore.")
        return False
    except Exception as e:
        error_msg = f"❌ Gmail SMTP connection failed: {e}"
        logging.error(error_msg)
        print(error_msg)
        return False

async def send_gmail(to: str, subject: str, body: str) -> dict:
    """Send a simple text email via Gmail SMTP asynchronously using STARTTLS."""
    import asyncio
    try:
        # Run SMTP operations in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send_sync, to, subject, body)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

def _send_sync(to_email: str, subject: str, body: str):
    """Synchronous email sending function to be run in executor using STARTTLS"""
    msg = MIMEText(body)
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    context = ssl.create_default_context()

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(str(EMAIL), str(PASSWORD))
        server.send_message(msg)

def test_ses_connection():
    """Test Amazon SES SMTP connection and login"""
    if not SES_SMTP_SERVER or not SES_SMTP_USERNAME or not SES_SMTP_PASSWORD:
        logging.warning("⚠️ Missing SES configuration. Please set SES_SMTP_SERVER, SES_SMTP_USERNAME, SES_SMTP_PASSWORD in .env")
        print("⚠️ Missing SES configuration. Please set SES_SMTP_SERVER, SES_SMTP_USERNAME, SES_SMTP_PASSWORD in .env")
        return False
    
    try:
        server = smtplib.SMTP(SES_SMTP_SERVER, SES_SMTP_PORT)
        server.starttls()
        server.login(SES_SMTP_USERNAME, SES_SMTP_PASSWORD)
        server.quit()
        logging.info("✅ Amazon SES SMTP connection successful")
        print("✅ Amazon SES SMTP connection successful")
        return True
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"❌ Amazon SES SMTP authentication failed: {e}"
        logging.error(error_msg)
        print(error_msg)
        print("\n📧 Amazon SES Authentication Solution:")
        print("1. Verify your SES SMTP credentials in AWS Console")
        print("2. Ensure your SES account is out of sandbox mode (if sending to unverified emails)")
        print("3. Check that SES_SMTP_USERNAME and SES_SMTP_PASSWORD are correct in .env")
        return False
    except Exception as e:
        error_msg = f"❌ Amazon SES SMTP connection failed: {e}"
        logging.error(error_msg)
        print(error_msg)
        return False

async def send_ses_email(to: str, subject: str, body: str, from_email: str = None) -> dict:
    """Send email via Amazon SES SMTP asynchronously"""
    if not SES_SMTP_SERVER or not SES_SMTP_USERNAME or not SES_SMTP_PASSWORD:
        raise HTTPException(status_code=500, detail="SES configuration missing. Please set SES_SMTP_SERVER, SES_SMTP_USERNAME, SES_SMTP_PASSWORD in .env")
    
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send_ses_sync, to, subject, body, from_email)
        return {"message": "Email sent successfully via Amazon SES"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email via SES: {str(e)}")

def _send_ses_sync(to_email: str, subject: str, body: str, from_email: str = None):
    """Synchronous Amazon SES email sending function"""
    # Use provided from_email or fall back to SES_FROM_EMAIL or SES_SMTP_USERNAME
    sender_email = from_email or SES_FROM_EMAIL or SES_SMTP_USERNAME
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    
    server = smtplib.SMTP(SES_SMTP_SERVER, SES_SMTP_PORT)
    server.starttls()
    server.login(SES_SMTP_USERNAME, SES_SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    # Test SES connection
    print("Testing Amazon SES connection...")
    if test_ses_connection():
        print("\n✅ SES connection test passed!")
        # Uncomment to send a test email:
        # import asyncio
        # asyncio.run(send_ses_email("recipient@example.com", "SES Test", "Hello from Amazon SES!"))
    else:
        print("\n❌ SES connection test failed. Please check your configuration.")
