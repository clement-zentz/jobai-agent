# app/extraction/parsers/linkedin.py

from bs4 import BeautifulSoup
from email_extraction.parser_base import EmailParser


class LinkedInParser(EmailParser):

    def matches(self, sender: str, subject: str) -> bool:
        return "linkedin" in sender.lower() and "alert" in subject.lower()

    def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for card in soup.select("a.job-card-container"):
            title_elem = card.select_one(".job-card-title")
            company_elem = card.select_one(".job-card-company")
            
            if not title_elem or not company_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            company = company_elem.get_text(strip=True)
            url = card["href"]

            jobs.append({
                "title": title,
                "company": company,
                "location": "",
                "url": url,
                "platform": "linkedin",
            })

        return jobs


        