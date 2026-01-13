# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/extraction/email/job_extraction_service.py

import logging

from .email_alert_fetcher import FetchedEmail
from .parser_base import EmailParser
from .parsers.indeed import IndeedParser
from .parsers.linkedin import LinkedInParser

logger = logging.getLogger(__name__)


class JobExtractionService:
    """
    Service for extracting job postings from email alerts.

    This service processes fetched emails by matching them with appropriate parsers
    based on sender and subject, then extracts job information from the email content.
    """

    def __init__(self) -> None:
        """Initialize the service with registered email parsers."""
        self.parsers: list[EmailParser] = [
            LinkedInParser(),
            IndeedParser(),
            # WWTTJParser(),
        ]

    def extract_jobs(self, emails: list[FetchedEmail]) -> list[dict]:
        """
        Parse job postings from a list of fetched emails.

        Args:
            emails: List of FetchedEmail objects to process

        Returns:
            List of job dictionaries, each containing job details and source metadata
        """
        jobs: list[dict] = []
        for email in emails:
            parser = self._match_parser(email.sender, email.subject)

            if not parser:
                continue

            platform = parser.__class__.__name__.replace("Parser", "").lower()

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

    def _match_parser(self, sender: str, subject: str) -> EmailParser | None:
        """
        Find the appropriate parser for an email based on sender and subject.

        Args:
            sender: Email sender address
            subject: Email subject line

        Returns:
            Matching EmailParser instance or None if no parser matches
        """
        for parser in self.parsers:
            if parser.matches(sender, subject):
                return parser
        return None
