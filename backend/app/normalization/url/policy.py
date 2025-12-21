# backend/app/samples/constants.py

from typing import FrozenSet
from urllib.parse import urlparse

LINKEDIN_JOBSVIEW_REDACT_KEYS = frozenset({
    "trackingId", "refId", "lipi", "midToken", 
    "midSig", "trk", "trkEmail", "eid", "otpToken",
    "utm_source", "utm_medium", "utm_campaign",
    "utm_term", "utm_content",
})

INDEED_PAGEAD_REDACT_KEYS = frozenset({
    "tmtk", "xkcb", "camk", "alid", "sid", "tk"
})

INDEED_RK_REDACT_KEYS = frozenset ({
    "tk", "alid", "qd", "rd", "bb", "sid", "session", "user",
})

def get_job_url_policy(url: str) -> FrozenSet[str] | None:
    parsed = urlparse(url)
    path = parsed.path

    # --- Indeed ---
    if "indeed.com" in parsed.netloc:
        if "/rc/clk/" in path:
            return INDEED_RK_REDACT_KEYS
        if "/pagead/clk/" in path:
            return INDEED_PAGEAD_REDACT_KEYS
        return None

    if "linkedin.com" in parsed.netloc:
        if "/jobs/view/" in path:
            return LINKEDIN_JOBSVIEW_REDACT_KEYS
        return None
    
    return None