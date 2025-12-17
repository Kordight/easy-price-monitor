"""
Easy Price Monitor - Main Application Script

This script monitors product prices from various online stores and saves the data
to CSV files and/or MySQL database. It supports email alerts for significant price
changes and can be scheduled to run automatically.

The script uses a plugin-based architecture for supporting different online stores,
making it easy to add new retailers. Currently supports Polish tech stores like
X-Kom and MediaExpert.

Usage:
    python easyPriceMonitor.py --handlers [csv,mysql]
    
Example:
    python easyPriceMonitor.py --handlers csv mysql
"""
from datetime import datetime, timedelta
import argparse
import random
from time import sleep

from pricephraser.core import get_price
from storage import STORAGE_HANDLERS, get_changes_mysql, get_changes_csv, get_all_product_ids_mysql, get_product_id_by_name_mysql
from visualization import PLOT_HANDLERS
from utils import load_products, load_app_config
from notifier import send_email_alert

PRODUCTS_FILE = "products.json"
DATABASE_CONFIG_FILE = "mysql_config.json"
DEFAULT_APP_CONFIG = "easyPrice_monitor_config.json"

settings = load_app_config(DEFAULT_APP_CONFIG)
interval = settings[0]["interval"][0] if settings[0].get("bUseDelayInterval") else None
product_names = []


def sleep_with_log(interval):
    """
    Implements a random sleep delay between product scraping to avoid overwhelming the server.
    
    Args:
        interval: Dictionary containing 'minIntervalSeconds' and 'maxInterval' keys
    """
    time_to_wait = random.randint(interval["minIntervalSeconds"], interval["maxInterval"])
    wait_until = datetime.now() + timedelta(seconds=time_to_wait)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Waiting {time_to_wait}s until {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
    sleep(time_to_wait)

def main():
    """
    Main entry point for the Easy Price Monitor application.
    
    Parses command line arguments, loads product configurations, scrapes prices from
    configured shops, saves the data using specified handlers, and sends email alerts
    for significant price changes.
    """
    parser = argparse.ArgumentParser(description="Easy Price Monitor")
    parser.add_argument("--handlers", nargs="+", help="List of handlers to run  (csv, mysql, default)")
    args = parser.parse_args()

    products = load_products(PRODUCTS_FILE)

    results = []
    # Keep track of product-shop pairs that failed during this run
    scrape_errors = set()

    for idx, product in enumerate(products):
        product_name = product["name"]
        product_names.append(product_name)
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Monitoring product: {product_name}")

        for shop in product["shops"]:
            try:
                price = get_price(shop)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] {product_name} - {shop['name']}: {price} PLN")
                results.append({
                    "product": product_name,
                    "shop": shop["name"],
                    "price": price,
                    "date": datetime.now().isoformat(),
                    "product_url": shop["url"]
                })
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] {product_name} - {shop['name']}: {e}")
                # Mark this product-shop as errored to ignore in alerts
                scrape_errors.add((product_name, shop['name']))
        
        # Random delay between products (not after the last product)
        if interval and idx < len(products) - 1:
            sleep_with_log(interval)

    # dynamic handlers execution
    if args.handlers:
        for handler_name in args.handlers:
            handler_name = handler_name.lower()
            if handler_name in STORAGE_HANDLERS:
                STORAGE_HANDLERS[handler_name](results)
            elif handler_name in PLOT_HANDLERS:
                PLOT_HANDLERS[handler_name](results)
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] Invalid handler: {handler_name}")
    alerts_config = settings[0]["alerts"]
    if not alerts_config.get("bEnableAlerts", True):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Alerts are disabled in config.")
        return
    percent_threshold = alerts_config["percentDropThreshold"]
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Alert threshold set to {percent_threshold}%")
    smtp_config = {
        "server": settings[0]["email"]["smtpServer"],
        "port": settings[0]["email"]["smtpPort"],
        "user": settings[0]["email"]["user"],
        "password": settings[0]["email"]["password"]
    }
    email_from = settings[0]["email"]["from"]
    email_to = settings[0]["email"]["to"]
    
    # Collect changes from all handlers (consolidate to send only one email)
    all_changes = []
    handlers_used = []
    
    for handler_name in args.handlers or []:
        handler_name = handler_name.lower()
        if handler_name in STORAGE_HANDLERS:
            if handler_name == "mysql":
                handlers_used.append("MySQL")
                PRODUCT_IDS = settings[0]["alerts"].get("ProductIDs", [])
                if not PRODUCT_IDS:
                    # If no specific product IDs are set, monitor all products from the products list
                    # Products are identified by name (refactored from URL-based lookup)
                    for name in product_names:
                        product_id = get_product_id_by_name_mysql(name)
                        if product_id:
                            PRODUCT_IDS.append(product_id)
                changes = get_changes_mysql(PRODUCT_IDS)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Checking {len(PRODUCT_IDS)} product(s) for price changes in MySQL")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Found {len(changes)} price record(s) in MySQL")
                all_changes.extend(changes)
            elif handler_name == "csv":
                handlers_used.append("CSV")
                changes = get_changes_csv()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Checking for price changes in CSV")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Found {len(changes)} price record(s) in CSV")
                all_changes.extend(changes)
        elif handler_name in PLOT_HANDLERS:
            PLOT_HANDLERS[handler_name](results)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] Invalid handler: {handler_name}")

    # Remove duplicate changes (same product_name and shop_name)
    if all_changes:
        seen = set()
        unique_changes = []
        for change in all_changes:
            key = (change['product_name'], change['shop_name'])
            if key not in seen:
                seen.add(key)
                unique_changes.append(change)
        all_changes = unique_changes
        
        if len(handlers_used) > 1:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Consolidated {len(all_changes)} unique price change(s) from {' and '.join(handlers_used)}")

    # If any product-shop combination failed during scraping in this run, 
    # exclude them from alerts to avoid false alerts based on stale data
    if all_changes and scrape_errors:
        before = len(all_changes)
        filtered = []
        skipped_pairs = set()
        for c in all_changes:
            key = (c['product_name'], c['shop_name'])
            if key in scrape_errors:
                skipped_pairs.add(key)
            else:
                filtered.append(c)
        all_changes = filtered
        if skipped_pairs:
            skipped_count = before - len(all_changes)
            pairs_str = ", ".join([f"{p} - {s}" for p, s in sorted(skipped_pairs)])
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Skipping {skipped_count} change(s) due to scrape errors: {pairs_str}")
    
    # Filter out changes for products not included in the current run (e.g., legacy CSV entries)
    if all_changes:
        before_count = len(all_changes)
        all_changes = [c for c in all_changes if c.get('product_name') in product_names]
        if len(all_changes) != before_count:
            removed = before_count - len(all_changes)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Ignored {removed} change(s) for products not in current watchlist")
    
    if all_changes:
        alerts = []
        for c in all_changes:
            percent = c.get("percent_change")
            price_diff = c.get("price_diff")
            if percent is not None:
                percent_float = float(percent)
                diff_float = float(price_diff) if price_diff is not None else 0.0
                direction = "↑" if diff_float > 0 else "↓" if diff_float < 0 else "→"
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Price change detected: "
                      f"{c['product_name']} at {c['shop_name']}: "
                      f"{diff_float:+.2f} PLN ({percent_float:+.2f}%) {direction} "
                      f"Current: {c['price']} PLN")
                
                if abs(percent_float) >= percent_threshold:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ALERT] Threshold exceeded for {c['product_name']}: "
                          f"{abs(percent_float):.2f}% >= {percent_threshold}%")
                    alerts.append(c)
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Below threshold: "
                          f"{abs(percent_float):.2f}% < {percent_threshold}%")
        
        if alerts:
            # Debug preview of the first alert
            try:
                preview = {k: alerts[0].get(k) for k in ("product_name","shop_name","price","price_diff","percent_change","product_url","product_id")}
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Email alert preview: {preview}")
            except Exception:
                pass
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Sending {len(alerts)} alert(s) via email")
            send_email_alert(alerts, smtp_config, email_from, email_to)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] No price changes exceeded the alert threshold")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] No price changes detected")

if __name__ == "__main__":
    main()
