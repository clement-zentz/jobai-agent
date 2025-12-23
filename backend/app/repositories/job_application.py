# backend/repositories/job_application.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_application import JobApplication

class JobApplicationRepository:
    async def create(
            self,
            session: AsyncSession,
            app: JobApplication,
    ) -> JobApplication:
        session.add(app)
        await session.commit()
        await session.refresh(app)
        return app
    
    async def list(
        self,
        session: AsyncSession,
    ) -> list[JobApplication]:
        result = await session.execute(select(JobApplication))
        return list(result.scalars().all())
    
    async def get(
        self,
        session: AsyncSession,
        application_id: int,
    ) -> JobApplication | None:
        return await session.get(JobApplication, application_id)
