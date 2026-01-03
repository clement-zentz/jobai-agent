#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/scripts/python/ingest_emails.py
import asyncio

from app.core.config import get_settings
from app.core.database import async_session_local
from app.ingestion.email_ingestion import JobIngestionService

settings = get_settings()


async def main():
    async with async_session_local() as session:
        service = JobIngestionService(session)
        await service.ingest_from_email(
            email_address=settings.email_address,
            password=settings.email_password,
        )


if __name__ == "__main__":
    asyncio.run(main())
