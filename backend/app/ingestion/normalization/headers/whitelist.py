# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/normalization/headers/whitelist.py

def whitelist_headers(raw: dict[str, str]) -> dict[str, str]:
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

    return {k.lower(): v for k, v in raw.items() if k.lower() in ALLOWED_KEYS}
