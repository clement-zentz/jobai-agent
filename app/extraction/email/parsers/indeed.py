# SPDX-License-Identifier: AGPL-3.0-or-later
# app/data_extraction/email_extraction/parsers/indeed.py

from bs4 import BeautifulSoup
from app.extraction.email.parser_base import EmailParser



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
        jobs: list[dict] = []

        offer_cells = soup.find_all(
            "td",
            style=lambda s: s is not None and "padding:0px 0px 32px" in s,
            class_=lambda c: bool(c and "pb-24" in c.split())
        )

        for cell_td in offer_cells:
            # ----- 0. Extract job URL -----
            root_a = cell_td.find("a", href=True)

            # TODO: add title_a href fallback
            if not root_a:
                continue 

            job_url = root_a.get("href")

            # ----- 1. Title -----
            title_a = cell_td.find("a", class_="strong-text-link")

            if not title_a:
                h2 = cell_td.find("h2")
                title_text_el = h2 if h2 else None
            else:
                title_text_el = title_a

            if not title_text_el:
                continue # cannot extract job without title

            title = title_text_el.get_text(strip=True)

            # ----- 2. Company & Rating -----
            company = ""
            rating: float | None = None

            title_tr = title_text_el.find_parent("tr")
            company_tr = title_tr.find_next_sibling("tr") if title_tr else None

            if company_tr:
                tds = company_tr.find_all("td")
                if tds:
                    # First <td> text is company
                    company = tds[0].get_text(" ", strip=True)

                # strong row can be rating
                strong = company_tr.find("strong")
                if strong:
                    raw_rating = strong.get_text(strip=True).replace(",", ".")
                    try:
                        rating = float(raw_rating)
                    except ValueError:
                        rating = None
                
            # ----- 3. Location
            location = ""
            location_tr = None

            if company_tr:
                location_tr = company_tr.find_next_sibling("tr")

            if location_tr:
                location = location_tr.get_text(" ", strip=True)

            # Fallback: search for something like "Paris (75)" within cell
            if not location:
                for td in cell_td.find_all("td"):
                    txt = td.get_text(" ", strip=True)
                    if "(" in txt and ")" in txt:
                        location = txt
                        break

            # ----- 4. Salary -----
            salary = ""
            salary_tr = None

            if location_tr:
                salary_tr = location_tr.find_next_sibling("tr")

            if salary_tr:
                salary_text = salary_tr.get_text(" ", strip=True)
                if "€" in salary_text or "$" in salary_text:
                    salary = salary_text

            # ----- 4.5 Simplified application process
            easy_apply = False
            easy_apply_tr = None

            easy_apply_tr = cell_td.find(
                "tr", 
                style=lambda s: s is not None 
                and "color:#2d2d2d;font-size:14px;line-height:21px" in s
            )

            if easy_apply_tr:
                easy_apply = True

            # ----- 5. Extract Summary -----
            summary = ""
            summary_tr = None

            if easy_apply_tr:
                summary_tr = easy_apply_tr.find_next_sibling("tr")
            elif salary_tr:
                summary_tr = salary_tr.find_next_sibling("tr")
            elif location_tr:
                summary_tr = location_tr.find_next_sibling("tr")

            if summary_tr:
                summary = summary_tr.get_text(" ", strip=True)

            if not summary:
                summary_td = cell_td.find(
                    "td",
                    style=lambda s: s is not None 
                    and "padding:0;color:#767676;font-size:14px;line-height:21px" in s
                )
                if summary_td:
                    summary = summary_td.get_text(" ", strip=True)

            # TODO: add published_at

            # ----- 6. Build job dict -----
            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": job_url,
                    "summary": summary,
                    "salary": salary,
                    "rating": rating,
                    "easy_apply": easy_apply,
                    "platform": "indeed",
                }
            )

        return jobs
