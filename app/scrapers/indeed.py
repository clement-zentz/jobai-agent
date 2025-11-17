from typing import List, Dict
from urllib.parse import urlencode, urljoin

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from .base import JobScraper


class IndeedScraper(JobScraper):
    BASE_URL = "https://fr.indeed.com/jobs"

    async def search(self, query: str, location: str | None = None) -> List[Dict]:
        print("[Indeed] Starting search…")

        params = {"q": query}
        if location:
            params["l"] = location
        url = f"{self.BASE_URL}?{urlencode(params)}"

        print(f"[Indeed] Target URL: {url}")

        async with Stealth().use_async(async_playwright()) as p:
            print("[Indeed] Playwright started with Stealth")

            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-accelerated-2d-canvas",
                    "--disable-webgl",
                    "--no-zygote",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )
            print("[Indeed] Chromium launched")

            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                locale="fr-FR",
                timezone_id="Europe/Paris",
                viewport={"width": 1280, "height": 900},
            )
            print("[Indeed] Context created (locale fr-FR)")

            page = await context.new_page()
            print("[Indeed] Page opened")

            try:
                print("[Indeed] Navigating to search URL…")
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                print("[Indeed] Page loaded (domcontentloaded)")

                # DEBUG: Save HTML preview
                html = await page.content()
                if "<title>" in html:
                    title = html.split("<title>")[1].split("</title>")[0]
                    print(f"[Indeed] Page title: {title}")

                # Detect CAPTCHA / robot blocks
                print("[Indeed] Checking CAPTCHA…")
                captcha = (
                    await page.query_selector("input[name='captcha']")
                    or await page.query_selector("div#captchadiv")
                    or await page.query_selector("div.g-recaptcha")
                )
                if captcha:
                    print("[Indeed] CAPTCHA detected! Returning empty list.")
                    await page.screenshot(path="/app/captcha_detected.png")
                    return []

                # Check for cookie wall
                cookie_wall = await page.query_selector("button#onetrust-accept-btn-handler")
                if cookie_wall:
                    print("[Indeed] Cookie consent button detected — clicking it.")
                    try:
                        await cookie_wall.click()
                        await page.wait_for_timeout(1000)
                    except Exception as e:
                        print(f"[Indeed] Failed to click cookie button: {e}")

                # Core selector
                cards = page.locator("a.tapItem")
                print("[Indeed] Waiting for job cards…")
                await page.wait_for_load_state("domcontentloaded")

                # First count attempt
                first_count = await cards.count()
                print(f"[Indeed] First card count: {first_count}")

                if first_count == 0:
                    print("[Indeed] No cards immediately found — trying fallback method")
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1500)

                total_cards = await cards.count()
                print(f"[Indeed] Final card count: {total_cards}")

                # If still zero → debug capture
                if total_cards == 0:
                    print("[Indeed] Still ZERO cards. Dumping page screenshot + HTML.")
                    await page.screenshot(path="/app/indeed_no_cards.png")

                    with open("/app/indeed_no_cards.html", "w", encoding="utf-8") as f:
                        f.write(html)

                    return []

                results: List[Dict] = []
                print("[Indeed] Extracting cards…")

                for i in range(total_cards):
                    print(f"[Indeed] Scraping card {i+1}/{total_cards}…")
                    card = cards.nth(i)

                    try:
                        title = await card.locator("h2 span").first.text_content()
                        company = await card.locator("span.companyName").first.text_content()
                        location_text = await card.locator("div.companyLocation").first.text_content()
                        href = await card.get_attribute("href")
                    except Exception as e:
                        print(f"[Indeed] Error extracting card {i}: {e}")
                        continue

                    title = title.strip() if title else None
                    company = company.strip() if company else None
                    location_text = location_text.strip() if location_text else None
                    full_url = urljoin("https://fr.indeed.com", href) if href else None

                    print(
                        f"[Indeed] Parsed → title={title}, company={company}, location={location_text}, url={full_url}"
                    )

                    if not title or not company or not full_url:
                        print("[Indeed] Card skipped due to missing fields")
                        continue

                    results.append(
                        self.normalize(
                            {
                                "title": title,
                                "company": company,
                                "location": location_text,
                                "description": None,
                                "url": full_url,
                                "platform": "Indeed",
                            }
                        )
                    )

                print(f"[Indeed] DONE. Extracted {len(results)} valid offers.")
                return results

            finally:
                print("[Indeed] Cleaning resources…")
                await context.close()
                await browser.close()
                print("[Indeed] Browser closed.")
