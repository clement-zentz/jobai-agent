# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/services/job_offer.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.job_offer import JobOffer
from app.repositories.job_offer import JobOfferRepository
from app.schemas.job_offer import JobOfferCreate, JobOfferUpdate


class JobOfferService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = JobOfferRepository(session)

    async def create_manual(
        self,
        data: JobOfferCreate,
    ) -> JobOffer:
        """
        Create a job offer manually (user is the source of truth).
        """
        job_offer = JobOffer(**data.model_dump())
        await self.repo.add(job_offer)
        await self.session.commit()
        await self.session.refresh(job_offer)

        return job_offer

    async def create_from_email_ingestion(
        self,
        data: dict,
    ) -> JobOffer | None:
        platform = data.get("platform")
        job_key = data.get("job_key")
        raw_url = data.get("raw_url")

        # 1. Strong de-duplication: platform + job_key
        if platform and job_key:
            existing = await self.repo.get_by_job_key(
                platform=platform,
                job_key=job_key,
            )
            if existing:
                return None

        # 2. Fallback de-duplication: raw_url
        if raw_url:
            existing = await self.repo.get_by_raw_url(raw_url)
            if existing:
                return None

        # 3. Create new job offer
        job_offer = JobOffer(
            title=data.get("title", ""),
            company=data.get("company", ""),
            location=data.get("location"),
            rating=data.get("rating"),
            salary=data.get("salary"),
            summary=data.get("summary"),
            job_key=job_key,
            platform=platform or "unknown",
            raw_url=raw_url,
            canonical_url=data.get("canonical_url"),
            source_email_id=data.get("source", {}).get("uid"),
            posted_at=data.get("posted_at"),
            easy_apply=data.get("easy_apply"),
            active_hiring=data.get("active_hiring"),
        )

        await self.repo.add(job_offer)
        return job_offer

    async def get_offer(
        self,
        job_offer_id: int,
    ) -> JobOffer:
        job_offer = await self.repo.get_by_id(job_offer_id)
        if not job_offer:
            raise ValueError("Job offer not found")
        return job_offer

    async def list_offers(
        self,
        *,
        platform: str | None = None,
        company: str | None = None,
        has_application: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JobOffer]:
        return await self.repo.list(
            platform=platform,
            company=company,
            has_application=has_application,
            limit=limit,
            offset=offset,
        )

    async def update_offer(
        self,
        job_offer_id: int,
        data: JobOfferUpdate,
    ) -> JobOffer:
        job_offer = await self.repo.get_by_id(job_offer_id)
        if not job_offer:
            raise ValueError("Job offer not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(job_offer, field, value)

        await self.session.commit()
        await self.session.refresh(job_offer)
        return job_offer


def get_job_offer_service(
    session: AsyncSession = Depends(get_session),
) -> JobOfferService:
    return JobOfferService(session)
