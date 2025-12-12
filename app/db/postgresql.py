import asyncpg
import logging
import ssl
from app.core.config import settings

pool = None

async def connect_postgresql():
    """
    Create and return an asyncpg connection pool for PostgreSQL.
    Similar to Node.js Pool pattern with SSL support.
    """
    global pool
    
    if pool is not None:
        return pool
    
    try:
        # Determine SSL configuration
        # For production, typically use SSL. For local development, SSL might be disabled.
        # You can add an environment variable like POSTGRESQL_SSL_MODE to control this
        ssl_mode = getattr(settings, 'POSTGRESQL_SSL_MODE', 'prefer')
        
        if ssl_mode == 'require' or ssl_mode == 'prefer':
            # Create SSL context for secure connections
            ssl_config = ssl.create_default_context()
            
            # Handle self-signed certificates
            # If POSTGRESQL_SSL_REJECT_UNAUTHORIZED is False, disable certificate verification
            # Default to False to allow self-signed certificates (similar to Node.js rejectUnauthorized: false)
            ssl_reject_unauthorized = getattr(settings, 'POSTGRESQL_SSL_REJECT_UNAUTHORIZED', False)
            
            if not ssl_reject_unauthorized:
                # Disable hostname checking and certificate verification for self-signed certs
                ssl_config.check_hostname = False
                ssl_config.verify_mode = ssl.CERT_NONE
        else:
            ssl_config = None
        
        pool = await asyncpg.create_pool(
            host=settings.POSTGRESQL_DB_HOST,
            port=settings.POSTGRESQL_DB_PORT,
            user=settings.POSTGRESQL_DB_USER,
            password=settings.POSTGRESQL_DB_PASSWORD,
            database=settings.POSTGRESQL_DB_NAME,
            ssl=ssl_config,
            min_size=1,
            max_size=10,
        )
        
        logging.info("✅ PostgreSQL connection pool created")
        print(f"✅ PostgreSQL connected to {settings.POSTGRESQL_DB_HOST}:{settings.POSTGRESQL_DB_PORT}/{settings.POSTGRESQL_DB_NAME}")
        return pool
        
    except Exception as e:
        logging.error(f"❌ PostgreSQL connection error: {e}")
        raise


async def close_postgresql():
    """Close the PostgreSQL connection pool."""
    global pool
    if pool is not None:
        await pool.close()
        pool = None
        logging.info("PostgreSQL connection pool closed")


def get_pool():
    """Get the current PostgreSQL connection pool."""
    return pool


async def get_connection():
    """
    Alias for connect_postgresql() for backward compatibility.
    Returns the PostgreSQL connection pool.
    """
    return await connect_postgresql()
