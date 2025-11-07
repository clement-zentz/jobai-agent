# app/api/jobs.py
from fastapi import APIRouter
from app.models.job import Job

router = APIRouter()

@router.post("/apply")
async def apply_job(job: Job):
    # replace with your app service here
    return {"status": "success", "job_title": job.title}