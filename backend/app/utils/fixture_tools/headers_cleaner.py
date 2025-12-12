# backend/app/utils/fixture_tools/headers_cleaner.py

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
    if not settings.user_email:
        return None
    
    raw_email = settings.user_email.strip()
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

def clean_headers(
        raw: dict[str, str],
        name_re: re.Pattern[str] | None,
        email_re: re.Pattern[str] | None,
) -> dict[str, str]:
    """
    Clean email metadata extracted from IMAP.
    Keeps only safe and relevant fields while removing:
    - personal data (emails, names)
    - server routing headers (Received, ARC, SPF, DKIM...)
    - tracking IDs
    - unsubscribe URLs (contain identifiers)
    """

    # 1. Whitelist of useful & safe headers
    ALLOWED_KEYS = {
        "from",
        "subject",
        "date",
        "message-id",
        "mime-version",
        "content-type",

        # Indeed-specific
        "preheader",
        "x-indeed-content-type",
        "x-indeed-client-app",
        "x-campaign-id",

        # Linkedin-specific
        "x-linkedin-class",
        "x-linkedin-template",
    }

    cleaned: dict[str, str] = {}

    for key, value in raw.items():
        k = key.lower().strip()

        # Skip anything not in the whitelist
        if k not in ALLOWED_KEYS:
            continue

        v = value or ""

        # Remove personal data
        if name_re:
            v = name_re.sub("", v)
        if email_re:
            v = email_re.sub("", v)
         
        # 3. Normalize content-type (remove boundaries)
        if k == "content-type":
            # Example: multipart/alternative; boundary="XYZ"
            v = v.split(";", 1)[0].strip()
        
        cleaned[k] = v

    return cleaned
