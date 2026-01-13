# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/app/ingestion/extraction/email/parsers/linkedin.py

import re
from datetime import datetime

from bs4 import BeautifulSoup

from app.ingestion.extraction.email.parser_base import EmailParser
from app.ingestion.normalization.url.sanitize import normalize_job_url


class LinkedInParser(EmailParser):
    """
    Parser for LinkedIn "Job Alert" digest emails
    """

    # subject is in lower case
    keywords = ["python", "backend", "data", "engineer", "developer", "ai"]

    def matches(self, sender: str, subject: str) -> bool:
        """
        Match Linkedin job alerts like:
        - sender: Alertes LinkedIn Jo. () <jobalerts-noreply@linkedin.com>
        - subject: often contains keyword + 'emplois' or similar.
        """
        s_sender = sender.lower()
        s_subject = subject.lower()

        return (
            "linkedin" in s_sender or "jobalerts-noreply@linkedin.com" in s_sender
        ) and any(kw in s_subject for kw in self.keywords)

    def parse(self, html: str, msg_dt: datetime | None = None) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[dict] = []

        job_cards = soup.find_all(
            "td",
            class_="pt-3",
            attrs={"data-test-id": "job-card"},
        )

        for card in job_cards:
            # --- 1. Title and URL ---
            title_a = card.find(
                "a", class_=lambda c: c is not None and "font-bold" in c.split()
            )

            #  No title, break
            if not title_a:
                continue

            raw_url = title_a.get("href")
            if not raw_url:
                continue

            # --- Job Key and Canonical Url
            if raw_url:
                result = normalize_job_url(str(raw_url))
                if result:
                    job_key, canonical_url = result

            title = title_a.get_text(strip=True)
            if not title:
                continue

            # --- 2. Company & Location ---
            company = ""
            location = ""

            company_loc_p = title_a.find_next(
                "p",
                class_=lambda c: c is not None and "text-system-gray-100" in c.split(),
            )

            if company_loc_p:
                text = company_loc_p.get_text(" ", strip=True)
                # "Company · Location"
                if "·" in text:
                    company, location = [x.strip() for x in text.split("·", 1)]
                else:
                    company = text

            # --- 3. Active hiring (optional) ---
            active_hiring = None

            active_hiring_p = card.find(
                string=re.compile(r"(Recrutement actif|Actively recruiting)", re.I)
            )

            if active_hiring_p:
                active_hiring = True

            # --- 4. Easy apply / flags (optional) ---
            easy_apply = None

            easy_apply_p = card.find(
                string=re.compile(r"(Candidature simplifiée|Easy Apply)", re.I)
            )

            if easy_apply_p:
                easy_apply = True

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "raw_url": raw_url,
                    "job_key": job_key,
                    "canonical_url": canonical_url,
                    "platform": "linkedin",
                    "active_hiring": active_hiring,
                    "easy_apply": easy_apply,
                }
            )

        return jobs
