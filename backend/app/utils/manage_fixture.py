# SPDX-License-Identifier: AGPL-3.0-or-later
# app/utils/clean_fixture.py
import secrets, json, shutil
from bs4 import BeautifulSoup, Comment
from datetime import datetime, timedelta, timezone
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

        # --- 7. Pretty-print output
        return soup.prettify()

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
