# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/fixtures/naming.py

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from dateutil import parser as dateutil_parser


@staticmethod
def parse_msg_date(msg):
    # parse Date header to datetime for fixture naming
    header_date = msg.get("Date")
    if not header_date:
        return None

    # Try strict RFC parser first
    try:
        dt = parsedate_to_datetime(header_date)
        if dt is not None:
            return dt
    except Exception:
        pass

    try:
        dt = dateutil_parser.parse(header_date, fuzzy=True)
        return dt
    except Exception:
        return None


def format_fixture_date(dt: datetime):
    dt = dt.astimezone(UTC)
    return dt.strftime("%Y-%m-%d")
