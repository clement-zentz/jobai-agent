# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa
from app.api import job_applications, job_postings
from app.core.config import get_settings
from app.lifespan import lifespan

settings = get_settings()

app = FastAPI(title="JobAI Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(job_applications.router)
app.include_router(job_postings.router)
