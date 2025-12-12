"""
Script to run database migrations/create tables.
Run this script to create the teams table in your PostgreSQL database.
"""
import asyncio
import asyncpg
from pathlib import Path
from app.core.config import settings

async def run_migrations():
    """Create tables from SQL files."""
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(
            host=settings.POSTGRESQL_DB_HOST,
            port=settings.POSTGRESQL_DB_PORT,
            user=settings.POSTGRESQL_DB_USER,
            password=settings.POSTGRESQL_DB_PASSWORD,
            database=settings.POSTGRESQL_DB_NAME,
        )
        
        print(f"✅ Connected to PostgreSQL database: {settings.POSTGRESQL_DB_NAME}")
        
        # Read and execute create.sql
        sql_file = Path(__file__).parent / "create.sql"
        if sql_file.exists():
            sql_content = sql_file.read_text()
            # Split by semicolons and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    try:
                        await conn.execute(statement)
                        print(f"✅ Executed: {statement[:50]}...")
                    except Exception as e:
                        print(f"⚠️ Error executing statement: {e}")
                        print(f"Statement: {statement[:100]}...")
        
        # Read and execute create_teams_table.sql
        teams_sql_file = Path(__file__).parent / "create_teams_table.sql"
        if teams_sql_file.exists():
            sql_content = teams_sql_file.read_text()
            statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    try:
                        await conn.execute(statement)
                        print(f"✅ Executed: {statement[:50]}...")
                    except Exception as e:
                        print(f"⚠️ Error executing statement: {e}")
                        print(f"Statement: {statement[:100]}...")
        
        await conn.close()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migrations())

