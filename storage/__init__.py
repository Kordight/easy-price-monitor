"""
Storage Package for Easy Price Monitor

This package provides storage handlers for saving and retrieving price data.
Supports both CSV files and MySQL database backends.

Available handlers:
- csv: Saves to local CSV file (price_history.csv)
- mysql: Saves to MySQL database with full relational structure

The package also provides functions for retrieving price changes and product information.
"""
from . import csv_storage
from . import mysql_storage
from utils import load_mysql_config


def mysql_handler(results):
    """
    Handler function for saving results to MySQL database.
    
    Loads MySQL configuration and delegates to the mysql_storage module.
    
    Args:
        results: List of price records to save
    """
    db_config = load_mysql_config("mysql_config.json")
    mysql_storage.save_price_mysql(results, db_config)


def get_changes_mysql(product_ids):
    """
    Retrieves price changes from MySQL database for specified products.
    
    Args:
        product_ids: List of product IDs to check for changes
        
    Returns:
        List of price change records
    """
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_price_changes(db_config, product_ids)

def get_changes_csv():
    """
    Retrieves price changes from CSV file.
    
    Returns:
        List of price change records
    """
    return csv_storage.get_price_changes_csv()

def get_all_product_ids_mysql():
    """
    Retrieves all product IDs from MySQL database.
    
    Returns:
        List of product IDs
    """
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_all_product_ids(db_config)

def get_product_url_by_id_mysql(product_id, shop_name):
    """
    Retrieves product URL from MySQL database.
    
    Args:
        product_id: Product ID to look up
        shop_name: Shop name to look up
        
    Returns:
        Product URL if found
    """
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_product_url_by_id(db_config, product_id, shop_name)

def get_shop_id_by_name_mysql(shop_name):
    """
    Retrieves shop ID from MySQL database by shop name.
    
    Args:
        shop_name: Shop name to look up
        
    Returns:
        Shop ID if found
    """
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_shop_id_by_name(db_config, shop_name)

def get_product_id_by_name_mysql(product_name):
    """
    Retrieves product ID from MySQL database by product name.
    
    This function is part of the refactored approach where products are identified
    by name instead of URL for improved flexibility.
    
    Args:
        product_name: Product name to look up
        
    Returns:
        Product ID if found
    """
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_product_id_by_name(db_config, product_name)

STORAGE_HANDLERS = {
    "csv": csv_storage.save_price_csv,
    "mysql": mysql_handler
}
