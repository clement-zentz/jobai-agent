# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/normalization/pii/patterns.py

import re

from app.core.config import get_settings

settings = get_settings()


def build_name_pattern() -> re.Pattern[str] | None:
    parts: list[str] = []

    if settings.user_first_name:
        parts.append(re.escape(settings.user_first_name.strip()))

    if settings.user_last_name:
        parts.append(re.escape(settings.user_last_name.strip()))

    if not parts:
        return None

    # Matches first and/or last name, case insentitive
    pattern = rf"\b({'|'.join(parts)})\b"
    return re.compile(pattern, flags=re.IGNORECASE)


def build_email_pattern() -> re.Pattern[str] | None:
    if not settings.email_address:
        return None

    raw_email = settings.email_address.strip()
    escaped_email = re.escape(raw_email)
    encoded_email = re.escape(raw_email.replace("@", "%40"))

    # Matches:
    # - youremail@example.com
    # - <youremail@example.com>
    # - youremail%40example.com
    pattern = rf"""
        (?:
            <{escaped_email}> |
            {escaped_email} |
            {encoded_email}
        )
    """

    return re.compile(pattern, flags=re.IGNORECASE | re.VERBOSE)
