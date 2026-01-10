# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/tests/api/test_job_applications_api.py

from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_application import JobApplication
from app.models.job_posting import JobPosting


@pytest.mark.asyncio
async def test_create_job_application_success(
    async_client: AsyncClient,
    test_session: AsyncSession,
):
    # Create job offer
    job_posting = JobPosting(
        title="Backend Engineer",
        company="Acme",
        platform="indeed",
        raw_url="https://indeed.com/viewjob?jk=123",
    )

    test_session.add(job_posting)
    await test_session.commit()
    await test_session.refresh(job_posting)

    # Create job application
    response = await async_client.post(
        "/job-applications",
        json={
            "job_posting_id": job_posting.id,
            "application_date": "2025-01-01",
            "notes": "First job application",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert isinstance(data["id"], int)
    assert data["notes"] == "First job application"
    assert data["status"] == "applied"
    assert "job_posting" not in data

    stmt = select(JobApplication).where(JobApplication.id == data["id"])
    result = await test_session.execute(stmt)
    job_application = result.scalar_one()

    assert job_application.job_posting_id == job_posting.id


@pytest.mark.asyncio
async def test_create_job_application_with_invalid_job_posting_id(
    async_client: AsyncClient,
    test_session: AsyncSession,
):
    response = await async_client.post(
        "/job-applications",
        json={
            "job_posting_id": 99999,
            "application_date": "2025-01-01",
            "notes": "First job application",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job Posting not found"


@pytest.mark.asyncio
async def test_list_job_applications(
    async_client: AsyncClient,
    test_session: AsyncSession,
):
    # Arrange
    job_posting = JobPosting(
        title="Data Engineer",
        company="DataCorp",
        location="London",
        platform="linkedin",
        raw_url="https://linkedin.com/jobs/123",
    )
    test_session.add(job_posting)
    await test_session.commit()
    await test_session.refresh(job_posting)

    job_application = JobApplication(
        job_posting_id=job_posting.id,
        application_date=date(2025, 1, 10),
        notes="Applied via website",
    )
    test_session.add(job_application)
    await test_session.commit()

    # Act
    response = await async_client.get("/job-applications")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["job_posting"]["company"] == "DataCorp"


@pytest.mark.asyncio
async def test_update_job_application_success(
    async_client: AsyncClient,
    test_session: AsyncSession,
):
    # Arrange
    job_posting = JobPosting(
        title="DevOps Engineer",
        company="InfraCo",
        location="Paris",
        platform="wttj",
        raw_url="https://wttj.com/jobs/123",
    )
    test_session.add(job_posting)
    await test_session.commit()
    await test_session.refresh(job_posting)

    job_application = JobApplication(
        job_posting_id=job_posting.id,
        application_date=date(2025, 1, 5),
        notes="Initial notes",
    )
    test_session.add(job_application)
    await test_session.commit()
    await test_session.refresh(job_application)

    # Act
    response = await async_client.patch(
        f"/job-applications/{job_application.id}",
        json={
            "notes": "Updated notes",
        },
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "Updated notes"


@pytest.mark.asyncio
async def test_update_job_application_not_found(
    async_client: AsyncClient,
):
    response = await async_client.patch(
        "/job-applications/99999",
        json={"notes": "Does not matter"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"
