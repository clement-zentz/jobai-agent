# backend/app/normalization/html/pii.py

import re

def redact_pii(
    soup,
    name_re: re.Pattern[str] | None,
    email_re: re.Pattern[str] | None,
) -> None:
    """Mutate soup in place"""
    # --- 8. Replace first name and last name with [REDACTED]
    if name_re:
        # Remove from text nodes
        for text in soup.find_all(string=name_re):
            text.replace_with(name_re.sub("[REDACTED]", text))

        # Remove from alt attributes
        for img in soup.find_all("img"):
            alt = img.get("alt")
            if alt and name_re.search(str(alt)):
                img["alt"] = name_re.sub("[REDACTED]", str(img["alt"]))
                # Redact src if alt contained personal info
                if img.get("src"):
                    img["src"] = "[REDACTED]"

        # Remove from URLs
        for a in soup.find_all("a", href=True):
            cleaned = name_re.sub("[REDACTED]", str(a["href"]))
            a["href"] = cleaned

    if email_re:
        for text in soup.find_all(string=email_re):
            text.replace_with(email_re.sub("[REDACTED]", text))

    JOB_URL_MARKERS = (
        "/rc/clk/",
        "/pagead/clk/",
        "/jobs/view/",
    )

    # --- Redact all non job urls ---
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not any(marker in href for marker in JOB_URL_MARKERS):
            a["href"] = "[REDACTED]"
