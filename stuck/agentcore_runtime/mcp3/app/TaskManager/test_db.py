"""
Test database connectivity to Aiven PostgreSQL.
Run this to verify the database connection before deploying.

Usage:
    export AIVEN_DB_URL='postgresql+asyncpg://...'
    python test_db.py
"""
import asyncio
import asyncpg
import os

async def test_connection():
    # Read from environment variable
    db_url = os.getenv('AIVEN_DB_URL')
    if not db_url:
        print("❌ Error: AIVEN_DB_URL environment variable not set")
        print("\nSet it with:")
        print("  export AIVEN_DB_URL='postgresql+asyncpg://...'")
        return

    # Remove the +asyncpg suffix for asyncpg.connect
    db_url_clean = db_url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"Connecting to database...")

    try:
        conn = await asyncpg.connect(db_url_clean)
        print("✅ Connected successfully!")

        # Test query
        version = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version: {version[:50]}...")

        # Create table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                description TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'medium',
                completed BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        ''')
        print("✅ Table 'tasks' created/verified")

        # Test insert
        task_id = await conn.fetchval(
            "INSERT INTO tasks (description, priority, completed) VALUES ($1, $2, $3) RETURNING id",
            "Test task", "high", False
        )
        print(f"✅ Test task inserted with ID: {task_id}")

        # Test select
        tasks = await conn.fetch("SELECT * FROM tasks")
        print(f"✅ Found {len(tasks)} task(s) in database")

        await conn.close()
        print("\n🎉 All tests passed! Database is ready.")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_connection())
