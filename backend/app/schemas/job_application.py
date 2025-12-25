# backend/app/schemas/job_application.py

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from app.models.job_application import ApplicationStatus
from .job_offer import JobOfferSummary

class JobApplicationBase(BaseModel):
    application_date: date
    notes: str | None = None

class JobApplicationCreate(JobApplicationBase):
    job_offer_id: int

class JobApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None

class JobApplicationRead(JobApplicationBase):
    id: int
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JobApplicationReadWithOffer(JobApplicationRead):
    job_offer: JobOfferSummary
