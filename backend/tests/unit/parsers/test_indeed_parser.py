# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/tests/unit/parsers/test_indeed_parser.py

import json
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

from app.ingestion.extraction.email.parsers.indeed import IndeedParser

# --- Fixtures paths ---
ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURES_DIR = ROOT_DIR / "email_fixtures" / "indeed"
FIXTURE_ID = "2025-12-14_7128"
FIXTURE_DIR = FIXTURES_DIR / FIXTURE_ID

HTML_FILE = FIXTURE_DIR / "clean_7128.html"
HEADERS_FILE = FIXTURE_DIR / "net_headers_7128.json"
RESPONSE_FILE = FIXTURE_DIR / "response_7128.json"

print(f"✅ ROOT_DIR = {ROOT_DIR}")


# --- Tests ---
def test_indeed_matches_headers():
    headers = json.loads(HEADERS_FILE.read_text())

    parser = IndeedParser()

    assert (
        parser.matches(
            sender=headers["from"],
            subject=headers["subject"],
        )
        is True
    )


def test_indeed_parse_count():
    html = HTML_FILE.read_text()

    parser = IndeedParser()
    jobs = parser.parse(html, msg_dt=datetime.now())

    assert len(jobs) == 30


def test_indeed_job_fields():
    html = HTML_FILE.read_text()

    jobs = IndeedParser().parse(html, msg_dt=datetime.now())

    for job in jobs:
        assert job["platform"] == "indeed"
        assert job["title"]
        assert job["company"]
        assert job["location"]
        assert job["url"].startswith("http")


def normalize(job: dict) -> dict:
    job = job.copy()
    if isinstance(job["posted_at"], datetime):
        job["posted_at"] = job["posted_at"].isoformat()
    return job


def test_indeed_parse_against_expected():
    html = HTML_FILE.read_text()
    expected = json.loads(RESPONSE_FILE.read_text())
    headers = json.loads(HEADERS_FILE.read_text())

    msg_dt: datetime = parsedate_to_datetime(headers["date"])
    jobs = IndeedParser().parse(html, msg_dt=msg_dt)

    assert [normalize(j) for j in jobs] == expected["jobs"]
