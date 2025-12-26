
import smtplib
import ssl
from email.mime.text import MIMEText
import logging

from fastapi import HTTPException

from app.core.config import settings

# Get environment variables safely
EMAIL = settings.GMAIL_USERNAME
PASSWORD = settings.GMAIL_PASS

# SMTP Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

if not EMAIL or not PASSWORD:
    raise ValueError("❌ Missing GMAIL_USERNAME or GMAIL_PASS environment variables")

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

if __name__ == "__main__":
    # send_gmail("recipient@example.com", "Test Email", "Hello! This is a test email sent from Python.")
    print("✅ Email sent successfully!")
