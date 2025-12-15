# SPDX-License-Identifier: AGPL-3.0-or-later
# backend/app/extraction/email/job_extraction_service.py

from typing import List, Optional
from .email_alert_fetcher import FetchedEmail
from .parser_base import EmailParser
from .parsers.indeed import IndeedParser
from .parsers.linkedin import LinkedInParser
import logging

logger = logging.getLogger(__name__)


class JobExtractionService:
    """Fetch job alerts from an IMAP inbox and parse them into job dicts."""
    def __init__(self) -> None:
        self.parsers: List[EmailParser] = [
            LinkedInParser(),
            IndeedParser(),
            # WWTTJParser(),
        ]

    def extract_jobs(self, emails: list[FetchedEmail]) -> list[dict]:
        """Return parsed jobs from emails received within the last `days_back` days."""

        jobs: list[dict] = []
        for email in emails:

            parser = self._match_parser(email.sender, email.subject)

            if not parser:
                continue

            platform = parser.__class__.__name__.replace(
                "Parser", "").lower()

            parsed = parser.parse(email.html, email.msg_dt)

            for job in parsed:
                job["source"] = {
                    "uid": email.uid,
                    "platform": platform,
                    "subject": email.subject,
                    "sender": email.sender,
                }
            jobs.extend(parsed)

        return jobs

    def _match_parser(
            self, sender: str, subject: str) -> Optional[EmailParser]:
        for parser in self.parsers:
            if parser.matches(sender, subject):
                return parser
        return None

