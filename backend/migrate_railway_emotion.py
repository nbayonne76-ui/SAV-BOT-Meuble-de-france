#!/usr/bin/env python
"""
Railway Database Migration: Add voice emotion fields
Run this with your Railway database URL as argument
"""
import asyncio
import asyncpg
import sys


async def migrate_railway(database_url: str):
    """Add voice emotion fields to Railway database"""
    print("=" * 80)
    print("RAILWAY DATABASE MIGRATION - Voice Emotion Fields")
    print("=" * 80)
    print()

    # Convert SQLAlchemy URL to asyncpg format if needed
    if "postgresql+psycopg2://" in database_url:
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")

    print(f"Connecting to Railway database...")
    print(f"Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'hidden'}")
    print()

    try:
        conn = await asyncpg.connect(database_url)
        print("[OK] Connected to database")
        print()

        # Check if table exists
        print("Checking if sav_tickets table exists...")
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'sav_tickets'
            );
        """)

        if not table_exists:
            print("[ERROR] Table 'sav_tickets' does not exist!")
            print("Please create the table first before adding emotion fields.")
            return False

        print("[OK] Table 'sav_tickets' exists")
        print()

        # Check existing columns
        print("Checking existing columns...")
        existing_columns = await conn.fetch("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'sav_tickets'
            AND column_name LIKE 'voice_emotion%'
        """)

        if existing_columns:
            print(f"[INFO] Found {len(existing_columns)} emotion column(s) already:")
            for col in existing_columns:
                print(f"   - {col['column_name']}")
            print()

        # Add voice_emotion column
        print("Adding voice_emotion column...")
        try:
            await conn.execute("""
                ALTER TABLE sav_tickets
                ADD COLUMN IF NOT EXISTS voice_emotion VARCHAR(50);
            """)
            print("[OK] voice_emotion column added (or already exists)")
        except Exception as e:
            print(f"[ERROR] Failed to add voice_emotion: {e}")
            return False

        # Add voice_emotion_confidence column
        print("Adding voice_emotion_confidence column...")
        try:
            await conn.execute("""
                ALTER TABLE sav_tickets
                ADD COLUMN IF NOT EXISTS voice_emotion_confidence FLOAT;
            """)
            print("[OK] voice_emotion_confidence column added (or already exists)")
        except Exception as e:
            print(f"[ERROR] Failed to add voice_emotion_confidence: {e}")
            return False

        # Add voice_emotion_indicators column
        print("Adding voice_emotion_indicators column...")
        try:
            await conn.execute("""
                ALTER TABLE sav_tickets
                ADD COLUMN IF NOT EXISTS voice_emotion_indicators JSONB;
            """)
            print("[OK] voice_emotion_indicators column added (or already exists)")
        except Exception as e:
            print(f"[ERROR] Failed to add voice_emotion_indicators: {e}")
            return False

        print()
        print("Verifying migration...")

        # Verify all columns exist
        result = await conn.fetch("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'sav_tickets'
            AND column_name LIKE 'voice_emotion%'
            ORDER BY column_name;
        """)

        print()
        print("Emotion columns in database:")
        for row in result:
            print(f"   - {row['column_name']}: {row['data_type']}")

        if len(result) == 3:
            print()
            print("=" * 80)
            print("[SUCCESS] Migration completed successfully!")
            print("All 3 emotion fields have been added to the database.")
            print("=" * 80)
            return True
        else:
            print()
            print(f"[WARNING] Expected 3 columns, found {len(result)}")
            return False

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    finally:
        if 'conn' in locals():
            await conn.close()
            print()
            print("Database connection closed.")


async def test_connection(database_url: str):
    """Test connection to Railway database"""
    print("Testing database connection...")

    # Convert URL format if needed
    if "postgresql+psycopg2://" in database_url:
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")

    try:
        conn = await asyncpg.connect(database_url)
        version = await conn.fetchval('SELECT version();')
        print(f"[OK] Connected to: {version.split(',')[0]}")
        await conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_railway_emotion.py <database_url>")
        print()
        print("Example:")
        print('  python migrate_railway_emotion.py "postgresql://user:pass@host:port/dbname"')
        print()
        print("Get your Railway database URL from:")
        print("  1. Open Railway dashboard")
        print("  2. Go to your Postgres service")
        print("  3. Click 'Variables' tab")
        print("  4. Copy the DATABASE_URL value")
        sys.exit(1)

    database_url = sys.argv[1]

    # Test connection first
    if asyncio.run(test_connection(database_url)):
        print()
        # Run migration
        success = asyncio.run(migrate_railway(database_url))
        sys.exit(0 if success else 1)
    else:
        print()
        print("[ERROR] Cannot proceed with migration due to connection failure.")
        sys.exit(1)
