# SPDX-License-Identifier: AGPL-3.0-or-later
# app/utils/clean_fixture.py
import secrets, json, shutil, re
from bs4 import BeautifulSoup, Comment
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from dateutil import parser as dateutil_parser
from pathlib import Path
from app.core.config import get_settings


settings = get_settings()

def clean_raw_fixture(html: str) -> str:
    """
    Clean extracted html from emails into a human readable file.
    """
    soup = BeautifulSoup(html, "html.parser")

    # # --- 1. Remove all <style> blocks (media queries + hacks)
    for style in soup.find_all("style"):
        style.decompose()

    # --- 2. Remove Outlook conditionnal comments and all comments
    for element in soup(text=lambda t: isinstance(t, Comment)):
        # Remove comments like <!--[if mso]> ... <![endif]-->
        if "if" in element or "mso" in element or "endif" in element:
            element.extract()
        else:
            element.extract()

    # --- 3. Remove preview text (hidden divs)
    for div in soup.find_all("div"):
        style = str(div.get("style", "")) or ""
        if "display:none" in style or "max-height:0" in style:
            div.decompose()

    # --- 4. Remove tracking pixels
    for img in soup.find_all("img"):
        w = img.get("width", "")
        h = img.get("height", "")
        if w in ("1", "0", "1px") or h in ("1", "0", "1px"):
            img.decompose()

    # --- 5. Remove meta tags (useless for readability)
    for meta in soup.find_all("meta"):
        meta.decompose()

    # --- 6. Remove <script> tags (rare in emails)
    for script in soup.find_all("script"):
        script.decompose()

    # --- 7. Remove url trackers and tokens,
    # replace unnecessary urls too
    for a in soup.find_all("a", href=True):
        a["href"] = clean_job_url(str(a["href"]))

    # --- 8. Replace first name and last name with [REDACTED]
    name_pattern = build_name_pattern()
    if name_pattern:
        # Remove from text nodes
        for text in soup.find_all(string=name_pattern):
            text.replace_with(name_pattern.sub("[REDACTED]", text))

        # Remove from alt attributes
        for img in soup.find_all("img"):
            if img.get("alt"):
                img["alt"] = name_pattern.sub("[REDACTED]", str(img["alt"]))

        # Remove from URLs
        for a in soup.find_all("a", href=True):
            cleaned = name_pattern.sub("[REDACTED]", str(a["href"]))
            a["href"] = cleaned

    # --- 9. Pretty-print output
    return soup.prettify()

def clean_job_url(url: str) -> str:
    # --- Indeed ---
    if "indeed.com" in url:
        match = re.search(r"jk=([\w]+)", url)
        if match:
            return f"https://indeed.com/viewjob?jk={match.group(1)}"
        return "https://indeed.com"

    # --- LinkedIn ---
    if "linkedin.com" in url:
        match = re.search(r"/jobs/view/(\d+)", url)
        if match:
            return f"https://www.linkedin.com/jobs/view/{match.group(1)}"
        return "https://www.linkedin.com"

    return url

def build_name_pattern():
    parts = []

    if settings.user_first_name:
        parts.append(re.escape(settings.user_first_name.strip()))

    if settings.user_last_name:
        parts.append(re.escape(settings.user_last_name.strip()))

    if not parts:
        return None

    # Matches: Foo Bar, any case
    pattern = r"\b(" + "|".join(parts) + r")\b"
    return re.compile(pattern, flags=re.IGNORECASE)

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

def create_fixture(
    platform: str, 
    html: str, 
    uid: int,
    msg_date: datetime | None = None,
    subject: str | None = None,
):
    """
    Generate fixture with extracted email:
    - brut fixture for tests
    - net fixture for human reader
    """
    if not settings.debug:
        return # no fixture generation in production

    subject = subject if subject else secrets.token_hex(4)
    msg_date = msg_date if msg_date else datetime.now(timezone.utc)

    msg_date_s = msg_date.astimezone(timezone.utc).strftime("%Y-%m-%d")

    # Raw email fixture
    fixt_dir = Path(settings.fixture_dir) / platform / f"{msg_date_s}_{uid}"
    fixt_dir.mkdir(parents=True, exist_ok=True)

    (fixt_dir / f"raw_{uid}.html").write_text(
        html, encoding="utf-8")
    (fixt_dir / f"clean_{uid}.html").write_text(
        clean_raw_fixture(html), encoding="utf-8")
    
    meta = {
        "subject": subject,
        "received_at": msg_date.isoformat(),
        "platform": platform,
        "uid": uid,
    }

    (fixt_dir / f"meta_{uid}.json").write_text(
        json.dumps(meta, indent=2))
  


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
