# backend/repositories/job_application.py

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_application import JobApplication

class JobApplicationRepository:
    async def create(
            self,
            session: AsyncSession,
            job_application: JobApplication,
    ) -> JobApplication:
        session.add(job_application)
        await session.commit()
        await session.refresh(job_application)
        return job_application
    
    async def get_by_id_with_offer(
        self,
        session: AsyncSession,
        job_application_id: int,
    ) -> JobApplication | None:
        stmt = (
            select(JobApplication)
            .where(JobApplication.id == job_application_id)
            .options(selectinload(JobApplication.job_offer))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_with_offer(
        self,
        session: AsyncSession,
    ) -> list[JobApplication]:
        stmt = (
            select(JobApplication)
            .options(selectinload(JobApplication.job_offer))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
