#!/usr/bin/env python
"""Check if tables exist in Railway PostgreSQL database"""
import asyncio
import asyncpg

async def check_tables():
    """Connect to Railway and check if sav_tickets table exists"""

    database_url = "postgresql://postgres:rhuTZdokjJXJMlqNCXltoNhazphIncbT@hopper.proxy.rlwy.net:12551/railway"

    print("[INFO] Connecting to Railway PostgreSQL...")

    try:
        conn = await asyncpg.connect(database_url)
        print("[INFO] Connected successfully!")
        print()

        # Check what tables exist
        print("[INFO] Checking existing tables...")
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        if tables:
            print(f"[INFO] Found {len(tables)} table(s):")
            for table in tables:
                print(f"  - {table['table_name']}")
        else:
            print("[WARNING]   NO TABLES FOUND in database!")
            print("[WARNING] This is the problem - tables need to be created!")

        print()

        # Check specifically for sav_tickets
        sav_tickets_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'sav_tickets'
            );
        """)

        if sav_tickets_exists:
            print("[INFO]  Table 'sav_tickets' exists")

            # Count tickets
            count = await conn.fetchval("SELECT COUNT(*) FROM sav_tickets;")
            print(f"[INFO] Number of tickets in database: {count}")

            if count > 0:
                # Show first few tickets
                tickets = await conn.fetch("""
                    SELECT ticket_id, order_number, created_at
                    FROM sav_tickets
                    ORDER BY created_at DESC
                    LIMIT 5;
                """)
                print(f"[INFO] Recent tickets:")
                for ticket in tickets:
                    print(f"  - {ticket['ticket_id']} | {ticket['order_number']} | {ticket['created_at']}")
        else:
            print("[ERROR]  Table 'sav_tickets' DOES NOT EXIST!")
            print("[ERROR] This is why tickets cannot be saved or retrieved!")
            print()
            print("[SOLUTION] You need to run database initialization to create tables.")

        await conn.close()

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_tables())
