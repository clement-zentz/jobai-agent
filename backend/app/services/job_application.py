# backend/services/job_application.py

from app.models.job_application import JobApplication
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
)
from app.repositories.job_application import JobApplicationRepository

class JobApplicationService:
    def __init__(self) -> None:
        self.repo = JobApplicationRepository()

    async def create_application(
        self,
        session: AsyncSession,
        data: JobApplicationCreate,
    ) -> JobApplication:
        job_application = JobApplication(**data.model_dump())
        return await self.repo.create(session, job_application)
  
    async def list_applications(
            self,
            session: AsyncSession,
    ) -> list[JobApplication]:
        return await self.repo.list_with_offer(session)

    async def update_application_by_id(
        self,
        session: AsyncSession,
        job_application_id: int,
        data: JobApplicationUpdate,
    ) -> JobApplication:
        job_application = await self.repo.get_by_id_with_offer(
             session, job_application_id)
        if not job_application:
            raise ValueError("Job application not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(job_application, field, value)

        await session.commit()
        await session.refresh(job_application)
        return job_application
    
def get_job_application_service() -> JobApplicationService:
        return JobApplicationService()
