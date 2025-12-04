# SPDX-License-Identifier: AGPL-3.0-or-later
# tests/test.py

import pytest


@pytest.mark.asyncio
async def test_root_route(async_client):
    resp = await async_client.get("/")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_create_job(async_client):
    payload = {
        "title": "Python Developer", 
        "company": "OpenAI", 
        "location": "London",
        "url": "https://example.com/job/python-dev",
        "platform": "test"
    }
    response = await async_client.post("/jobs/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["company"] == payload["company"]


@pytest.mark.asyncio
async def test_list_jobs(async_client):
    resp = await async_client.get("/jobs/")
    assert resp.status_code == 200
    assert resp.json() == []
    jobs = [
        {
            "title": "SRE", 
            "company": "OpsLtd", 
            "location": "London",
            "url": "https://example.com/job/python-dev1",
            "platform": "test"
        },
        {
            "title": "Data Engineer",
            "company": "Pipeline Inc.",
            "location": "London",
            "url": "https://example.com/job/python-dev2",
            "platform": "test"
        }
    ]
    # Create
    for j in jobs:
        r = await async_client.post("/jobs/", json=j)
        assert r.status_code == 201
    # Get
    resp = await async_client.get("/jobs/")
    assert resp.status_code == 200
    data = resp.json()
    titles = [j["title"] for j in data]
    assert "SRE" in titles
    assert "Data Engineer" in titles


@pytest.mark.asyncio
async def test_get_job(async_client):
    # Create
    payload = {
        "title": "Backend developer", 
        "company": "Nvidia", 
        "location": "London",
        "url": "https://example.com/job/python-dev",
        "platform": "test"
    }
    create_resp = await async_client.post("/jobs/", json=payload)
    assert create_resp.status_code == 201
    job_id = create_resp.json()["id"]
    # Get
    resp = await async_client.get(f"/jobs/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == job_id
    assert data["title"] == payload["title"]
    assert data["company"] == payload["company"]


@pytest.mark.asyncio
async def test_update_job(async_client):
    # Create
    payload = {
        "title": "Data analyst", 
        "company": "DataCorp", 
        "location": "Paris",
        "url": "https://example.com/job/python-dev",
        "platform": "test"
    }
    create_resp = await async_client.post("/jobs/", json=payload)
    assert create_resp.status_code == 201
    job_id = create_resp.json()["id"]
    # Update only title
    update_payload = {"title": "Senior ML Engineer"}
    update_resp = await async_client.patch(f"/jobs/{job_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["id"] == job_id
    assert updated["title"] == "Senior ML Engineer"
    # company remains unchanged
    assert updated["company"] == "DataCorp"


@pytest.mark.asyncio
async def test_delete_job(async_client):
    # Create
    payload = {
        "title": "Frontend Dev", 
        "company": "WebCo", 
        "location": "Dublin",
        "url": "https://example.com/job/python-dev",
        "platform": "test"
    }
    create_resp = await async_client.post("/jobs/", json=payload)
    assert create_resp.status_code == 201
    job_id = create_resp.json()["id"]
    # Delete
    del_resp = await async_client.delete(f"/jobs/{job_id}")
    assert del_resp.status_code == 204
    assert del_resp.content in (b"", None)
    # Verify gone
    get_resp = await async_client.get(f"/jobs/{job_id}")
    assert get_resp.status_code == 404
    assert get_resp.json() == {"detail": "Job not found"}
