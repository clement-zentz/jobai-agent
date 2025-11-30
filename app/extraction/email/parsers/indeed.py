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

        job_links = soup.select("td.pb-24 > a")
        jobs: list[dict] = []

        for a_tag in job_links:
            container = a_tag.select_one("table")
            if not container:
                continue

            rows = container.find_all("tr", recursive=False)
    
            # --- Title + URL ---
            title = None
            url = None

            if rows:
                title_tag = rows[0].select_one("h2 a")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    url = title_tag.get("href")

            # --- Company & Rating ---
            company = None
            rating = None

            if len(rows) >= 2:
                company_row = rows[1]
                company_cells = company_row.find_all("td")

                if company_cells:
                    company = company_cells[0].get_text(strip=True)

                    for cell in company_cells:
                        strong = cell.find("strong")
                        if strong:
                            try:
                                rating = float(strong.get_text(strip=True))
                            except ValueError:
                                pass

            # --- Location ---
            location = None
            if len(rows) >= 3:
                location_tag = rows[2]
                if location_tag:
                    location = location_tag.get_text(strip=True)

            # --- Salary (optional) ---
            salary = None
            salary_tag = container.select_one("table[bgcolor]")
            if salary_tag:
                salary = salary_tag.get_text(strip=True)

            # --- Simplified apply & Responsive employer (optional) ---
            # match <img> tag whose src attrs contains the substring : 'my_example_substring.ext'
            easy_apply = bool(container.select_one("img[src*='Plane_primary_whitebg.png']"))
            # Linkedin Actively recruiting <==> Indeed Responsive employer
            active_hiring = bool(container.select_one("img[src*='ResponsiveEmployer_whitebg.png']"))

            # --- Summary ---
            summary = None

            for tr in rows:
                txt = tr.get_text(" ", strip=True)
                if len(txt) > 40:
                    # skip salary tables
                    if "€" in txt and "par" in txt:
                        continue 
                    # skip posted_at lines
                    if "il y a" in txt.lower() or "publié" in txt.lower():
                        continue
                    summary = txt
                    break

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
                    "active_hiring": active_hiring,
                    "platform": "indeed",
                }
            )

        return jobs
