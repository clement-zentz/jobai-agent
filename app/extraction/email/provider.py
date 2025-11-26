# SPDX-License-Identifier: AGPL-3.0-or-later
# app/extraction/provider.py
from dataclasses import dataclass


@dataclass
class EmailProvider:
    host: str
    port: int = 993


PROVIDERS = {
    "gmail.com": EmailProvider("imap.gmail.com"),
    "googlemail.com": EmailProvider("imap.gmail.com"),
    "outlook.com": EmailProvider("imap-mail.outlook.com"),
    "hotmail.com": EmailProvider("imap-mail.outlook.com"),
    "live.com": EmailProvider("imap-mail.outlook.com"),
    "yahoo.com": EmailProvider("imap.mail.yahoo.com"),
    "yahoo.fr": EmailProvider("imap.mail.yahoo.com"),
    "icloud.com": EmailProvider("imap.mail.me.com"),
}


def detect_provider(email_address: str) -> EmailProvider:
    domain = email_address.split("@")[-1].lower()
    return PROVIDERS.get(domain, EmailProvider(f"imap.{domain}"))
