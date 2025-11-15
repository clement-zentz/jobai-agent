# SPDX-License-Identifier: AGPL-3.0-or-later
# app/api/jobs.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.models.job import JobOffer

router = APIRouter(prefix="/jobs", tags=["jobs"])


# 🟢 CREATE
@router.post("/", response_model=JobOffer, status_code=status.HTTP_201_CREATED)
async def create_job(job: JobOffer, session: AsyncSession = Depends(get_session)):
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


# 🔵 READ ALL
@router.get("/", response_model=List[JobOffer])
async def list_jobs(session: AsyncSession = Depends(get_session)):
    results = await session.execute(select(JobOffer))
    jobs = results.scalars().all()
    return jobs


# 🟣 READ ONE
@router.get("/{job_id}")
async def get_job(job_id: int, session: AsyncSession = Depends(get_session)):
    job = await session.get(JobOffer, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# 🟠 UPDATE
@router.put("/{job_id}")
async def update_job(
    job_id: int, updated_job: JobOffer, session: AsyncSession = Depends(get_session)
):
    db_job = await session.get(JobOffer, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    for key, value in updated_job.model_dump(exclude_unset=True).items():
        setattr(db_job, key, value)

    session.add(db_job)
    await session.commit()
    await session.refresh(db_job)
    return db_job


# 🔴 DELETE
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int, session: AsyncSession = Depends(get_session)):
    job = await session.get(JobOffer, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await session.delete(job)
    await session.commit()
    return None
