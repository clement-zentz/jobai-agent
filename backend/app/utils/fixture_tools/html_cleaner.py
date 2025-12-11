# backend/app/utils/html_cleaner.py

import re
from bs4 import BeautifulSoup, Comment
from app.core.config import get_settings

settings = get_settings()


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

def clean_raw_fixture(html: str, name_re=None, email_re=None) -> str:
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
    if name_re:
        # Remove from text nodes
        for text in soup.find_all(string=name_re):
            text.replace_with(name_re.sub("[REDACTED]", text))

        # Remove from alt attributes
        for img in soup.find_all("img"):
            if img.get("alt"):
                img["alt"] = name_re.sub("[REDACTED]", str(img["alt"]))

        # Remove from URLs
        for a in soup.find_all("a", href=True):
            cleaned = name_re.sub("[REDACTED]", str(a["href"]))
            a["href"] = cleaned

    if email_re:
        for text in soup.find_all(string=email_re):
            text.replace_with(email_re.sub("[REDACTED]", text))

    # --- 9. Pretty-print output
    return soup.prettify()