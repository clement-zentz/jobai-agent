# app/main.py
from fastapi import FastAPI
from app.api import jobs

app = FastAPI(title="JobAI Agent")

# Include routes
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.get("/")
async def root():
    return {"message": "JobAI Agent is running"}
