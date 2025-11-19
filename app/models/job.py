# SPDX-License-Identifier: AGPL-3.0-or-later
# app/models/job.py
from datetime import datetime
from typing import ClassVar, Optional

from sqlmodel import Field, SQLModel


class JobOffer(SQLModel, table=True):
    __tablename__: ClassVar[str] = "joboffer"

    id: Optional[int] = Field(default=None, primary_key=True)

    title: str = Field(nullable=False)
    company: str = Field(nullable=False)
    rating: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    url: str = Field(nullable=False, index=True)
    platform: str = Field(nullable=False)

    date_scraped: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
    )

    # New field for email ingestion
    source_email_id: Optional[str] = Field(default=None, nullable=True)
