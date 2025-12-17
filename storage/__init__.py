from . import csv_storage
from . import mysql_storage
from utils import load_mysql_config


def mysql_handler(results):
    db_config = load_mysql_config("mysql_config.json")
    mysql_storage.save_price_mysql(results, db_config)


def get_changes_mysql(product_ids):
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_price_changes(db_config, product_ids)

def get_changes_csv():
    return csv_storage.get_price_changes_csv()

def get_all_product_ids_mysql():
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_all_product_ids(db_config)

def get_product_url_by_id_mysql(product_id, shop_name):
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_product_url_by_id(db_config, product_id, shop_name)

def get_product_id_by_url_mysql(product_url):
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_product_id_by_url(db_config, product_url)

def get_shop_id_by_name_mysql(shop_name):
    db_config = load_mysql_config("mysql_config.json")
    return mysql_storage.get_shop_id_by_name(db_config, shop_name)

STORAGE_HANDLERS = {
    "csv": csv_storage.save_price_csv,
    "mysql": mysql_handler
}
