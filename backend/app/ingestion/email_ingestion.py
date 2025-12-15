# SPDX-License-Identifier: AGPL-3.0-or-later
# app/data_ingestion/email_ingestion.py

from typing import Optional

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.extraction.email.job_extraction_service import JobExtractionService
from app.extraction.email.email_alert_fetcher import EmailAlertFetcher
from app.models.job_offer import JobOffer

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
        email_fetcher = EmailAlertFetcher(email_address, password, folder)
        emails = email_fetcher.fetch_recent(days_back)

        job_extractor = JobExtractionService()
        raw_jobs = job_extractor.extract_jobs(emails)

        new_jobs: list[JobOffer] = []

        for job_data in raw_jobs:

            # check if job already exists by source_uid or unique URL
            existing = await self._find_existing_job(
                url=job_data.get("url")
            )

            if existing:
                continue

            job_offer = JobOffer(
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                rating = job_data.get("rating", None),
                salary = job_data.get("salary", None),
                location=job_data.get("location", ""),
                active_hiring=job_data.get("active_hiring", None),
                easy_apply=job_data.get("easy_apply", None),
                posted_at=job_data.get("posted_at", None),
                url=job_data.get("url", ""),
                platform=job_data.get("platform", ""),
                source_email_id=job_data.get("source_uid"),
            )

            self.session.add(job_offer)
            new_jobs.append(job_offer)

        await self.session.commit()

        return new_jobs

    async def _find_existing_job(
        self, url: Optional[str] = None
    ) -> Optional[JobOffer]:
        """Check if a job already exists in the database with job url."""
        if url:
            statement = select(JobOffer).where(JobOffer.url == url)
            result = await self.session.execute(statement)
            return result.scalars().first()
        return None
