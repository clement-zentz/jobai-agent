# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/repositories/job_application.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job_application import JobApplication


class JobApplicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        job_application: JobApplication,
    ) -> JobApplication:
        self.session.add(job_application)
        await self.session.commit()
        await self.session.refresh(job_application)
        return job_application

    async def get_by_id_with_job_posting(
        self,
        job_application_id: int,
    ) -> JobApplication | None:
        stmt = (
            select(JobApplication)
            .where(JobApplication.id == job_application_id)
            .options(selectinload(JobApplication.job_posting))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_with_job_posting(
        self,
    ) -> list[JobApplication]:
        stmt = select(JobApplication).options(selectinload(JobApplication.job_posting))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
