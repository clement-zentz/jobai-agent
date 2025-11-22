# SPDX-License-Identifier: AGPL-3.0-or-later
# app/data_ingestion/email_ingestion.py

from typing import Optional

import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.data_extraction.email_extraction.email_alert_fetcher import (
    EmailExtractionService,
)
from app.models.job import JobOffer

logger = logging.getLogger(__name__)

class JobIngestionService:
    """Service to ingest job offers from various sources into the database"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def ingest_from_email(
        self,
        email_address: str,
        password: str,
        folder: str = "INBOX",
        days_back: int = 1,
    ) -> list[JobOffer]:
        """Fetch job alerts from email and save them to database."""
        extractor = EmailExtractionService(email_address, password, folder)
        raw_jobs = extractor.fetch_recent_jobs(days_back)

        new_jobs: list[JobOffer] = []

        for job_data in raw_jobs:

            # check if job already exists by source_uid or unique URL
            existing = await self._find_existing_job(
                source_uid=job_data.get("source_uid"), 
                url=job_data.get("url")
            )

            if existing:
                continue

            job_offer = JobOffer(
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                location=job_data.get("location", ""),
                url=job_data.get("url", ""),
                platform=job_data.get("platform", ""),
                source_email_id=job_data.get("source_uid"),
            )

            self.session.add(job_offer)
            new_jobs.append(job_offer)

        await self.session.commit()

        return new_jobs

    async def _find_existing_job(
        self, source_uid: Optional[str] = None, url: Optional[str] = None
    ) -> Optional[JobOffer]:
        """Check if a job already exists in the database."""
        if source_uid:
            statement = select(JobOffer).where(JobOffer.source_email_id == source_uid)
            result = await self.session.execute(statement)
            job = result.scalars().first()
            if job:
                return job

        if url:
            statement = select(JobOffer).where(JobOffer.url == url)
            result = await self.session.execute(statement)
            return result.scalars().first()

        return None
