# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/tests/unit/services/test_job_application_service.py

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.job_application import JobApplication
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
)
from app.services.job_application import JobApplicationService


@pytest.fixture
def session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def repo():
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.list_with_job_posting = AsyncMock()
    repo.get_by_id_with_job_posting = AsyncMock()
    return repo


@pytest.fixture
def service(session, repo):
    return JobApplicationService(
        session=session,
        repo=repo,
    )


# --- create_application ---
@pytest.mark.asyncio
async def test_create_application_raises_if_job_posting_not_found(
    service: JobApplicationService,
    session,
):
    # Mock FK check: no Job Posting
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    data = JobApplicationCreate(
        job_posting_id=123,
        job_application_date=date(2025, 1, 1),
        notes="Test",
    )

    with pytest.raises(HTTPException) as exc:
        await service.create_application(data)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Job Posting not found"


@pytest.mark.asyncio
async def test_create_application_success(
    service: JobApplicationService,
    session,
    repo,
):
    # Mock FK check: job Posting exists
    result = MagicMock()
    result.scalar_one_or_none.return_value = 1
    session.execute.return_value = result

    job_application = JobApplication(
        job_posting_id=1,
        notes="Applied",
    )

    repo.create.return_value = job_application

    data = JobApplicationCreate(
        job_posting_id=1,
        job_application_date=date(2025, 1, 1),
        notes="Applied",
    )

    result = await service.create_application(data)

    assert result is job_application
    assert result.job_posting_id == 1
    assert result.notes == "Applied"
    repo.create.assert_awaited_once()


# --- list_applications ---
@pytest.mark.asyncio
async def test_list_applications_calls_repo(
    service: JobApplicationService,
    repo,
):
    expected = [JobApplication(id=1), JobApplication(id=2)]
    repo.list_with_job_posting.return_value = expected

    result = await service.list_applications()

    assert result == expected
    repo.list_with_job_posting.assert_awaited_once()


# --- update_application_by_id ---
@pytest.mark.asyncio
async def test_update_application_raises_if_not_found(
    service: JobApplicationService,
    repo,
):
    repo.get_by_id_with_job_posting.return_value = None

    data = JobApplicationUpdate(notes="Updated")

    with pytest.raises(ValueError, match="Job application not found"):
        await service.update_application_by_id(1, data)


@pytest.mark.asyncio
async def test_update_application_success(
    service: JobApplicationService,
    repo,
    session,
):
    job_application = JobApplication(
        job_posting_id=1,
        notes="Old notes",
    )

    repo.get_by_id_with_job_posting.return_value = job_application

    data = JobApplicationUpdate(
        notes="New notes",
    )

    result = await service.update_application_by_id(1, data)

    assert result is job_application
    assert job_application.notes == "New notes"

    session.commit.assert_awaited_once()
