# SPDX-License-Identifier: AGPL-3.0-or-later
# app/extraction/parsers/linkedin.py
import re

from bs4 import BeautifulSoup
from app.data_extraction.email_extraction.parser_base import EmailParser


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
            "linkedin" in s_sender or 
            "jobalerts-noreply@linkedin.com" in s_sender
        ) and any (kw in s_subject for kw in self.keywords)

    def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[dict] = []


        job_cards = soup.find_all(
            "td",
            class_="pt-3",
            attrs={"data-test-id": "job-card"},
        )

        for card in job_cards:
            # --- 0. Main job URL ---
            job_link_tag = card.find(
                "a", 
                href=lambda h: h is not None 
                and "/job/view/" in h
            )

            if not job_link_tag:
                continue

            job_url = job_link_tag.get("href")

            # --- 1. Title ---
            title_a = card.find(
                "a", 
                class_=lambda c: c is not None 
                and "font-bold" in c.split()
            )

            #  No title, break
            if not title_a:
                continue

            title = title_a.get_text(strip=True)
            if not title:
                continue

            # --- 2. Company & Location ---
            company = ""
            location = ""

            company_loc_p = title_a.find_next(
                "p", 
                class_=lambda c: c is not None 
                and "text-system-gray-100" in c.split()
            )

            if company_loc_p:
                text = company_loc_p.get_text(" ", strip=True)
                # "Company · Location"
                if "·" in text:
                    company, location = [x.strip() for x in text.split("·", 1)]
                else:
                    company = text

            # --- 3. Easy apply / flags (optional) ---
            easy_apply = False

            easy_apply_p = card.find("p", text=re.compile("Candidature simplifiée"))

            if easy_apply_p:
                easy_apply = True

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": job_url,
                    "platform": "linkedin",
                    "easy_apply": easy_apply,
                }
            )

        return jobs
