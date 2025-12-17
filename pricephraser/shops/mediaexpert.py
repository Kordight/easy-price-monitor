"""
MediaExpert Price Parser

This module extracts product prices from MediaExpert (mediaexpert.pl), a popular
Polish electronics and home appliances retailer. Extracts pricing information from
JSON-LD structured data embedded in product pages.
"""
import cloudscraper
from bs4 import BeautifulSoup
import json

constant_price_divisor = 1 # MediaExpert usually flips decimal in prices; temporary solution, variable should be 1 or 100 value

def get_price_mediaexpert(url):
    """
    Downloads and parses the product page from MediaExpert to extract the price.
    
    MediaExpert is a popular Polish electronics and home appliances retailer.
    This function extracts pricing from JSON-LD structured data embedded in the page.
    
    Args:
        url: Product page URL on mediaexpert.pl
        
    Returns:
        Float representing the product price in PLN
        
    Raises:
        Exception: If the page cannot be downloaded or price cannot be found
    """
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    if response.status_code != 200:
        raise Exception(f"[mediaexpert] Error, downloading webpage {url}: failed, response: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Collect all <script type="application/ld+json">
    scripts = soup.find_all("script", type="application/ld+json")
    if not scripts:
        raise Exception("[mediaexpert] No <script type='application/ld+json'> found on the page")

    price = None

    for script in scripts:
        try:
            data = json.loads(script.string)
        except Exception:
            continue

        if isinstance(data, dict):
            # easy case
            if data.get("@type") == "Product" and "offers" in data:
                price = float(data["offers"]["price"]) / constant_price_divisor
                break
            # case when there is a list of nodes
            if "@graph" in data:
                for node in data["@graph"]:
                    if node.get("@type") == "Product" and "offers" in node:
                        price = float(node["offers"]["price"])
                        break

    if price is None:
        raise Exception("[mediaexpert] Price not found in the JSON-LD scripts")

    return price
