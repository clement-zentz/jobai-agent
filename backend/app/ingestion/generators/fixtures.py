# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/generators/fixtures.py

from app.ingestion.extraction.email.email_alert_fetcher import (
    EmailAlertFetcher,
    FetchedEmail,
)
from app.ingestion.extraction.email.parser_base import EmailParser
from app.ingestion.fixtures.writer import create_fixture, remove_all_fixtures

PLATFORMS: dict[str, str] = {
    "indeed": "alert@indeed.com",
    "linkedin": "jobalerts-noreply@linkedin.com",
}


class FixtureGenerator:
    def __init__(
        self,
        fetcher: EmailAlertFetcher,
        parsers: dict[str, EmailParser],
        max_per_platform: int = 3,
    ):
        self.fetcher: EmailAlertFetcher = fetcher
        self.parsers = parsers
        self.max_per_platform = max_per_platform

    def generate(self, days_back: int = 7):
        remove_all_fixtures()

        for platform, sender in PLATFORMS.items():
            emails: list[FetchedEmail] = self.fetcher.fetch_recent(
                sender_filter=sender,
                days_back=days_back,
            )

            for email in emails[: self.max_per_platform]:
                parser = self.parsers[platform]
                jobs = parser.parse(email.html, email.msg_dt)

                create_fixture(
                    platform=platform,
                    html=email.html,
                    headers=email.headers,
                    jobs=jobs,
                    uid=email.uid,
                    msg_date=email.msg_dt,
                )
