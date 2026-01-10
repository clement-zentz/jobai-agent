# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/services/job_posting.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.job_posting import JobPosting
from app.repositories.job_posting import JobPostingRepository
from app.schemas.job_posting import JobPostingCreate, JobPostingUpdate


class JobPostingService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        repo: JobPostingRepository | None = None,
    ) -> None:
        self.session = session
        self.repo = repo if repo is not None else JobPostingRepository(session)

    async def create_job_posting(
        self,
        data: JobPostingCreate,
    ) -> JobPosting:
        """
        Create a Job Posting manually (user is the source of truth).
        """
        job_posting = JobPosting(**data.model_dump())
        await self.repo.add(job_posting)
        await self.session.commit()
        await self.session.refresh(job_posting)

        return job_posting

    async def create_from_email_ingestion(
        self,
        data: dict,
    ) -> JobPosting | None:
        platform = data.get("platform")
        job_key = data.get("job_key")
        raw_url = data.get("raw_url")
        uid = data.get("source", {}).get("uid")

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

        # 3. Create new job job_posting
        job_posting = JobPosting(
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
            source_email_id=str(uid) if uid is not None else None,
            posted_at=data.get("posted_at"),
            easy_apply=data.get("easy_apply"),
            active_hiring=data.get("active_hiring"),
        )

        await self.repo.add(job_posting)
        return job_posting

    async def get_job_posting(
        self,
        job_posting_id: int,
    ) -> JobPosting:
        job_posting = await self.repo.get_by_id(job_posting_id)
        if not job_posting:
            raise ValueError("Job Posting not found")
        return job_posting

    async def list_job_postings(
        self,
        *,
        platform: str | None = None,
        company: str | None = None,
        has_application: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JobPosting]:
        return await self.repo.list(
            platform=platform,
            company=company,
            has_application=has_application,
            limit=limit,
            offset=offset,
        )

    async def update_job_posting(
        self,
        job_posting_id: int,
        data: JobPostingUpdate,
    ) -> JobPosting:
        job_posting = await self.repo.get_by_id(job_posting_id)
        if not job_posting:
            raise ValueError("Job Posting not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(job_posting, field, value)

        await self.session.commit()
        await self.session.refresh(job_posting)
        return job_posting


def get_job_posting_service(
    session: AsyncSession = Depends(get_session),
) -> JobPostingService:
    return JobPostingService(session=session)
