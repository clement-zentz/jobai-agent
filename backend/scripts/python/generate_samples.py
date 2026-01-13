#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/scripts/python/generate_samples.py

from app.core.config import get_settings
from app.ingestion.extraction.email.email_alert_fetcher import EmailAlertFetcher
from app.ingestion.extraction.email.parser_base import EmailParser
from app.ingestion.extraction.email.parsers import indeed, linkedin
from app.ingestion.generators.samples import SampleGenerator

settings = get_settings()


def generate_recent_samples():
    parsers: dict[str, EmailParser] = {
        "indeed": indeed.IndeedParser(),
        "linkedin": linkedin.LinkedInParser(),
    }

    email_address = settings.email_address
    email_password = settings.email_password

    email_fetcher = EmailAlertFetcher(
        email_address=email_address, password=email_password
    )

    generator = SampleGenerator(fetcher=email_fetcher, parsers=parsers)

    generator.generate()


if __name__ == "__main__":
    generate_recent_samples()
