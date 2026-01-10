# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/schemas/job_posting.py

# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/schemas/job_offer.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobPostingBase(BaseModel):
    title: str
    company: str
    location: str | None = None
    raw_url: str
    canonical_url: str | None = None
    job_key: str | None = None
    platform: str
    ingestion_source: str | None = "manual"
    rating: float | None = None
    salary: str | None = None
    summary: str | None = None
    description: str | None = None
    easy_apply: bool | None = None
    active_hiring: bool | None = None
    posted_at: datetime | None = None
    source_email_id: str | None = None


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingUpdate(BaseModel):
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
    ingestion_source: str | None = None
    easy_apply: bool | None = None
    active_hiring: bool | None = None
    posted_at: datetime | None = None
    source_email_id: str | None = None


class JobPostingRead(JobPostingBase):
    id: int
    date_scraped: datetime

    model_config = ConfigDict(from_attributes=True)


class JobPostingListItem(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    platform: str

    model_config = ConfigDict(from_attributes=True)


class JobPostingReadDetail(BaseModel):
    id: int
    title: str
    company: str
    location: str | None
    platform: str
    raw_url: str
    canonical_url: str
    salary: str | None
    summary: str | None
    description: str | None
    posted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
