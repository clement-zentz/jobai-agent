# SPDX-License-Identifier: AGPL-3.0-or-later
# app/extraction/email_alert_parser.py

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from dateutil import parser as dateutil_parser
from typing import List, Optional

from .imap_client import IMAPClient
from .parser_base import EmailParser
from .parsers.indeed import IndeedParser
from .parsers.linkedin import LinkedInParser
from .provider import detect_provider

from app.utils.manage_fixture import (
    remove_old_fixtures,
    generate_tests_fixtures
)


import logging

logger = logging.getLogger(__name__)

class EmailExtractionService:
    """Fetch job alerts from an IMAP inbox and parse them into job dicts."""

    def __init__(self, email_address: str, password: str, folder: str = "INBOX"):
        provider = detect_provider(email_address)
        self.client = IMAPClient(
            host=provider.host,
            username=email_address,
            password=password,
            port=provider.port,
        )

        self.folder = folder
        self.parsers: List[EmailParser] = [
            LinkedInParser(),
            IndeedParser(),
            # WWTTJParser(),
        ]

    def fetch_recent_jobs(self, days_back: int = 1) -> list[dict]:
        """Return parsed jobs from emails received within the last `days_back` days."""
        self.client.connect()
        self.client.select_folder(self.folder)

        since_str = self._since_query(days_back)
        uids = self.client.search("SINCE", since_str)

        jobs: list[dict] = []
        for uid in uids:
            msg = self.client.fetch_email(uid)
            if not msg:
                continue

            sender = IMAPClient.decode(msg.get("From"))
            subject = IMAPClient.decode(msg.get("Subject"))

            parser = self._match_parser(sender, subject)

            if not parser:
                continue

            if not self._is_recent_enough(msg, days_back):
                continue

            html = IMAPClient.extract_html(msg)
            if not html:
                continue

            platform = parser.__class__.__name__.replace(
                "Parser", "").lower()

            # Generate raw and net fixtures
            msg_dt = self.parse_msg_date(msg)
            generate_tests_fixtures(
                platform=platform, 
                html=html, 
                msg_date=msg_dt,
                subject=subject,
            )

            parsed = parser.parse(html)

            for job in parsed:
                job.setdefault("platform", platform)
                job["source_uid"] = uid
                job["source_subject"] = subject
                job["source_sender"] = sender
            jobs.extend(parsed)

        if self.client.conn is not None:
            self.client.conn.logout()

        return jobs

    def _match_parser(
            self, sender: str, subject: str) -> Optional[EmailParser]:
        for parser in self.parsers:
            if parser.matches(sender, subject):
                return parser
        return None

    @staticmethod
    def _since_query(days_back: int) -> str:
        ref_date = datetime.now() - timedelta(days=days_back)
        return ref_date.strftime("%d-%b-%Y")

    @staticmethod
    def _is_recent_enough(message, days_back: int) -> bool:
        header_date = message.get("Date")
        if not header_date:
            return True
        try:
            msg_dt = parsedate_to_datetime(header_date)
        except (TypeError, ValueError):
            return True

        if msg_dt.tzinfo is None:
            msg_dt = msg_dt.replace(tzinfo=timezone.utc)

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        return msg_dt >= cutoff

    @staticmethod
    def parse_msg_date(msg):
        # parse Date header to datetime for fixture naming
        header_date = msg.get("Date")
        if not header_date:
            return None

        # Try strict RFC parser first
        try:
            dt = parsedate_to_datetime(header_date)
            if dt is not None:
                return dt
        except Exception:
            pass

        try:
            dt = dateutil_parser.parse(header_date, fuzzy=True)
            return dt
        except Exception:
            return None

    def remove_old_alert_email(self, days_back: int = 3):
        """Remove alert emails and fixtures older than days_back"""

        self.client.connect()
        self.client.select_folder(self.folder)

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        remove_old_fixtures()

        uids_indeed = self.client.search('FROM', '"alert@indeed.com"')
        uids_linkedin = self.client.search('FROM', '"jobalerts-noreply@linkedin.com"')

        all_uids = list(set(uids_indeed + uids_linkedin))

        if not all_uids:
            logger.info("No job alerts found.")
            return 0
        
        uid_set = ",".join(all_uids)

        header_blocks = self.client.fetch_headers_bulk(uid_set)

        deleted_count = 0
        uids_to_delete = []

        for uid, msg in header_blocks:
            sender = IMAPClient.decode(msg.get("From"))
            subject = IMAPClient.decode(msg.get("Subject"))

            sender_l = sender.lower()

            is_linkedin = "jobalerts-noreply@linkedin.com" in sender_l
            is_indeed = "alert@indeed.com" in sender_l

            # Skip email that are not job alerts
            if not (is_linkedin or is_indeed):
                continue

            msg_date = self.parse_msg_date(msg)
            if not msg_date:
                continue # cannot delete an email without a valid date

            if msg_date.tzinfo is None:
                msg_date.replace(tzinfo=timezone.utc)

            # Remove alert email older than 3 days
            # ex: 2025-11-20 < 2025-11-25
            if msg_date < cutoff_date:
                uids_to_delete.append(uid)
                deleted_count += 1
                logger.info(
                    f"Deleted email: {sender} {subject}" 
                    f"(UID: {uid}) date:{msg_date}")

        # batch deletion
        self.client.delete_emails_batch(uids_to_delete)

        if self.client.conn is not None:
            self.client.conn.logout()

        return deleted_count