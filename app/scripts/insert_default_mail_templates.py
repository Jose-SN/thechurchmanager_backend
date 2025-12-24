"""
Script to insert default mail templates (welcome and forgot_password)
"""
import asyncio
import asyncpg
from app.core.config import settings

async def insert_default_templates():
    """Insert default mail templates"""
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(
            host=settings.POSTGRESQL_DB_HOST,
            port=settings.POSTGRESQL_DB_PORT,
            user=settings.POSTGRESQL_DB_USER,
            password=settings.POSTGRESQL_DB_PASSWORD,
            database=settings.POSTGRESQL_DB_NAME,
        )
        
        print("✅ Connected to PostgreSQL")
        
        # Insert welcome template
        welcome_result = await conn.execute("""
            INSERT INTO mail_templates (key, subject, body, created_at, updated_at)
            VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT (key) DO UPDATE SET
                subject = EXCLUDED.subject,
                body = EXCLUDED.body,
                updated_at = NOW()
        """, 
        'welcome',
        'Welcome to The Church Manager',
        'Hello {{name}},\n\nWelcome to The Church Manager! We are excited to have you join our community.\n\nYour account has been successfully created. You can now access all the features and services we offer.\n\nIf you have any questions, please feel free to contact us.\n\nBest regards,\nThe Church Manager Team'
        )
        print(f"✅ Inserted/Updated welcome template: {welcome_result}")
        
        # Insert forgot_password template
        forgot_password_result = await conn.execute("""
            INSERT INTO mail_templates (key, subject, body, created_at, updated_at)
            VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT (key) DO UPDATE SET
                subject = EXCLUDED.subject,
                body = EXCLUDED.body,
                updated_at = NOW()
        """,
        'forgot_password',
        'Password Reset Request - The Church Manager',
        'Hello {{name}},\n\nWe received a request to reset your password for your account.\n\nIf you requested this password reset, please click on the following link to reset your password:\n{{reset_link}}\n\nThis link will expire in {{expiry_time}}.\n\nIf you did not request a password reset, please ignore this email. Your password will remain unchanged.\n\nFor security reasons, please do not share this link with anyone.\n\nBest regards,\nThe Church Manager Team'
        )
        print(f"✅ Inserted/Updated forgot_password template: {forgot_password_result}")
        
        # Insert user_created_by_organization template
        user_created_result = await conn.execute("""
            INSERT INTO mail_templates (key, subject, body, created_at, updated_at)
            VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT (key) DO UPDATE SET
                subject = EXCLUDED.subject,
                body = EXCLUDED.body,
                updated_at = NOW()
        """,
        'user_created_by_organization',
        'Welcome to The Church Manager - Account Created',
        'Hello {{name}},\n\nYour account has been created by {{organization_name}} on The Church Manager platform.\n\nYour login credentials:\nEmail: {{email}}\nPhone: {{phone}}\n\nTo proceed and set your password, please click on the following link to reset your password:\n{{reset_link}}\n\nThis link will redirect you to the forgot password page where you can set your password.\n\nIf you have any questions, please contact your organization administrator.\n\nBest regards,\nThe Church Manager Team'
        )
        print(f"✅ Inserted/Updated user_created_by_organization template: {user_created_result}")
        
        await conn.close()
        print("✅ Default mail templates inserted successfully!")
        
    except Exception as e:
        print(f"❌ Error inserting mail templates: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(insert_default_templates())

