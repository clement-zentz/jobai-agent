# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/extraction/email/email_alert_fetcher.py

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime

from .imap_client import IMAPClient
from .provider import detect_provider


@dataclass
class FetchedEmail:
    """
    Container for parsed email data.

    Attributes:
        uid: Unique email identifier from IMAP server
        sender: Email sender address
        subject: Email subject line
        msg_dt: Email datetime
        html: HTML content of the email body
        headers: Dictionary of email headers
    """

    uid: int
    sender: str
    subject: str
    msg_dt: datetime
    html: str
    headers: dict[str, str]


class EmailAlertFetcher:
    """
    Fetches and parses recent emails from an IMAP mailbox.

    Connects to an IMAP server, retrieves emails from a specified folder,
    and extracts relevant information including HTML content and headers.
    """

    def __init__(self, email_address: str, password: str, folder: str = "INBOX"):
        """
        Initialize the email fetcher with IMAP credentials.

        Args:
            email_address: Email address for authentication
            password: Email account password or app-specific password
            folder: IMAP folder name to fetch from (default: "INBOX")
        """
        provider = detect_provider(email_address)
        self.client = IMAPClient(
            host=provider.host,
            username=email_address,
            password=password,
            port=provider.port,
        )
        self.folder = folder

    def fetch_recent(
        self, days_back: int = 1, sender_filter: str | None = None
    ) -> list[FetchedEmail]:
        """
        Fetch emails from the last N days.

        Args:
            days_back: Number of days to look back for emails

        Returns:
            List of FetchedEmail objects containing parsed email data
        """
        self.client.connect()
        self.client.select_folder(self.folder)

        # Build IMAP search criteria (filter emails)
        since_str = self._since_query(days_back)
        criteria = ["SINCE", since_str]
        if sender_filter:
            criteria += ["FROM", sender_filter]
        uids = self.client.search(*criteria)

        emails: list[FetchedEmail] = []
        for uid_str in uids:
            msg = self.client.fetch_email(uid_str)
            if not msg:
                continue

            if not self._is_recent_enough(msg, days_back):
                continue

            html = IMAPClient.extract_html(msg)
            if not html:
                continue

            headers = IMAPClient.extract_headers(msg)
            if not headers:
                continue

            sender = IMAPClient.decode(msg["from"])
            subject = IMAPClient.decode(msg["subject"])
            msg_dt = parsedate_to_datetime(msg["date"])
            uid = int(uid_str)

            email = FetchedEmail(
                uid=uid,
                sender=sender,
                subject=subject,
                msg_dt=msg_dt,
                html=html,
                headers=headers,
            )

            emails.append(email)

        if self.client.conn is not None:
            self.client.conn.logout()

        return emails

    @staticmethod
    def _since_query(days_back: int) -> str:
        """
        Generate IMAP SINCE query date string.

        Args:
            days_back: Number of days to subtract from current date

        Returns:
            Date string in IMAP format (DD-Mon-YYYY)
        """
        ref_date = datetime.now() - timedelta(days=days_back)
        return ref_date.strftime("%d-%b-%Y")

    @staticmethod
    def _is_recent_enough(message, days_back: int) -> bool:
        """
        Check if email date falls within the lookback period.

        Args:
            message: Email message object
            days_back: Number of days to look back

        Returns:
            True if email is recent enough, False otherwise
        """
        header_date = message.get("Date")
        if not header_date:
            return True
        try:
            msg_dt = parsedate_to_datetime(header_date)
        except (TypeError, ValueError):
            return True

        if msg_dt.tzinfo is None:
            msg_dt = msg_dt.replace(tzinfo=UTC)

        cutoff = datetime.now(UTC) - timedelta(days=days_back)
        return msg_dt >= cutoff
