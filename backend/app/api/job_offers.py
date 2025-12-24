# SPDX-License-Identifier: AGPL-3.0-or-later
# app/api/jobs.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.models.job_offer import JobOffer
from app.schemas.job_offer import (
    JobOfferCreate, JobOfferRead, JobOfferUpdate)

router = APIRouter(prefix="/job-offers", tags=["Job Offers"])


# 🟢 CREATE
@router.post(
        "/", 
        response_model=JobOfferRead, 
        status_code=status.HTTP_201_CREATED,
)
async def create_job(
    job: JobOfferCreate, 
    session: AsyncSession = Depends(get_session)
):
    db_job = JobOffer(**job.model_dump())
    session.add(db_job)
    await session.commit()
    await session.refresh(db_job)
    return db_job


# 🔵 READ ALL
@router.get("/", response_model=List[JobOfferRead], status_code=status.HTTP_200_OK)
async def list_jobs(session: AsyncSession = Depends(get_session)):
    results = await session.execute(select(JobOffer))
    jobs = results.scalars().all()
    return jobs


# 🟣 READ ONE
@router.get(
        "/{job_id}", 
        response_model=JobOfferRead, 
        status_code=status.HTTP_200_OK,
)
async def get_job(
    job_id: int, 
    session: AsyncSession = Depends(get_session),
):
    job = await session.get(JobOffer, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# 🟠 UPDATE (partial - PATCH)
@router.patch(
        "/{job_id}", 
        response_model=JobOfferRead, 
        status_code=status.HTTP_200_OK
)
async def update_job(
    job_id: int, 
    updated_job: JobOfferUpdate, 
    session: AsyncSession = Depends(get_session)
):
    db_job = await session.get(JobOffer, job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # Apply only fields provided by the client
    update_data = updated_job.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)

    session.add(db_job)
    await session.commit()
    await session.refresh(db_job)
    return db_job


# 🔴 DELETE
@router.delete(
        "/{job_id}", 
        status_code=status.HTTP_204_NO_CONTENT
)
async def delete_job(
    job_id: int, 
    session: AsyncSession = Depends(get_session)
):
    job = await session.get(JobOffer, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    await session.delete(job)
    await session.commit()
    return None
