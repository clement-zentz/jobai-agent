# backend/app/api/job_applications.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_session
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationRead,
    JobApplicationUpdate,
)
from app.services.job_application import JobApplicationService, get_job_application_service

router = APIRouter(prefix="/job-applications", tags=["Job Applications"])

@router.post(
        "/", 
        response_model=JobApplicationRead, 
        status_code=201)
async def create_job_application(
    data: JobApplicationCreate,
    session: AsyncSession = Depends(get_session),
    service: JobApplicationService = Depends(get_job_application_service),
):
    return await service.create_application(session, data)

@router.get("/", response_model=list[JobApplicationRead])
async def list_job_applications(
    session: AsyncSession = Depends(get_session),
    service: JobApplicationService = Depends(get_job_application_service),
):
    return await service.list_applications(session)

@router.patch(
        "/{application_id}", 
        response_model=JobApplicationRead, 
        status_code=status.HTTP_200_OK)
async def update_job_application(
    application_id: int,
    data: JobApplicationUpdate,
    session: AsyncSession = Depends(get_session),
    service: JobApplicationService = Depends(get_job_application_service),
):
    try:
        return await service.update_application_by_id(
            session, application_id, data
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Application not found")
