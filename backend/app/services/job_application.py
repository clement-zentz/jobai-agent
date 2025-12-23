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
        app = JobApplication(**data.model_dump())
        return await self.repo.create(session, app)
    
    async def list_applications(
            self,
            session: AsyncSession,
    ) -> list[JobApplication]:
        return await self.repo.list(session)
    
    async def update_application_by_id(
        self,
        session: AsyncSession,
        application_id: int,
        data: JobApplicationUpdate,
    ) -> JobApplication:
        app = await self.repo.get(session, application_id)
        if not app:
            raise ValueError("Application not found")
        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(app, field, value)

        await session.commit()
        await session.refresh(app)
        return app
    
def get_job_application_service() -> JobApplicationService:
        return JobApplicationService()
