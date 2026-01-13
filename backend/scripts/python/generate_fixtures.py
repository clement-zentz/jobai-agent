#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/scripts/python/generate_fixtures.py

import logging

from app.core.config import get_settings
from app.ingestion.extraction.email.email_alert_fetcher import EmailAlertFetcher
from app.ingestion.extraction.email.parser_base import EmailParser
from app.ingestion.extraction.email.parsers.indeed import IndeedParser
from app.ingestion.extraction.email.parsers.linkedin import LinkedInParser
from app.ingestion.generators.fixtures import FixtureGenerator

settings = get_settings()


logger = logging.getLogger(__name__)


def generate_recent_fixtures():
    parsers: dict[str, EmailParser] = {
        "indeed": IndeedParser(),
        "linkedin": LinkedInParser(),
    }

    email_address = settings.email_address
    email_password = settings.email_password

    email_fetcher = EmailAlertFetcher(
        email_address=email_address, password=email_password
    )

    generator = FixtureGenerator(fetcher=email_fetcher, parsers=parsers)

    generator.generate()


if __name__ == "__main__":
    generate_recent_fixtures()
