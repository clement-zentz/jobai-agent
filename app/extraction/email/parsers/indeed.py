# SPDX-License-Identifier: AGPL-3.0-or-later
# app/data_extraction/email_extraction/parsers/indeed.py

import re, logging

from bs4 import BeautifulSoup
from app.extraction.email.parser_base import EmailParser

from datetime import datetime, timedelta, timezone


logger = logging.getLogger(__name__)

class IndeedParser(EmailParser):
    """
    Parser for Indeed "Job Alerts" emails
    """
    # subject is in lower case
    keywords = ["python", "backend", "data", "engineer", "developer", "ai"]

    def matches(self, sender: str, subject: str) -> bool:
        """
        Match Indeed job alert emails.

        Example:
        - sender like "Indeed <alert@indeed.com>"
        - subject like "Licorne Society recherche un/e Data Analyst..."
        """
        s_sender = sender.lower()
        s_subject = subject.lower()

        return (
            "indeed" in s_sender or
            "alert@indeed.com" in s_sender
        ) and any (kw in s_subject for kw in self.keywords)

    def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")

        job_blocks = soup.select("td.pb-24 > a")
        jobs: list[dict] = []

        for a_tag in job_blocks:
            container = a_tag.select_one("table")
            if not container:
                continue
    
            # --- Title ---
            title_tag = container.select_one("h2 a")
            title = title_tag.get_text(strip=True) \
                if title_tag else None
            url = title_tag["href"] if title_tag else None

            # --- Company & Rating ---
            company = None
            rating = None

            info_cells = container.select(
                "tr:nth-of-type(2) table tr td")

            if info_cells:
                company = info_cells[0].get_text(strip=True)
                if len(info_cells) > 1:
                    try:
                        rating = float(info_cells[1].get_text(strip=True))
                    except ValueError:
                        rating = None
                
            # --- Location ---
            location_tag = container.select_one("tr:nth-of-type(3) td")
            location = location_tag.get_text(strip=True) \
                if location_tag else None

            # --- Salary (optional) ---
            salary_tag = container.select_one("td > table[bgcolor]")
            salary = None
            if salary_tag:
                salary = salary_tag.get_text(strip=True)

            # --- Simplified apply (optional) ---
            easy_apply = bool(container.select_one("img[alt=' ']"))

            # --- Summary ---
            summary = None

            all_rows = container.select("tr")

            summary_tag = None
            for row in all_rows:  
                # Can have one or more cells  
                cells = row.find("td")
                if not cells:
                    continue

                # Description line always have no 
                # nested tables and contains long text
                if not cells.find("tables") and \
                    len(cells.get_text(strip=True)) > 40:
                    summary_tag = cells
                break

            summary = summary_tag.get_text(strip=True) \
                if summary_tag else None

            # --- Date posted ---
            posted_at = None

            posted_at_tag = container.select_one("td[style*='font-size:12px']")

            if posted_at_tag:
                posted_at_text = posted_at_tag.get_text("", strip=True)
                if posted_at_text:

                    # Normalize non-breaking spaces and unicode apostrophes
                    normalized = (
                        posted_at_text
                        .replace("\u00A0", " ") # NBSP --> normal space
                        .replace("’", "'") # curly apostrophe --> straight
                        .lower()
                    )

                    if "publié à l'instant" in normalized:
                        posted_at = datetime.now(timezone.utc)

                    else:
                        numbers = re.findall(r'\d+', normalized)
                        if numbers:
                            days_ago_int = int(numbers[0])
                            # today - days_ago = days_back
                            today, days_ago = datetime.now(timezone.utc), timedelta(days=days_ago_int)
                            posted_at = today - days_ago
                        else:
                            logger.warning(
                                "[IndeedParser] Could not parse posted_at text: %r",
                                posted_at_text
                            )

            # --- Build job dict ---
            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": url,
                    "summary": summary,
                    "posted_at": posted_at,
                    "salary": salary,
                    "rating": rating,
                    "easy_apply": easy_apply,
                    "platform": "indeed",
                }
            )

        return jobs
