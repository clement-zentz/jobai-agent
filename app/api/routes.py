# SPDX-License-Identifier: AGPL-3.0-or-later
# app/api/routes.py
import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.database import get_session

# email data processing
from app.ingestion.email_ingestion import JobIngestionService
from app.extraction.email.email_alert_fetcher import EmailExtractionService
from app.ingestion.web_ingestion import ingest_scraped_jobs
from app.scrapers.indeed import IndeedScraper

router = APIRouter(prefix="/scrape", tags=["scraping"])


class EmailProcessingRequest(BaseModel):
    folder: str = Field(default="INBOX", examples=["INBOX"])
    days_back: int = Field(
        1, ge=1, le=30, description="How many days back to look for alerts"
    )


@router.post("/indeed")
async def scrape_indeed(
    query: str,
    location: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    scraper = IndeedScraper()
    results = await scraper.search(query=query, location=location)
    inserted = await ingest_scraped_jobs(results, session)
    return {"found": len(results), "inserted": inserted}


@router.post("/email-datas/")
async def process_email_datas(
    payload: EmailProcessingRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Extract job alerts from email and ingest them into the database.
    """
    email_address = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    
    if not email_address or not password:
        raise RuntimeError("email_address or password is not set.")

    service = JobIngestionService(session)
    new_jobs = await service.ingest_from_email(
        email_address=email_address,
        password=password,
        folder=payload.folder,
        days_back=payload.days_back,
    )

    return {
        "created": len(new_jobs),
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "rating": job.rating,
                'salary': job.salary,
                "location": job.location,
                "url": job.url,
                "active_hiring": job.active_hiring,
                "easy_apply": job.easy_apply,
                "posted_at": job.posted_at,
                "platform": job.platform,
                "source_email_id": job.source_email_id,
            }
            for job in new_jobs
        ],
    }
