#!/bin/bash
set -Eeuo pipefail

# ===============================
# Settings
# ===============================

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"
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
    if ! command -v ping >/dev/null 2>&1; then
        log "WARNING: 'ping' is unavailable; continuing without an internet check"
        return 0
    fi

    for attempt in 1 2 3; do
        if ping -c 1 -W 5 8.8.8.8 >/dev/null 2>&1; then
            return 0
        fi
        log "No internet connection (attempt $attempt/3). Waiting 20 seconds and retrying..."
        sleep 20
    done

    log "ERROR: Internet connection could not be established after 3 attempts"
    return 1
}

init_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi
    "$PYTHON_BIN" -m pip install --upgrade pip
    "$PYTHON_BIN" -m pip install -r "$REQUIREMENTS_FILE"
}

# ===============================
# Main logic
# ===============================

cd "$PROJECT_DIR" || exit 1
check_internet
init_venv

log "Starting script"

if [[ -f "$SCRIPT_PATH" ]]; then
    "$PYTHON_BIN" "$SCRIPT_PATH" --handlers mysql csv
else
    log "ERROR: Script file '$SCRIPT_PATH' not found!"
    exit 1
fi

log "Script finished"
