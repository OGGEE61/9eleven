import asyncio
import logging
from selenium import webdriver

from database.database import create_db, insert_data

from scrapers.listing_scraper import scrape_listing
from scrapers.otomoto_scraper import OtomotoScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration is defined in the main file so it can be shared and adjusted
config = {
    "category": "osobowe",         # Vehicle category
    "model": "porsche/911",         # Change to other models as needed, e.g., "porsche/718"
    "year": "1990",                # Maximum year limit
    "advanced_search": "true"      # Toggle advanced search parameters
}

if __name__ == "__main__":
    scraper = OtomotoScraper(config=config, headless=True)
    result = asyncio.run(scraper.scrape())
    
    offers_info = result["offers_info"]
    listings = result["listings"]

    conn = create_db()
    
    # Set up the Selenium WebDriver with headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    # Example listing URLs from your scraped listings
    listing_urls = [
        "https://www.otomoto.pl/osobowe/oferta/porsche-911-porsche-911-ID6H4VVU.html"
        # add more URLs as needed
    ]
    
    for url in listing_urls:
        data = scrape_listing(url, driver)
        print("Scraped Data:", data)
        if data["vin"]:
            insert_data(conn, data)
        else:
            print("VIN not found for URL:", url)
    
    driver.quit()
    conn.close()
