# SPDX-License-Identifier: AGPL-3.0-or-later
# backend/app/api/job_offers.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.job_offer import (
    JobOfferCreate, 
    JobOfferRead, 
    JobOfferUpdate
)
from app.services.job_offer import JobOfferService, get_job_offer_service

router = APIRouter(prefix="/job-offers", tags=["Job Offers"])


# 🟢 CREATE
@router.post(
    "/",
    response_model=JobOfferRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_offer(
    data: JobOfferCreate,
    service: JobOfferService = Depends(get_job_offer_service) 
):
    """
    Create a job offer manually.
    """
    return await service.create_manual(data)


# 🔵 READ ALL
@router.get(
    "/",
    response_model=List[JobOfferRead],
    status_code=status.HTTP_200_OK
)
async def list_job_offers(
    platform: str | None = None,
    company: str | None = None,
    has_application: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    service: JobOfferService = Depends(get_job_offer_service),
):
    """
    List job offers for dashboard and browsing.
    """
    return await service.list_offers(
        platform=platform,
        company=company,
        has_application=has_application,
        limit=limit,
        offset=offset,
    )


# 🟣 READ ONE
@router.get(
    "/{job_offer_id}",
    response_model=JobOfferRead,
    status_code=status.HTTP_200_OK,
)
async def get_job_offer(
    job_offer_id: int,
    service: JobOfferService = Depends(get_job_offer_service),
):
    """
    Get a single job offer by ID.
    """
    try:
        return await service.get_offer(job_offer_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job offer not found",
        )


# 🟠 UPDATE (partial - PATCH)
@router.patch(
    "/{job_offer_id}",
    response_model=JobOfferRead,
    status_code=status.HTTP_200_OK
)
async def update_job_offer(
    job_offer_id: int,
    data: JobOfferUpdate,
    service: JobOfferService = Depends(get_job_offer_service)
):
    """
    Correct or Enrich a Job offer manually.
    """
    try:
        return await service.update_offer(job_offer_id, data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job offer not found",
        )
