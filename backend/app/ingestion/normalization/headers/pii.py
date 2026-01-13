# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/normalization/headers/pii.py

import re


def redact_headers(
    headers: dict[str, str],
    name_re: re.Pattern[str] | None,
    email_re: re.Pattern[str] | None,
) -> dict[str, str]:
    cleaned = {}
    for k, v in headers.items():
        if name_re:
            v = name_re.sub("[REDACTED]", v)
        if email_re:
            v = email_re.sub("[REDACTED]", v)
        if k == "message_id":
            v = "[REDACTED]"
        cleaned[k] = v
    return cleaned
