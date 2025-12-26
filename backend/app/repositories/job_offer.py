# backend/app/repositories/job_offer.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job_offer import JobOffer


class JobOfferRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, job_offer: JobOffer) -> None:
        self.session.add(job_offer)

    async def get_by_id(
        self,
        job_offer_id: int,
    ) -> JobOffer | None:
        stmt = (
            select(JobOffer)
            .where(JobOffer.id == job_offer_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_raw_url(
        self,
        raw_url: str,
    ) -> JobOffer | None:
        stmt = (
            select(JobOffer)
            .where(JobOffer.raw_url == raw_url)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_job_key(
        self,
        *,
        platform: str,
        job_key: str,
    ) -> JobOffer | None:
        stmt = (
            select(JobOffer)
            .where(
                JobOffer.platform == platform,
                JobOffer.job_key == job_key,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list(
        self,
        *,
        platform: str | None = None,
        company: str | None = None,
        has_application: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JobOffer]:
        """
        List job offers with optional filters.
        Intended for dashboards and browsing.
        """
        stmt = select(JobOffer)

        if platform is not None:
            stmt = stmt.where(JobOffer.platform == platform)

        if company is not None:
            stmt = stmt.where(JobOffer.company == company)

        if has_application is not None:
            if has_application:
                stmt = stmt.where(JobOffer.applications.any())
            else:
                stmt = stmt.where(~JobOffer.applications.any())
        
        stmt = (
            stmt
            .order_by(JobOffer.date_scraped.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_applications(
        self,
        job_offer_id: int,
    ) -> JobOffer | None:
        """
        Load a JobOffer with its applications eagerly.
        Useful for detail views.
        """
        stmt = (
            select(JobOffer)
            .where(JobOffer.id == job_offer_id)
            .options(selectinload(JobOffer.applications))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
