"""
Price Parser Package for Easy Price Monitor

This package provides a plugin-based system for extracting prices from different
online stores. Each shop has its own parser module that handles the specific
HTML/JSON structure of that retailer's product pages.

Currently supported shops:
- X-Kom (x-kom.pl) - Polish electronics retailer
- MediaExpert (mediaexpert.pl) - Polish electronics and appliances retailer

To add support for a new shop, create a new module in the shops/ directory and
register it in CORE_HANDLERS.
"""
from .shops import xkom
from .shops import mediaexpert

CORE_HANDLERS = {
    "x-kom": xkom.get_price_xkom,
    "mediaexpert": mediaexpert.get_price_mediaexpert,
    # Can add more shops here
}
