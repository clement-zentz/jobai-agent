# SPDX-License-Identifier: AGPL-3.0-or-later
# app/main.py
from fastapi import FastAPI

from app.api import jobs
from app.lifespan import lifespan

app = FastAPI(title="JobAI Agent", lifespan=lifespan)

# Include routes
app.include_router(jobs.router)
