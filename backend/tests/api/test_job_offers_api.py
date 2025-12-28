# SPDX-License-Identifier: AGPL-3.0-or-later
# backend/tests/api/test_job_offers_api.py

import pytest


@pytest.mark.asyncio
async def test_root_route(async_client):
    resp = await async_client.get("/")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}


# --- CREATE Job Offer ---
@pytest.mark.asyncio
async def test_create_job_offer(async_client):
    payload = {
        "title": "Python Developer",
        "company": "OpenAI",
        "location": "London",
        "raw_url": "https://example.com/job/python-dev",
        "platform": "test",
    }
    response = await async_client.post("/job-offers/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["company"] == payload["company"]


# --- LIST Job Offers ---
@pytest.mark.asyncio
async def test_list_job_offers(async_client):
    resp = await async_client.get("/job-offers/")
    assert resp.status_code == 200
    assert resp.json() == []
    job_offers = [
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
    for j in job_offers:
        r = await async_client.post("/job-offers/", json=j)
        assert r.status_code == 201
    # Get
    resp = await async_client.get("/job-offers/")
    assert resp.status_code == 200
    data = resp.json()
    titles = [j["title"] for j in data]
    assert "SRE" in titles
    assert "Data Engineer" in titles


# --- GET Job Offer ---
@pytest.mark.asyncio
async def test_get_job_offer(async_client):
    # Create
    payload = {
        "title": "Backend developer",
        "company": "Nvidia",
        "location": "London",
        "raw_url": "https://example.com/job/python-dev",
        "platform": "test",
    }
    create_resp = await async_client.post("/job-offers/", json=payload)
    assert create_resp.status_code == 201
    job_offer_id = create_resp.json()["id"]
    # Get
    resp = await async_client.get(f"/job-offers/{job_offer_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == job_offer_id
    assert data["title"] == payload["title"]
    assert data["company"] == payload["company"]


# --- UPDATE Job Offer ---
@pytest.mark.asyncio
async def test_update_job_offer(async_client):
    # Create
    payload = {
        "title": "Data analyst",
        "company": "DataCorp",
        "location": "Paris",
        "raw_url": "https://example.com/job/python-dev",
        "platform": "test",
    }
    create_resp = await async_client.post("/job-offers/", json=payload)
    assert create_resp.status_code == 201
    job_offer_id = create_resp.json()["id"]
    # Partial update
    update_payload = {"title": "Senior ML Engineer"}
    update_resp = await async_client.patch(
        f"/job-offers/{job_offer_id}", json=update_payload
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["id"] == job_offer_id
    assert updated["title"] == "Senior ML Engineer"
    # company remains unchanged
    assert updated["company"] == "DataCorp"
