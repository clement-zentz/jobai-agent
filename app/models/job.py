# app/models/job.py
from pydantic import BaseModel

class Job(BaseModel):
    title: str
    company: str
    description: str
    location: str
