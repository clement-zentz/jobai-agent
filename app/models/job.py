# SPDX-License-Identifier: AGPL-3.0-or-later
# app/models/job.py
from datetime import datetime, timezone
from typing import ClassVar, Optional

from sqlmodel import Field, SQLModel, DateTime, Column


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
    easy_apply: Optional[bool] = Field(default=None)
    active_hiring: Optional[bool] = Field(default=None)
    posted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

    date_scraped: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )

    source_email_id: Optional[str] = Field(default=None, nullable=True)
