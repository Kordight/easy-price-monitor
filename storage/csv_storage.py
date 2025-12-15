import csv
from datetime import datetime
import os

CSV_FILE = "price_history.csv"

def save_price_csv(results):
    """Saves price history to CSV file."""
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product", "shop", "price", "date", "product_url"])
        # add headers only if file is empty
        if f.tell() == 0:
            writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] CSV: Saved {len(results)} price record(s) to {CSV_FILE}")

def get_price_changes_csv():
    """Get price changes from CSV file by comparing last two prices for each product/shop combination."""
    if not os.path.exists(CSV_FILE):
        return []
    
    # Read all data from CSV
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        return []
    
    # Group by product and shop
    product_shop_prices = {}
    for row in rows:
        key = (row["product"], row["shop"])
        if key not in product_shop_prices:
            product_shop_prices[key] = []
        product_shop_prices[key].append({
            "price": float(row["price"]),
            "date": row["date"],
            "product_url": row.get("product_url", "")
        })
    
    # Calculate changes for each product/shop
    changes = []
    for (product_name, shop_name), prices in product_shop_prices.items():
        if len(prices) < 2:
            continue
        
        # Sort by date and get last two prices
        prices.sort(key=lambda x: x["date"])
        latest = prices[-1]
        previous = prices[-2]
        
        price_diff = latest["price"] - previous["price"]
        if previous["price"] != 0:
            percent_change = round((price_diff / previous["price"]) * 100, 2)
        else:
            percent_change = 0.0
        
        # Only include if there's an actual change
        if price_diff != 0:
            changes.append({
                "product_name": product_name,
                "shop_name": shop_name,
                "price": latest["price"],
                "currency": "PLN",
                "timestamp": latest["date"],
                "price_diff": price_diff,
                "percent_change": percent_change,
                "product_url": latest["product_url"]
            })
    
    return changes
