"""
Price Parser Core Module

This module provides the main interface for extracting prices from shop websites.
It dispatches to shop-specific parsers based on the shop name.
"""
from . import CORE_HANDLERS

def get_price(shop):
    """
    Retrieves the current price for a product from a specific shop.
    
    Dispatches to the appropriate shop-specific price parser based on the shop name.
    
    Args:
        shop: Dictionary containing 'name' and 'url' keys
        
    Returns:
        Float representing the product price
        
    Raises:
        NotImplementedError: If no price parser is available for the specified shop
    """
    handler = CORE_HANDLERS.get(shop["name"].lower())
    if not handler:
        raise NotImplementedError(f"No handler for {shop['name']} found.")
    return handler(shop["url"])
