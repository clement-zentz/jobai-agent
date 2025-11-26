# SPDX-License-Identifier: AGPL-3.0-or-later
# app/services/job_ingestion.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.job import JobOffer


async def ingest_scraped_jobs(jobs: list[dict], session: AsyncSession) -> int:
    inserted = 0

    for job in jobs:
        # Avoid duplicate by URL
        stmt = select(JobOffer).where(JobOffer.url == job["url"])
        result = await session.execute(stmt)
        if result.scalars().first():
            continue

        offer = JobOffer(**job)
        session.add(offer)
        inserted += 1

    await session.commit()
    return inserted
