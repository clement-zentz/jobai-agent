# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/services/job_application.py

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.job_application import JobApplication
from app.models.job_posting import JobPosting
from app.repositories.job_application import JobApplicationRepository
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
)


class JobApplicationService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        repo: JobApplicationRepository | None = None,
    ) -> None:
        self.session = session
        self.repo = repo if repo is not None else JobApplicationRepository(session)

    async def create_application(
        self,
        data: JobApplicationCreate,
    ) -> JobApplication:
        # ✅ Validate FK explicitly
        result = await self.session.execute(
            select(JobPosting.id).where(JobPosting.id == data.job_posting_id)
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job Posting not found",
            )

        job_application = JobApplication(**data.model_dump())
        return await self.repo.create(job_application)

    async def list_applications(
        self,
    ) -> list[JobApplication]:
        return await self.repo.list_with_job_posting()

    async def update_application_by_id(
        self,
        job_application_id: int,
        data: JobApplicationUpdate,
    ) -> JobApplication:
        job_application = await self.repo.get_by_id_with_job_posting(job_application_id)
        if not job_application:
            raise ValueError("Job application not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(job_application, field, value)

        await self.session.commit()
        return job_application


def get_job_application_service(
    session: AsyncSession = Depends(get_session),
) -> JobApplicationService:
    return JobApplicationService(session=session)
