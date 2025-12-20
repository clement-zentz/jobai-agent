# SPDX-License-Identifier: AGPL-3.0-or-later
# backend/app/samples/writer.py

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone, date

from app.core.config import get_settings
from app.normalization.html.structural import strip_structure
from app.normalization.html.pii import redact_pii
from app.normalization.headers.pii import redact_headers
from app.normalization.headers.whitelist import whitelist_headers
from app.normalization.pii.patterns import build_name_pattern, build_email_pattern
from app.fixtures.naming import format_fixture_date

settings = get_settings()

def _json_safe(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    return obj

def serialize_jobs(jobs: list[dict], platform: str) -> str:
    return json.dumps(
        {
            "platform": platform,
            "count": len(jobs),
            "jobs": jobs,
        },
        indent=2,
        ensure_ascii=False,
        default=_json_safe,
    )

def create_sample(
    platform: str, 
    html: str, 
    headers: dict,
    jobs: list[dict],
    uid: int,
    msg_date: datetime | None = None,
):
    """
    Generate samples with extracted email:
    - body_raw.html, body_struct.html, body_sanitized.html
    - headers_raw.json, headers_sanitized.json
    - jobs_raw.json, jobs_sanitized.json
    """
    if not settings.debug:
        return # no fixture generation in production
    
    name_re = build_name_pattern()
    email_re = build_email_pattern()

    msg_date = msg_date or datetime.now(timezone.utc)
    date_str = format_fixture_date(msg_date)

    sample_dir = Path(settings.sample_dir) / platform / f"{date_str}_{uid}"
    sample_dir.mkdir(parents=True, exist_ok=True)

    # --- Body raw ---
    body_raw_path = sample_dir / "body_raw.html"
    body_raw_path.write_text(
        html, encoding="utf-8")

    # --- Body struct ---
    body_structured_soup = strip_structure(html)
    body_struct_path = sample_dir / "body_struct_.html"
    body_struct_path.write_text(
        body_structured_soup.prettify(), encoding="utf-8")

    # --- Body sanitized ---
    body_sanitized_soup = strip_structure(html)
    redact_pii(body_sanitized_soup, name_re, email_re)
    body_sanitized_path = sample_dir / "body_sanitized_.html"
    body_sanitized_path.write_text(
        body_sanitized_soup.prettify(), encoding="utf-8")

    # --- Headers raw ---
    headers_raw_path = sample_dir / "headers_raw.json"
    headers_raw_path.write_text(
        json.dumps(headers, indent=2))

    # --- Headers sanitized ---
    headers_sanitized = redact_headers(
        whitelist_headers(headers), name_re, email_re)
    headers_sanitized_path = sample_dir / "headers_sanitized.json"
    headers_sanitized_path.write_text(
        json.dumps(headers_sanitized, indent=2))
    
    # --- Jobs raw ---
    if jobs is not None:
        jobs_raw_path = sample_dir / "jobs_raw.json"
        jobs_raw_path.write_text(
            serialize_jobs(jobs, platform),
            encoding="utf-8",
        )

def remove_all_samples():
    """Remove all sample files from sample directory."""
    sample_dir = Path(settings.sample_dir)

    # Remove recursively all files
    # in sample dir and subdirs
    for item in sample_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
