#!/bin/bash

# Configuration
PROJECT_DIR="/home/sebastian/easy-price-monitor"
CONFIG_JSON="$PROJECT_DIR/mysql_config.json"

# Check if config exists
if [ ! -f "$CONFIG_JSON" ]; then
    echo "Config file $CONFIG_JSON not found!"
    exit 1
fi

# Check dependencies
command -v jq >/dev/null 2>&1 || { echo "jq not found. Install it first."; exit 1; }
command -v mysqldump >/dev/null 2>&1 || { echo "mysqldump not found. Install it first."; exit 1; }

# Function to read configuration from JSON file
read_config() {
    DB_HOST=$(jq -r '.connection.host' "$CONFIG_JSON")
    DB_USER=$(jq -r '.connection.user' "$CONFIG_JSON")
    DB_PASSWORD=$(jq -r '.connection.password' "$CONFIG_JSON")
    DB_NAME=$(jq -r '.connection.database' "$CONFIG_JSON")
    DB_PORT=$(jq -r '.connection.port' "$CONFIG_JSON")
}

# Function to create a backup
create_backup() {
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_DIR="$PROJECT_DIR/backups"
    BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$TIMESTAMP.sql"
    mkdir -p "$BACKUP_DIR"

    if mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" --no-tablespaces "$DB_NAME" > "$BACKUP_FILE"; then
        echo "Backup successful: $BACKUP_FILE"
    else
        echo "Backup failed!"
        exit 1
    fi
}

# Run functions
read_config
create_backup
