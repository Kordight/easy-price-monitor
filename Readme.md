# Easy Price Monitor

**Easy Price Monitor** is a tool for tracking and monitoring product prices from various online sources.  
It is designed to track prices from multiple sites using easy-to-extend plugins. Currently, the tool supports popular tech stores in Poland.

---

## Disclaimer

This tool provides **no visual representation of collected data**.  
However, in [docs/grafana.md](docs/grafana.md) you can find a template to visually represent price history for selected products.

---

## Features

- Track prices from multiple websites
- Easy to expand support for new websites via plugins
- Saving price records to CSV
- **MySQL support**
- Lightweight
- **Built-in email alerting system for both MySQL and CSV**
- **Support for multiple email recipients**
- **Automatic alert consolidation when using multiple handlers**

---

## Installation

```bash
git clone https://github.com/Kordight/Easy-Price-Monitor
cd Easy-Price-Monitor
chmod +x save_prices.sh
```

> Make sure to edit `save_prices.sh` and replace `PROJECT_DIR` with your project path.
>
> For example, in `save_prices.sh`:
>
> **Before:**
> ```bash
> PROJECT_DIR="/path/to/your/project"
> ```
> **After (replace with your actual path):**
> ```bash
> PROJECT_DIR="/home/youruser/Easy-Price-Monitor"
> ```

---

## Usage

You can use the tool in **two ways**:

1. **Run the script directly**
   The easiest way is to run:

   ```bash
   ./save_prices.sh
   ```

   **Warning:** By default, this script also saves data to the database.  
    Make sure to check the `scheduled_price_scraping.md` section or disable it by changing the desired handlers (line 53):  

    ```bash
    $PYTHON_BIN "$SCRIPT_PATH" --handlers mysql csv
    ```
2. **Console call via Python**
   Run the script with:

   ```bash
   python easyPriceMonitor.py --handlers [csv,mysql]
   ```

   Example:
   - `python easyPriceMonitor.py --handlers csv mysql` 
   - `python easyPriceMonitor.py --handlers mysql`

---

### Configuring Watchlist

To add products to monitor, edit `products.json`.
This file is **automatically created if it does not exist**.

**Example structure:**

```json
{
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
```

---

### Configuring MySQL Connection

To configure the connection with the database, edit `mysql_config.json`.
This file is **automatically created if it does not exist**.

**Example structure:**

```json
{
  "connection": {
    "host": "localhost",
    "database": "easy_price_monitor",
    "user": "easy-price-monitor",
    "password": "",
    "port": 3306
  }
}
```

---

### Configuring Email Alerts

To configure email alerts, edit `easyPrice_monitor_config.json`.
This file is **automatically created if it does not exist**.

**Example structure:**

```json
{
  "settings": [
    {
      "bUseDelayInterval": true,
      "interval": [
        {
          "minIntervalSeconds": 5,
          "maxInterval": 20
        }
      ],
      "alerts": {
        "bEnableAlerts": true,
        "percentDropThreshold": 3.5,
        "ProductIDs": []
      },
      "email": {
        "smtpServer": "smtp.gmail.com",
        "smtpPort": 587,
        "user": "source@gmail.com",
        "password": "your-app-password",
        "from": "source@gmail.com",
        "to": ["recipient1@example.com", "recipient2@example.com"]
      }
    }
  ]
}
```

**Notes:**
- `bEnableAlerts`: Enable or disable email alerts
- `percentDropThreshold`: Minimum percentage change to trigger an alert (e.g., 3.5 means ±3.5%)
- `ProductIDs`: List of specific product IDs to monitor, or empty array `[]` for all products
- `email.to`: Can be a single email address as a string, or an array of multiple recipients
- **When using both CSV and MySQL handlers**, only one consolidated email will be sent

---

## Contributing

Contributions are welcome!
Please open issues or submit pull requests to improve the project.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
