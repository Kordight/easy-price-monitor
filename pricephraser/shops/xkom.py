import cloudscraper
from bs4 import BeautifulSoup
import re

def get_price_xkom(url):
    """
    Downloads and parses the product page from X-Kom to extract the price.
    Uses robust data-name and aria-label attributes to survive CSS class changes.
    """
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    
    if response.status_code != 200:
        raise Exception(f"[xkom] Error, downloading webpage {url}: failed, response: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the price container using data-name attribute
    price_container = soup.find(attrs={"data-name": "productPrice"})
    if not price_container:
        raise Exception("[xkom] Price container not found on the page")

    # Search for the price span using aria-label that contains "Cena:"
    price_span = price_container.find(attrs={"aria-label": re.compile(r"Cena:")})
    if not price_span:
        raise Exception("[xkom] Screen reader price (aria-label) not found")

    raw_price = price_span.get('aria-label')

    # Clean the price string by removing non-numeric characters and replacing comma with dot
    clean_price = raw_price.replace("Cena:", "").replace("zł", "").replace(" ", "").replace("\xa0", "").strip()
    
    # Replace comma with dot for decimal separator
    clean_price = clean_price.replace(",", ".")

    return float(clean_price)