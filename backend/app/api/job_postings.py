# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/api/job_postings.py


from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.job_posting import JobPostingCreate, JobPostingRead, JobPostingUpdate
from app.services.job_posting import JobPostingService, get_job_posting_service

router = APIRouter(prefix="/job-postings", tags=["Job Postings"])


# 🟢 CREATE
@router.post(
    "",
    response_model=JobPostingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_posting(
    data: JobPostingCreate,
    service: JobPostingService = Depends(get_job_posting_service),
):
    """
    Create a Job Posting manually.
    """
    return await service.create_job_posting(data)


# 🔵 READ ALL
@router.get("", response_model=list[JobPostingRead], status_code=status.HTTP_200_OK)
async def list_job_postings(
    platform: str | None = None,
    company: str | None = None,
    has_application: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    service: JobPostingService = Depends(get_job_posting_service),
):
    """
    List Job Postings for dashboard and browsing.
    """
    return await service.list_job_postings(
        platform=platform,
        company=company,
        has_application=has_application,
        limit=limit,
        offset=offset,
    )


# 🟣 READ ONE
@router.get(
    "/{job_posting_id}",
    response_model=JobPostingRead,
    status_code=status.HTTP_200_OK,
)
async def get_job_posting(
    job_posting_id: int,
    service: JobPostingService = Depends(get_job_posting_service),
):
    """
    Get a single Job Posting by ID.
    """
    try:
        return await service.get_job_posting(job_posting_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job Posting not found",
        ) from None


# 🟠 UPDATE (partial - PATCH)
@router.patch(
    "/{job_posting_id}", response_model=JobPostingRead, status_code=status.HTTP_200_OK
)
async def update_job_posting(
    job_posting_id: int,
    data: JobPostingUpdate,
    service: JobPostingService = Depends(get_job_posting_service),
):
    """
    Correct or Enrich a Job Posting manually.
    """
    try:
        return await service.update_job_posting(job_posting_id, data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job Posting not found",
        ) from None
