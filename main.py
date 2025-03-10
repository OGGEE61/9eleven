from scrapers.otomoto_scraper import OtomotoScraper
import asyncio
import logging

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

    print("Offers Info:")
    for offer in offers_info:
        print(offer)

    print("\nDetailed Offer URLs:")
    for link in listings:
        print(link)

    # The offers_info and listings can now be used for further processing or for a second scraping script
