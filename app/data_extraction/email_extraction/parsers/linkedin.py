# SPDX-License-Identifier: AGPL-3.0-or-later
# app/extraction/parsers/linkedin.py

from bs4 import BeautifulSoup
from email_extraction.parser_base import EmailParser


class LinkedInParser(EmailParser):

    def matches(self, sender: str, subject: str) -> bool:
        return "linkedin" in sender.lower() and "alert" in subject.lower()

    def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # 1. Find all job title links on reliable inline styles
        title_links = soup.find_all(
            "a",
            style=lambda s: s is not None
            and "font-size: 16px" in s
            and "line-height: 1.25" in s,
        )

        for title_a in title_links:
            title = title_a.get_text(strip=True)
            url = title_a.get("href")

        # 2. Company + location are in the next <p> sibling
        company = ""
        location = ""

        # Move to the next p tag after title_a
        next_p = title_a.find_next("p")
        if next_p:
            text = next_p.get_text(" ", strip=True)
            # "Company name · Location"
            if "." in text:
                company, location = [x.strip() for x in text.split("·", 1)]
            else:
                company = text

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "platform": "linkedin",
            }
        )

        return jobs
