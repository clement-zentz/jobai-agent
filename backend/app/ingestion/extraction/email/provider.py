# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/extraction/email/provider.py

from dataclasses import dataclass


@dataclass
class EmailProvider:
    host: str
    port: int = 993


# Optional alias fallback for domains using same IMAP host
FALLBACK_ALIASES = {
    "yahoo.co.uk": "yahoo.com",
    "yahoo.ca": "yahoo.com",
}

PROVIDERS = {
    # Google
    "gmail.com": EmailProvider("imap.gmail.com"),
    "googlemail.com": EmailProvider("imap.gmail.com"),
    # Microsoft (Outlook / Hotmail / Live)
    "outlook.com": EmailProvider("outlook.office365.com"),
    "hotmail.com": EmailProvider("outlook.office365.com"),
    "live.com": EmailProvider("outlook.office365.com"),
    "msn.com": EmailProvider("outlook.office365.com"),
    # Yahoo
    "yahoo.com": EmailProvider("imap.mail.yahoo.com"),
    "yahoo.fr": EmailProvider("imap.mail.yahoo.com"),
    # Apple (iCloud / Me / Mac)
    "icloud.com": EmailProvider("imap.mail.me.com"),
    "me.com": EmailProvider("imap.mail.me.com"),
    "mac.com": EmailProvider("imap.mail.me.com"),
}


def detect_provider(email_address: str) -> EmailProvider:
    if "@" not in email_address:
        raise ValueError(f"Invalid email address: {email_address}")

    domain = email_address.split("@")[-1].lower().strip()

    # Normalize known aliases
    domain = FALLBACK_ALIASES.get(domain, domain)

    # Return known provider or a generic fallback
    return PROVIDERS.get(domain, EmailProvider(f"imap.{domain}"))
