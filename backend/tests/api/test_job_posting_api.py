# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/tests/api/test_job_posting_api.py

# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/tests/api/test_job_postings_api.py

import pytest


@pytest.mark.asyncio
async def test_root_route(async_client):
    resp = await async_client.get("/")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}


# --- CREATE Job Offer ---
@pytest.mark.asyncio
async def test_create_job_posting(async_client):
    payload = {
        "title": "Python Developer",
        "company": "OpenAI",
        "location": "London",
        "raw_url": "https://example.com/job/python-dev",
        "platform": "test",
    }
    response = await async_client.post("/job-postings", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["company"] == payload["company"]


@pytest.mark.asyncio
async def test_create_job_posting_missing_required_fields(async_client):
    """Test creating a Job Posting without required fields"""
    payload = {"title": "Incomplete Job"}
    resp = await async_client.post("/job-postings", json=payload)
    assert resp.status_code == 422


# --- LIST Job Offers ---
@pytest.mark.asyncio
async def test_list_job_postings(async_client):
    resp = await async_client.get("/job-postings")
    assert resp.status_code == 200
    assert resp.json() == []
    job_postings = [
        {
            "title": "SRE",
            "company": "OpsLtd",
            "location": "London",
            "raw_url": "https://example.com/job/python-dev1",
            "platform": "test",
        },
        {
            "title": "Data Engineer",
            "company": "Pipeline Inc.",
            "location": "London",
            "raw_url": "https://example.com/job/python-dev2",
            "platform": "test",
        },
    ]
    # Create
    for j in job_postings:
        r = await async_client.post("/job-postings", json=j)
        assert r.status_code == 201
    # Get
    resp = await async_client.get("/job-postings")
    assert resp.status_code == 200
    data = resp.json()
    titles = [j["title"] for j in data]
    assert "SRE" in titles
    assert "Data Engineer" in titles


@pytest.mark.asyncio
async def test_list_job_postings_with_filters(async_client):
    """Test listing job offers with query filters"""
    jobs = [
        {
            "title": "Dev1",
            "company": "CompanyA",
            "location": "London",
            "raw_url": "https://a.com/1",
            "platform": "linkedin",
        },
        {
            "title": "Dev2",
            "company": "CompanyB",
            "location": "London",
            "raw_url": "https://b.com/2",
            "platform": "indeed",
        },
        {
            "title": "Dev3",
            "company": "CompanyC",
            "location": "Paris",
            "raw_url": "https://b.com/3",
            "platform": "wttj",
        },
        {
            "title": "Dev4",
            "company": "CompanyA",
            "location": "Dublin",
            "raw_url": "https://a.com/4",
            "platform": "linkedin",
        },
    ]

    # Create
    for job in jobs:
        resp = await async_client.post("/job-postings", json=job)
        assert resp.status_code == 201

    # Filter by platform
    resp = await async_client.get("/job-postings?platform=linkedin")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2

    # Filter by platform
    resp = await async_client.get("/job-postings?company=CompanyA")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


# --- GET Job Offer ---
@pytest.mark.asyncio
async def test_get_job_posting(async_client):
    # Create
    payload = {
        "title": "Backend developer",
        "company": "Nvidia",
        "location": "London",
        "raw_url": "https://example.com/job/python-dev",
        "platform": "test",
    }
    create_resp = await async_client.post("/job-postings", json=payload)
    assert create_resp.status_code == 201
    job_posting_id = create_resp.json()["id"]
    # Get
    resp = await async_client.get(f"/job-postings/{job_posting_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == job_posting_id
    assert data["title"] == payload["title"]
    assert data["company"] == payload["company"]


@pytest.mark.asyncio
async def test_get_nonexistent_job_posting(async_client):
    """Test retrieving a Job Posting that doesn't exist"""
    resp = await async_client.get("/job-postings/99999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Job Posting not found"}


# --- UPDATE Job Offer ---
@pytest.mark.asyncio
async def test_update_job_posting(async_client):
    # Create
    payload = {
        "title": "Data analyst",
        "company": "DataCorp",
        "location": "Paris",
        "raw_url": "https://example.com/job/python-dev",
        "platform": "test",
    }
    create_resp = await async_client.post("/job-postings", json=payload)
    assert create_resp.status_code == 201
    job_posting_id = create_resp.json()["id"]
    # Partial update
    update_payload = {"title": "Senior ML Engineer"}
    update_resp = await async_client.patch(
        f"/job-postings/{job_posting_id}", json=update_payload
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["id"] == job_posting_id
    assert updated["title"] == "Senior ML Engineer"
    # company remains unchanged
    assert updated["company"] == "DataCorp"


@pytest.mark.asyncio
async def test_update_nonexistent_job_posting(async_client):
    """Test updating a Job Posting that doesn't exist"""
    update_payload = {"title": "Updated Title"}
    resp = await async_client.patch("/job-postings/99999", json=update_payload)
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Job Posting not found"}
