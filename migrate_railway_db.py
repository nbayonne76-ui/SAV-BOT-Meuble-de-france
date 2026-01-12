#!/usr/bin/env python
"""Migrate Railway PostgreSQL database directly"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def migrate_railway():
    """Connect to Railway PostgreSQL and migrate warranty_status column"""

    # Get Railway DATABASE_URL
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("[ERROR] DATABASE_URL not found in .env")
        return

    # Convert to asyncpg format
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql://", 1)
    elif database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://", 1)
    elif database_url.startswith("postgresql+asyncpg://"):
        pass
    else:
        database_url = database_url.replace("postgresql", "postgresql", 1)

    print(f"[INFO] Connecting to Railway PostgreSQL...")

    try:
        # Connect to Railway database
        conn = await asyncpg.connect(database_url)

        print("[INFO] Connected! Migrating warranty_status column...")

        # Execute migration
        await conn.execute("""
            ALTER TABLE sav_tickets
            ALTER COLUMN warranty_status TYPE VARCHAR(200);
        """)

        print("[SUCCESS] Column warranty_status migrated to VARCHAR(200)")

        # Verify
        row = await conn.fetchrow("""
            SELECT
                column_name,
                data_type,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'sav_tickets'
              AND column_name = 'warranty_status';
        """)

        if row:
            print(f"\n[VERIFICATION]")
            print(f"  Column: {row['column_name']}")
            print(f"  Type: {row['data_type']}")
            print(f"  Max Length: {row['character_maximum_length']}")

        await conn.close()
        print("\n[DONE] Migration completed successfully!")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(migrate_railway())
