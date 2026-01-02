# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/email_ingestion.py

import logging

from sqlalchemy.ext.asyncio.session import AsyncSession

from app.extraction.email.email_alert_fetcher import EmailAlertFetcher
from app.extraction.email.job_extraction_service import JobExtractionService
from app.models.job_offer import JobOffer
from app.services.job_offer import JobOfferService

logger = logging.getLogger(__name__)


class JobIngestionService:
    """Service to ingest job offers from various sources into the database"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.job_offer_service = JobOfferService(session)

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

        extractor = JobExtractionService()
        extracted_jobs = extractor.extract_jobs(emails)

        created_jobs: list[JobOffer] = []

        for raw_job in extracted_jobs:
            job_offer = await self.job_offer_service.create_from_email_ingestion(
                raw_job
            )
            if job_offer:
                created_jobs.append(job_offer)

        await self.session.commit()
        return created_jobs
