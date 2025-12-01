# app/utils/clean_fixture.py
import re, secrets
from bs4 import BeautifulSoup, Comment
from datetime import datetime, timedelta, timezone
from pathlib import Path
from slugify import slugify
from .truncate_string import shorten_text
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

def generate_tests_fixtures(
    platform: str, 
    html: str, 
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

    slug_sbj = slugify(shorten_text(subject))
    ts = msg_date.astimezone(timezone.utc).strftime("%Y-%m-%d")

    # Raw email fixture
    raw_fixture_dir = Path(settings.raw_fixture_dir)
    raw_fixture_dir.mkdir(parents=True, exist_ok=True)

    raw_file_path = raw_fixture_dir / f"{platform}_raw_{slug_sbj}_{ts}.html"
    raw_file_path.write_text(html, encoding="utf-8")
    
    # Net email fixture
    net_fixture_dir = Path(settings.net_fixture_dir)
    net_fixture_dir.mkdir(parents=True, exist_ok=True)

    cleaned_html = clean_raw_fixture(html)

    net_file_path = net_fixture_dir / f"{platform}_net_{slug_sbj}_{ts}.html"
    net_file_path.write_text(cleaned_html, encoding="utf-8")

def remove_old_fixtures():
    raw_fixture_dir = Path(settings.raw_fixture_dir)
    net_dixture_dir = Path(settings.net_fixture_dir)

    # Pattern: *_2025-11-30.html
    pattern = r'_(\d{4}-\d{2}-\d{2})\.html$'
    cutoff_date = datetime.now().date() - timedelta(days=3)

    # Function to check file age
    def is_older_than_3_days(filename: str) -> bool:
        match = re.search(pattern, filename)
        if not match:
            return False # ignore files without date
        try:
            file_date = datetime.strptime(
                match.group(1), "%Y-%m-%d").date()
            return file_date < cutoff_date
        except ValueError:
            return False
    
    # Remove from raw fixtures
    for f in raw_fixture_dir.glob("*.html"):
        if f.is_file() and is_older_than_3_days(f.name):
            f.unlink()

    # Remove from net fixtures
    for f in net_dixture_dir.glob("*.html"):
        if f.is_file() and is_older_than_3_days(f.name):
            f.unlink()