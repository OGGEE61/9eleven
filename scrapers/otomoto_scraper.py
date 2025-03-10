import asyncio
import json
import logging
from urllib.parse import urlencode
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class OtomotoScraper:
    def __init__(self, config, headless=True):
        self.config = config
        self.headless = headless
        self.base_url = "https://www.otomoto.pl"

    def build_url(self):
        # Expected configuration keys: category, model, year, advanced_search.
        category = self.config.get("category", "osobowe")
        model = self.config.get("model", "porsche/911")
        year = self.config.get("year", "1990")
        advanced_search = self.config.get("advanced_search", "true")
        
        query_params = {
            "search[filter_float_year:to]": year,
            "search[advanced_search_expanded]": advanced_search
        }
        query_string = urlencode(query_params)
        url = f"{self.base_url}/{category}/{model}?{query_string}"
        return url

    async def scrape(self):
        url = self.build_url()
        logging.info("Starting to scrape: %s", url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/109.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            logging.info("Navigating to the page")
            await page.goto(url)

            try:
                logging.info("Waiting for cookie banner (if any)")
                accept_button = await page.wait_for_selector("#onetrust-accept-btn-handler", timeout=5000)
                await accept_button.click()
                logging.info("Cookie banner accepted")
            except:
                logging.info("Cookie banner not found or already accepted")

            try:
                logging.info("Waiting for article elements to ensure content is loaded")
                await page.wait_for_selector("article", timeout=10000)
            except:
                logging.info("Article elements did not load as expected")

            await page.screenshot(path="debug.png")
            logging.info("Screenshot saved as debug.png")

            html = await page.content()
            await browser.close()

        logging.info("Length of final HTML: %d", len(html))
        soup = BeautifulSoup(html, "html.parser")

        # Extract JSON‑LD data
        logging.info("Looking for JSON‑LD data")
        json_ld_script = soup.find("script", id="listing-json-ld")
        offers_info = []
        if json_ld_script:
            try:
                json_data = json.loads(json_ld_script.string)
                offers_info = json_data.get("mainEntity", {}).get("itemListElement", [])
                logging.info("Found %d offers in JSON‑LD", len(offers_info))
            except Exception as e:
                logging.error("Error parsing JSON‑LD: %s", e)
        else:
            logging.info("No JSON‑LD script found")

        # Extract offer links from article elements
        articles = soup.find_all("article")
        logging.info("Found %d article elements in final HTML", len(articles))

        listings = []
        for idx, article in enumerate(articles, start=1):
            for a in article.find_all("a", href=True):
                href = a["href"]
                if "/osobowe/oferta/" in href:
                    if not href.startswith("http"):
                        href = self.base_url + href
                    listings.append(href)
                    logging.info("Article %d: Found offer link: %s", idx, href)
                    break

        # Return data as a dictionary so that both offers_info and listings can be shared
        return {"offers_info": offers_info, "listings": listings}
