# SPDX-License-Identifier: AGPL-3.0-or-later
# app/utils/clean_fixture.py
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone, date

from app.core.config import get_settings
from .html_cleaner import clean_raw_fixture
from .headers_cleaner import clean_headers, build_name_pattern, build_email_pattern
from .naming import format_fixture_date

settings = get_settings()


def create_fixture(
    platform: str, 
    html: str, 
    headers: dict,
    jobs: list[dict],
    uid: int,
    msg_date: datetime | None = None,
):
    """
    Generate fixture with extracted email:
    - brut fixture for tests
    - net fixture for human reader
    """
    if not settings.debug:
        return # no fixture generation in production
    
    name_re = build_name_pattern()
    email_re = build_email_pattern()

    msg_date = msg_date or datetime.now(timezone.utc)
    date_str = format_fixture_date(msg_date)

    # Raw email fixture
    fixt_dir = Path(settings.fixture_dir) / platform / f"{date_str}_{uid}"
    fixt_dir.mkdir(parents=True, exist_ok=True)

    (fixt_dir / f"raw_{uid}.html").write_text(
        html, encoding="utf-8")
    (fixt_dir / f"clean_{uid}.html").write_text(
        clean_raw_fixture(html, name_re, email_re), encoding="utf-8")

    (fixt_dir / f"raw_headers_{uid}.json").write_text(
        json.dumps(headers, indent=2))
    (fixt_dir / f"net_headers_{uid}.json").write_text(
        json.dumps(clean_headers(headers), indent=2))
    
    def _json_safe(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        return obj

    if jobs is not None:
        (fixt_dir / f"response_{uid}.json").write_text(
            json.dumps(
                {
                    "platform": platform,
                    "count": len(jobs),
                    "jobs": jobs,
                },
                indent=2,
                ensure_ascii=False,
                default=_json_safe,
            ),
            encoding="utf-8",
        )

def remove_all_fixtures():
    """Remove all fixture files from fixture directory."""
    fixt_dir = Path(settings.fixture_dir)

    # Remove recursively all files
    # in fixture dir and subdirs
    for item in fixt_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
