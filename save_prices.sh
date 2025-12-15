#!/bin/bash

# ===============================
# Settings
# ===============================

PROJECT_DIR="/home/sebastian/projects/easy-price-monitor" #Replace with yours project path
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/debug.log"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_BIN="$VENV_DIR/bin/python3"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
SCRIPT_PATH="$PROJECT_DIR/easyPriceMonitor.py"

# Ensure logs directory exists
mkdir -p "$LOG_DIR"

# ===============================
# Helper functions
# ===============================

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_internet() {
    if ! ping -c 1 8.8.8.8 >/dev/null; then
        log "No internet connection! Waiting 20 seconds and retrying..."
        sleep 20
    fi
}

init_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"
    $PYTHON_BIN -m pip install --upgrade pip
    $PYTHON_BIN -m pip install -r "$REQUIREMENTS_FILE"
}

# ===============================
# Main logic
# ===============================

cd "$PROJECT_DIR" || exit 1
check_internet
init_venv

log "Starting script"

if [ -f "$SCRIPT_PATH" ]; then
    $PYTHON_BIN "$SCRIPT_PATH" --handlers mysql csv
else
    log "ERROR: Script file '$SCRIPT_PATH' not found!"
fi

deactivate
log "Script finished"
