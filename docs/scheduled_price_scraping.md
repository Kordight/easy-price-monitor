# Scheduled Price Scraping

This section explains how to automatically run **Easy Price Monitor** on a schedule to continuously collect product prices.

## Linux

On Linux systems we use the provided **shell script** (`save_prices.sh`) together with `cron` to schedule scraping tasks.

### 1. Make the script executable
```bash
chmod +x save_prices.sh
````

### 2. Set the project directory (optional)

The script uses its own directory as `PROJECT_DIR` by default. If you want to run it from another checkout or override the location, export `PROJECT_DIR` before starting it:

```bash
PROJECT_DIR="/path/to/Easy-Price-Monitor" ./save_prices.sh
```

### 3. Run the script manually (test)

```bash
./save_prices.sh
```

If everything works, the script will collect product prices and save them according to your configured handlers (e.g. CSV, MySQL).

### 4. Schedule with `cron`

To schedule scraping (e.g. every 6 hours):

1. Open your cron configuration:

   ```bash
   crontab -e
   ```

2. Add an entry like this:

   ```bash
   0 */6 * * * /path/to/Easy-Price-Monitor/save_prices.sh
   ```

This will run the scraper automatically every 6 hours.

---

## ⚠️ Warning

By default, the script also saves data to the database.
If you want to disable this, check the [save_prices.sh](save_prices.sh) and adjust the line:

```bash
$PYTHON_BIN "$SCRIPT_PATH" --handlers mysql csv
```

Remove `mysql` if you only want CSV output.

```