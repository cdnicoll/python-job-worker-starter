#!/usr/bin/env python3
"""
Idempotent database migration script.
Creates jobs table, PGMQ extension, and job_queue.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import asyncpg


JOBS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    user_id UUID NOT NULL,
    job_parameters JSONB,
    error_message TEXT,
    error_type TEXT,
    error_context JSONB,
    data_references JSONB,
    retry_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS jobs_status_idx ON public.jobs (status);
CREATE INDEX IF NOT EXISTS jobs_user_id_idx ON public.jobs (user_id);
CREATE INDEX IF NOT EXISTS jobs_created_at_idx ON public.jobs (created_at);
"""


async def migrate():
    """Run migrations."""
    url = os.environ.get("TRANSACTION_POOLER_URL")
    if not url:
        print("ERROR: TRANSACTION_POOLER_URL not set")
        sys.exit(1)

    conn = await asyncpg.connect(url)

    try:
        # PGMQ extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pgmq")
        print("✓ PGMQ extension ready")

        # Jobs table
        await conn.execute(JOBS_TABLE_SQL)
        print("✓ jobs table ready")

        # PGMQ queue
        try:
            await conn.execute("SELECT pgmq.create('job_queue')")
        except asyncpg.exceptions.DuplicateObjectError:
            pass  # Queue already exists
        print("✓ job_queue ready")

        print("\nMigration complete.")
    finally:
        await conn.close()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    asyncio.run(migrate())
