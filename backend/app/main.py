# SPDX-License-Identifier: AGPL-3.0-or-later
# app/main.py
from fastapi import FastAPI

from app.api import jobs, routes
from app.lifespan import lifespan
import app.models # noqa

app = FastAPI(title="JobAI Agent", lifespan=lifespan)

# Include routes
app.include_router(jobs.router)
app.include_router(routes.router)
