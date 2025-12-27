# backend/app/services/job_offer.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.job_offer import JobOffer
from app.schemas.job_offer import JobOfferCreate, JobOfferUpdate
from app.repositories.job_offer import JobOfferRepository

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