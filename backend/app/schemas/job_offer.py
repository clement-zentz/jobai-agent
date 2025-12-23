# SPDX-License-Identifier: AGPL-3.0-or-later
# app/schemas/job_offer.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class JobOfferBase(BaseModel):
    title: str
    company: str
    location: str | None = None
    raw_url: str
    canonical_url: str | None = None
    job_key: str | None = None
    platform: str
    rating: float | None = None
    salary: str | None = None
    summary:str | None = None
    description: str | None = None
    easy_apply: bool | None = None
    active_hiring: bool | None = None
    posted_at: datetime | None = None
    source_email_id: str | None = None

class JobOfferCreate(JobOfferBase):
    pass

class JobOfferUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    rating: float | None = None
    salary: str | None = None
    location: str | None = None
    summary: str | None = None
    description: str | None = None
    raw_url: str | None = None
    canonical_url: str | None = None
    job_key: str | None = None
    platform: str | None = None
    easy_apply: bool | None = None
    active_hiring: bool | None = None
    posted_at: datetime | None = None
    source_email_id: str | None = None

class JobOfferRead(JobOfferBase):
    id: int
    date_scraped: datetime

    model_config = ConfigDict(from_attributes=True)

class JobOfferSummary(BaseModel):
    id: int
    title: str
    company: str
    location: str
    platform: str

    model_config = ConfigDict(from_attributes=True)
