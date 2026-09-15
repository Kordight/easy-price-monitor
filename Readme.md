# Easy Price Monitor

**Easy Price Monitor** is a tool for tracking and monitoring product prices from various online sources.  
It tracks products from multiple sites using easy-to-extend plugins. Currently, the tool supports popular tech stores in Poland, including x-kom and MediaExpert.

---

## Disclaimer

The tool stores price history in CSV and/or MySQL. It can also generate a price-history plot with the `default` handler. For a Grafana-based view, see the template in [docs/grafana.md](docs/grafana.md).

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
- Enable or disable monitoring for individual products
- Enable email notifications globally or for selected products
- Randomized delays between product requests

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
   Make sure to check the [scheduled price scraping guide](docs/scheduled_price_scraping.md) or disable it by changing the desired handlers:

    ```bash
    $PYTHON_BIN "$SCRIPT_PATH" --handlers mysql csv
    ```
2. **Console call via Python**
   Run the script with:

   ```bash
  python easyPriceMonitor.py --handlers csv mysql
   ```

   Example:
   - `python easyPriceMonitor.py --handlers csv mysql` 
   - `python easyPriceMonitor.py --handlers mysql`
  - `python easyPriceMonitor.py --handlers csv default`

  `--handlers` accepts one or more space-separated handlers:
  - `csv` saves prices to `price_history.csv`
  - `mysql` saves prices to MySQL
  - `default` generates the price-history plot

  Email alerts are checked using changes from the selected `csv` and/or `mysql` handlers. Add `--notify` to enable alerts for every monitored product:

  ```bash
  python easyPriceMonitor.py --handlers csv mysql --notify
  ```

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
      "monitor": true,
      "notify_on_change": true,
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

Product fields:
- `monitor`: when `false`, the product is skipped and is not scraped. If omitted, it defaults to `true`.
- `notify_on_change`: when `true`, an eligible price change for this product can trigger an email. If omitted, it defaults to `false`.
- `shops`: one or more supported shops and their product URLs.

Use `--notify` to override the per-product notification setting for the current run. Without `--notify`, only products with `notify_on_change: true` can send alerts. A change must also meet `percentDropThreshold`, and `bEnableAlerts` must be `true`.

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
- Email alerts require either the `--notify` command-line flag or `notify_on_change: true` on the affected product
- The threshold applies to both price increases and decreases; the absolute percentage change must meet or exceed the configured value

The `save_prices.sh` script runs the monitor with `--handlers mysql csv`. It uses its own directory as the project directory by default; set `PROJECT_DIR` when launching it from another location. The script does not pass `--notify`, so scheduled runs only email for products explicitly marked with `notify_on_change: true`.

---

## Contributing

Contributions are welcome!
Please open issues or submit pull requests to improve the project.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
