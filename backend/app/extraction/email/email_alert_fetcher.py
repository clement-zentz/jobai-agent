# SPDX-License-Identifier: AGPL-3.0-or-later
# backend/app/extraction/email/email_alert_fetcher.py

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from dataclasses import dataclass
from .imap_client import IMAPClient
from .provider import detect_provider

@dataclass
class FetchedEmail:
    uid: str
    sender: str
    subject: str
    msg_dt: datetime
    html: str
    headers: dict[str, str]

class EmailAlertFetcher:

    def __init__(self, email_address: str, password: str, folder: str = "INBOX"):
        provider = detect_provider(email_address)
        self.client = IMAPClient(
            host=provider.host,
            username=email_address,
            password=password,
            port=provider.port,
        )

        self.folder = folder

    def fetch_recent(self, days_back: int) -> list[FetchedEmail]:
        self.client.connect()
        self.client.select_folder(self.folder)

        since_str = self._since_query(days_back)
        uids = self.client.search("SINCE", since_str)

        emails: list[FetchedEmail] = []
        for uid in uids:
            msg = self.client.fetch_email(uid)
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