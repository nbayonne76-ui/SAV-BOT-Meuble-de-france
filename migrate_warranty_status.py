#!/usr/bin/env python
"""Migrate warranty_status column from VARCHAR(50) to VARCHAR(200)"""
import asyncio
import sys
sys.path.insert(0, 'backend')

async def migrate_warranty_status():
    """Increase warranty_status column size to handle longer messages"""
    from app.db.session import engine
    from sqlalchemy import text

    async with engine.begin() as conn:
        print("[INFO] Migrating warranty_status column...")

        # Alter column type
        await conn.execute(
            text("""
            ALTER TABLE sav_tickets
            ALTER COLUMN warranty_status TYPE VARCHAR(200);
            """)
        )

        print("[SUCCESS] Column warranty_status migrated to VARCHAR(200)")

        # Verify
        result = await conn.execute(
            text("""
            SELECT
                column_name,
                data_type,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'sav_tickets'
              AND column_name = 'warranty_status';
            """)
        )

        row = result.first()
        if row:
            print(f"\n[VERIFICATION]")
            print(f"  Column: {row[0]}")
            print(f"  Type: {row[1]}")
            print(f"  Max Length: {row[2]}")

if __name__ == "__main__":
    asyncio.run(migrate_warranty_status())
