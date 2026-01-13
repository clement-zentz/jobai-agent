# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/web_ingestion.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_posting import JobPosting


async def ingest_scraped_jobs(jobs: list[dict], session: AsyncSession) -> int:
    inserted = 0

    for job in jobs:
        # Avoid duplicate by URL
        stmt = select(JobPosting).where(JobPosting.raw_url == job["raw_url"])
        result = await session.execute(stmt)
        if result.scalars().first():
            continue

        offer = JobPosting(**job)
        session.add(offer)
        inserted += 1

    await session.commit()
    return inserted
