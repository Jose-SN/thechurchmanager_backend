"""
Test script for Amazon SES email sending
Run this script to test SES configuration and send a test email
"""
import asyncio
from app.utils.mail import test_ses_connection, send_ses_email
from app.core.config import settings

async def main():
    print("=" * 60)
    print("Amazon SES Email Test")
    print("=" * 60)
    
    # Check configuration
    print("\n📋 Configuration Check:")
    print(f"  SES_SMTP_SERVER: {settings.SES_SMTP_SERVER or '❌ Not set'}")
    print(f"  SES_SMTP_PORT: {settings.SES_SMTP_PORT}")
    print(f"  SES_SMTP_USERNAME: {settings.SES_SMTP_USERNAME or '❌ Not set'}")
    print(f"  SES_SMTP_PASSWORD: {'✅ Set' if settings.SES_SMTP_PASSWORD else '❌ Not set'}")
    print(f"  SES_FROM_EMAIL: {settings.SES_FROM_EMAIL or '❌ Not set (will use SES_SMTP_USERNAME)'}")
    
    # Test connection
    print("\n🔌 Testing SES Connection...")
    if test_ses_connection():
        print("\n✅ Connection test passed!")
        
        # Ask for recipient email
        recipient = input("\n📧 Enter recipient email address (or press Enter to skip sending): ").strip()
        
        if recipient:
            print(f"\n📤 Sending test email to {recipient}...")
            try:
                result = await send_ses_email(
                    to=recipient,
                    subject="SES Test",
                    body="Hello from Amazon SES! This is a test email."
                )
                print(f"\n✅ {result['message']}")
            except Exception as e:
                print(f"\n❌ Error sending email: {e}")
        else:
            print("\n⏭️  Skipping email send. Connection test passed!")
    else:
        print("\n❌ Connection test failed. Please check your configuration.")
        print("\n💡 Make sure you have set the following in your .env file:")
        print("   SES_SMTP_SERVER=email-smtp.us-east-1.amazonaws.com")
        print("   SES_SMTP_PORT=587")
        print("   SES_SMTP_USERNAME=your-ses-smtp-username")
        print("   SES_SMTP_PASSWORD=your-ses-smtp-password")
        print("   SES_FROM_EMAIL=verified@yourdomain.com")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

