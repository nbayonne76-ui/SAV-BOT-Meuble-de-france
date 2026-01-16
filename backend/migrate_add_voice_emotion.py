#!/usr/bin/env python
"""
Database migration: Add voice emotion fields to sav_tickets table
"""
import asyncio
import asyncpg
from app.core.config import settings

async def migrate():
    """Add voice emotion fields to sav_tickets table"""
    print("Connecting to database...")
    # Convert SQLAlchemy URL to asyncpg format (remove +psycopg2)
    db_url = settings.DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
    conn = await asyncpg.connect(db_url)

    try:
        print("Adding voice_emotion column...")
        await conn.execute("""
            ALTER TABLE sav_tickets
            ADD COLUMN IF NOT EXISTS voice_emotion VARCHAR(50);
        """)

        print("Adding voice_emotion_confidence column...")
        await conn.execute("""
            ALTER TABLE sav_tickets
            ADD COLUMN IF NOT EXISTS voice_emotion_confidence FLOAT;
        """)

        print("Adding voice_emotion_indicators column...")
        await conn.execute("""
            ALTER TABLE sav_tickets
            ADD COLUMN IF NOT EXISTS voice_emotion_indicators JSONB;
        """)

        print("Migration completed successfully!")

        # Verify the migration
        result = await conn.fetch("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'sav_tickets'
            AND column_name LIKE 'voice_emotion%'
            ORDER BY column_name;
        """)

        print("\nVerification - New columns:")
        for row in result:
            print(f"  - {row['column_name']}: {row['data_type']}")

    finally:
        await conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    asyncio.run(migrate())
