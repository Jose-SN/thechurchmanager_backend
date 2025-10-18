
import smtplib
from email.message import EmailMessage

from fastapi import HTTPException

from app.core.config import settings

# Get environment variables safely
EMAIL = settings.GMAIL_USERNAME
PASSWORD = settings.GMAIL_PASS

if not EMAIL or not PASSWORD:
    raise ValueError("❌ Missing GMAIL_USERNAME or GMAIL_PASS environment variables")

async def send_gmail(to: str, subject: str, body: str) -> dict:
    """Send a simple text email via Gmail SMTP asynchronously."""
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        # Use SSL for Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(str(EMAIL), str(PASSWORD))
            smtp.send_message(msg)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    # send_gmail("recipient@example.com", "Test Email", "Hello! This is a test email sent from Python.")
    print("✅ Email sent successfully!")
