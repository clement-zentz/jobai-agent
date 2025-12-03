# SPDX-License-Identifier: AGPL-3.0-or-later
# app/extraction/imap_client.py
import email
import imaplib
import ssl
from email.header import decode_header
from email.message import Message
from typing import List, Optional

import logging

logger = logging.getLogger(__name__)

class IMAPClient:
    def __init__(self, host: str, username: str, password: str, port: int = 993):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.conn = None

    def connect(self):
        context = ssl.create_default_context()
        self.conn = imaplib.IMAP4_SSL(self.host, self.port, ssl_context=context)
        try:
            self.conn.login(self.username, self.password)
        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"IMAP login failed: {e}")

    def select_folder(self, folder="INBOX"):
        if self.conn is None:
            raise RuntimeError("Not connected. Call connect() first.")
        self.conn.select(folder)

    def search(self, *criteria: str) -> List[str]:
        if self.conn is None:
            raise RuntimeError("Not connected. Call connect() first.")
        status, data = self.conn.search(None, *criteria)
        if status != "OK" or not data or not data[0]:
            return []
        return data[0].decode().split()

    def fetch_email(self, uid: str) -> Optional[Message]:
        if self.conn is None:
            raise RuntimeError("IMAP connection not established")

        status, data = self.conn.fetch(uid, "(RFC822)")

        if status != "OK" or not data or data[0] is None:
            return None

        raw = data[0][1]
        if not isinstance(raw, bytes):
            return None
        return email.message_from_bytes(raw)

    def fetch_headers_bulk(self, uid_set: str) -> list[tuple[str, Message]]:
        """
        Fetch headers (From/Subject/Date) for a specific UID set in one IMAP command.
        Example uid_set: "100,105,110"
        Returns list of (uid, Message)
        """
        if self.conn is None:
            raise RuntimeError("IMAP connection not established")

        # Fetch only From, Subject and Date (much faster)
        status, data = self.conn.fetch(
            uid_set,
            "(UID BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])"
        )

        if status != "OK" or not data:
            return []

        results = []

        for item in data:
            if not isinstance(item, tuple):
                continue

            meta = item[0].decode(errors="ignore")
            body = item[1]

            # Extract UID from metadata: e.g. '1234 (UID 5678 BODY[...])'
            parts = meta.split()
            uid = None
            for i, part in enumerate(parts):
                if part == "UID" and i + 1 < len(parts):
                    uid = parts[i + 1]
                    break

            if not uid or not uid.isdigit():
                continue

            msg = email.message_from_bytes(body)
            results.append((uid, msg))

        return results
       
    def delete_email(self, uid: str):
        if self.conn is None:
            raise RuntimeError("IMAP connection not established")
        # Mark email as deleted
        self.conn.store(uid, '+FLAGS', r'(\Deleted)')
        # Permanently remove emails marked as deleted
        self.conn.expunge()

    def delete_emails_batch(self, uids: list[str]):
        if self.conn is None:
            raise RuntimeError("IMAP connection not established")

        if not uids:
            return

        uid_set = ",".join(uids)
        self.conn.store(uid_set, "+FLAGS", r"(\Deleted)")
        self.conn.expunge()

    @staticmethod
    def decode(value: Optional[str]) -> str:
        if not value:
            return ""
        decoded, charset = decode_header(value)[0]
        if isinstance(decoded, bytes):
            # Fallback for problematic charsets
            try:
                if not charset or charset.lower() \
                in ["unknown-8bit", "x-unknown", "unknown"]:
                    charset = "utf-8"
                return decoded.decode(charset, errors="ignore")
            except LookupError:
                return decoded.decode("utf-8", errors="ignore")
        return decoded

    @staticmethod
    def extract_html(msg: Message) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        return payload.decode("utf-8", errors="ignore")
        else:
            if msg.get_content_type() == "text/html":
                payload = msg.get_payload(decode=True)
                if isinstance(payload, bytes):
                    return payload.decode("utf-8", errors="ignore")

        return ""
