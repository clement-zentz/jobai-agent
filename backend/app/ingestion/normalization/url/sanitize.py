# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/normalization/url/sanitize.py

# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/normalization/url/sanitize.py

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from app.ingestion.normalization.url.policy import get_job_url_policy


def normalize_job_url(raw_url: str) -> tuple[str, str] | None:
    """
    Normalize a raw job posting URL from supported platforms.

    This function extracts a unique job identifier and constructs a canonical URL
    for job postings from Indeed and LinkedIn. If the URL does not match a supported
    pattern, None is returned.

    Args:
        raw_url: The raw URL string to normalize.

    Returns:
        A tuple (job_key, canonical_url) if the URL matches a supported platform,
        where:
            - job_key: The unique job identifier extracted from the URL.
            - canonical_url: The normalized, canonical URL for the job posting.
        Returns None if the URL does not match a supported pattern.
    """
    # --- Indeed ---
    if "indeed.com" in raw_url:
        match = re.search(r"jk=([\w]+)", raw_url)
        if match:
            job_key = match.group(1)
            canonical_url = f"https://indeed.com/viewjob?jk={match.group(1)}"
            return job_key, canonical_url

    # --- LinkedIn ---
    if "linkedin.com" in raw_url:
        match = re.search(r"/jobs/view/(\d+)", raw_url)
        if match:
            job_key = match.group(1)
            canonical_url = f"https://www.linkedin.com/jobs/view/{match.group(1)}"
            return job_key, canonical_url

    return None


def sanitize_job_url(raw_url: str) -> str:
    redact_keys = get_job_url_policy(raw_url)
    if not redact_keys:
        return raw_url

    parsed = urlparse(raw_url)
    query_params = parse_qsl(parsed.query, keep_blank_values=True)

    redacted_params = [
        (key, "REDACTED") if key in redact_keys else (key, value)
        for key, value in query_params
    ]

    redacted_query = urlencode(redacted_params, doseq=True)

    return urlunparse(parsed._replace(query=redacted_query))
