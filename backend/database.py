"""
Database connection and CRUD operations for Tasks
Uses Aiven PostgreSQL
"""
import os
import asyncpg
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

# Database connection pool
_pool: Optional[asyncpg.Pool] = None

# Aiven PostgreSQL connection string from environment
DATABASE_URL = os.getenv("AIVEN_DB_URL", "postgresql://user:pass@localhost:5432/db")

async def init_db_pool():
    """Initialize database connection pool"""
    global _pool
    if _pool is None:
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            ssl=ssl_context,
            command_timeout=10,
            timeout=10
        )

        # Create table if not exists
        async with _pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    completed BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            ''')
    return _pool

async def close_db_pool():
    """Close database connection pool"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

async def get_all_tasks() -> List[Dict]:
    """Get all tasks from database"""
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT id, description, priority, completed, created_at FROM tasks ORDER BY id')
        return [dict(row) for row in rows]

async def create_task(description: str, priority: str = "medium") -> Dict:
    """Create a new task"""
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'INSERT INTO tasks (description, priority, completed) VALUES ($1, $2, $3) RETURNING id, description, priority, completed, created_at',
            description, priority, False
        )
        return dict(row)

async def update_task_status(task_id: int, completed: bool) -> Optional[Dict]:
    """Update task completion status"""
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'UPDATE tasks SET completed = $2 WHERE id = $1 RETURNING id, description, priority, completed, created_at',
            task_id, completed
        )
        return dict(row) if row else None

async def delete_task(task_id: int) -> Optional[Dict]:
    """Delete a task"""
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'DELETE FROM tasks WHERE id = $1 RETURNING id, description, priority, completed',
            task_id
        )
        return dict(row) if row else None
