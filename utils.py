import json
import os

DEFAULT_PRODUCTS = {
    "products": [
        {
            "id": 1,
            "name": "ASRock X870 Pro RS",
            "shops": [
                {
                    "name": "x-kom",
                    "url": "https://www.x-kom.pl/p/1281720-plyta-glowna-socket-am5-asrock-x870-pro-rs.html"
                }
            ]
        },
        {
            "id": 2,
            "name": "Gembird CR2032 (2szt)",
            "shops": [
                {
                    "name": "x-kom",
                    "url": "https://www.x-kom.pl/p/748392-bateria-i-akumulatorek-gembird-cr2032-2szt.html?cid=api09&eid=pdp_pcacc"
                }
            ]
        }
    ]
}

def load_products(PRODUCTS_FILE):
    """Load products from JSON file, if not create default file"""
    from datetime import datetime
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PRODUCTS, f, indent=4, ensure_ascii=False)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Created default product list: {PRODUCTS_FILE}")

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["products"]

DEFAULT_MYSQL_CONFIG = {
    "connection": {
        "host": "localhost",
        "database": "easy_price_monitor",
        "user": "easy-price-monitor",
        "password": "",
        "port": 3306,
    }
}


def load_mysql_config(MYSQL_CONFIG):
    """Load MySQL config from JSON file, if not create default file"""
    from datetime import datetime
    if not os.path.exists(MYSQL_CONFIG):
        with open(MYSQL_CONFIG, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_MYSQL_CONFIG, f, indent=4, ensure_ascii=False)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Created default MySQL config file: {MYSQL_CONFIG}")
        return DEFAULT_MYSQL_CONFIG["connection"]

    with open(MYSQL_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["connection"]

DEFAULT_APP_CONFIG = {
    "settings": [
        {
            "bUseDelayInterval": True,
            "interval": [
                {
                    "minIntervalSeconds": 5,
                    "maxInterval": 20
                }
            ],
            "alerts": {
                "bEnableAlerts": True,
                "percentDropThreshold": 3.5,
                "ProductIDs": []  # empty list means all products
            },
            "email": {
                "smtpServer": "smtp.gmail.com",
                "smtpPort": 587,
                "user": "source@gmail.com",
                "password": "password",
                "from": "source@gmail.com",
                "to": "target@gmail.com"
            }
        }
    ]
}

def load_app_config(app_config_path):
    """Load app config from JSON file, if not create default file"""
    from datetime import datetime
    if not os.path.exists(app_config_path):
        with open(app_config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_APP_CONFIG, f, indent=4, ensure_ascii=False)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Created default config file: {app_config_path}")
        return DEFAULT_APP_CONFIG["settings"]

    with open(app_config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["settings"]
