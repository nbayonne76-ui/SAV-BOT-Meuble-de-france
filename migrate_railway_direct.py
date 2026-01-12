#!/usr/bin/env python
"""Migrate Railway PostgreSQL database directly with URL argument"""
import asyncio
import asyncpg
import sys

async def migrate_railway(database_url: str):
    """Connect to Railway PostgreSQL and migrate warranty_status column"""

    if not database_url:
        print("[ERROR] DATABASE_URL not provided")
        print("\nUsage: python migrate_railway_direct.py <database_url>")
        return False

    # Convert to asyncpg format if needed
    if database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://", 1)
    elif database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    print(f"[INFO] Connecting to Railway PostgreSQL...")

    try:
        # Connect to Railway database
        conn = await asyncpg.connect(database_url)
        print("[INFO] Connected successfully!")

        print("[INFO] Migrating warranty_status column...")

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
        return True

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR] Missing DATABASE_URL argument")
        print("\nUsage: python migrate_railway_direct.py <database_url>")
        print("\nExample:")
        print('  python migrate_railway_direct.py "postgresql://user:password@host:5432/database"')
        sys.exit(1)

    database_url = sys.argv[1]
    success = asyncio.run(migrate_railway(database_url))
    sys.exit(0 if success else 1)
