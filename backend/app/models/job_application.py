# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/models/job_application.py

from datetime import UTC, date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    INTERVIEW = "interview"
    TECHNICAL_TEST = "technical_test"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobApplication(Base):
    __tablename__ = "job_application"

    id: Mapped[int] = mapped_column(primary_key=True)

    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("jobposting.id"),
        nullable=False,
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.APPLIED,
        nullable=False,
    )

    job_application_date: Mapped[date] = mapped_column(Date, nullable=False)

    notes: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    job_posting = relationship(
        "JobPosting",
        back_populates="job_applications",
        lazy="raise",
    )
