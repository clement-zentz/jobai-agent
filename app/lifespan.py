# app/lifespan.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (optional)
    await close_db()