import mysql.connector
from mysql.connector import Error
from datetime import datetime

def ensure_tables_exist(cursor):
    """Creates the necessary tables if they do not exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            url_pattern TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            shop_id INT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            currency VARCHAR(10) DEFAULT 'PLN',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (shop_id) REFERENCES shops(id)
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_urls (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        product_url TEXT NOT NULL,
        shop_id INT NOT NULL,
        UNIQUE KEY unique_product_shop (product_id, shop_id),
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (shop_id) REFERENCES shops(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)


def save_price_mysql(results, db_config, commit_every=500):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        ensure_tables_exist(cursor)

        count = 0
        for row in results:
            try:
                product_name = row["product"]
                shop_name = row["shop"]
                price = row["price"]
                timestamp = row.get("date", datetime.now())
                currency = row.get("currency", "PLN")
                product_url = row.get("product_url")

                # 1) Shop (insert if missing)
                cursor.execute("SELECT id FROM shops WHERE name = %s", (shop_name,))
                shop = cursor.fetchone()
                if not shop:
                    cursor.execute("INSERT INTO shops (name) VALUES (%s)", (shop_name,))
                    shop_id = cursor.lastrowid
                else:
                    shop_id = shop[0]

                # 2) Product (insert if missing)
                cursor.execute("SELECT id FROM products WHERE name = %s", (product_name,))
                product = cursor.fetchone()
                if not product:
                    cursor.execute("INSERT INTO products (name) VALUES (%s)", (product_name,))
                    product_id = cursor.lastrowid
                else:
                    product_id = product[0]

                # 3) Product URL (insert or update)
                if product_url and str(product_url).strip():
                    product_url = str(product_url).strip()
                    cursor.execute("""
                        INSERT INTO product_urls (product_id, product_url, shop_id)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE product_url = VALUES(product_url)
                    """, (product_id, product_url, shop_id))
                else:
                    from datetime import datetime
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [WARNING] No product_url found for product '{product_name}' at shop '{shop_name}'")

                # 4) Insert price record
                cursor.execute("""
                    INSERT INTO prices (product_id, shop_id, price, currency, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (product_id, shop_id, price, currency, timestamp))

                count += 1
                # Commit periodically
                if commit_every and count % commit_every == 0:
                    conn.commit()

            except Exception as e_inner:
                # Log the error and continue with the next row
                from datetime import datetime
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] MySQL error saving row {row!r}: {e_inner}")
                continue

        conn.commit()
        from datetime import datetime
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] MySQL: Saved {count} price record(s) to database")

    except mysql.connector.Error as e:
        from datetime import datetime
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] MySQL connection error: {e}")
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()

def get_price_changes(db_config, product_ids):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = f"""
        SELECT *
        FROM (
            SELECT 
                pr.product_id,
                p.name AS product_name,
                s.name AS shop_name,
                pd.product_url AS product_url,
                pr.price,
                pr.currency,
                pr.timestamp,
                pr.price - LAG(pr.price) OVER (
                    PARTITION BY pr.product_id, pr.shop_id 
                    ORDER BY pr.timestamp
                ) AS price_diff,
                ROUND(
                (pr.price - LAG(pr.price) OVER (
                        PARTITION BY pr.product_id, pr.shop_id 
                        ORDER BY pr.timestamp
                    )) 
                / LAG(pr.price) OVER (
                        PARTITION BY pr.product_id, pr.shop_id 
                        ORDER BY pr.timestamp
                    ) * 100,
                2
            ) AS percent_change,
                ROW_NUMBER() OVER (PARTITION BY pr.product_id, pr.shop_id ORDER BY pr.timestamp DESC) AS rn
            FROM prices pr
            JOIN products p ON p.id = pr.product_id
            JOIN shops s ON s.id = pr.shop_id
            JOIN product_urls pd ON pd.product_id = pr.product_id AND pd.shop_id = pr.shop_id
            WHERE pr.product_id IN ({",".join(map(str, product_ids))})
        ) t
        WHERE rn = 1
        ORDER BY timestamp DESC;

    """

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    latest = {}
    for row in rows:
        key = (row["product_id"], row["shop_name"])
        if key not in latest:
            latest[key] = row
    return list(latest.values())

def get_all_product_ids(db_config):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM products")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [row[0] for row in rows]

def get_shop_id_by_name(db_config, shop_name):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM shops WHERE name = %s", (shop_name,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return row[0] if row else None

def get_product_url_by_id(db_config, product_id, shop_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_url 
        FROM product_urls 
        WHERE product_id = %s AND shop_id = %s
    """, (product_id, shop_id))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

