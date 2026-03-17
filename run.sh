#!/bin/bash

set -e

VENV_DIR="venv"

# create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
fi

# activate venv
source $VENV_DIR/bin/activate

# install deps ONLY if not already installed
if ! python -c "import requests" &>/dev/null; then
  echo "Installing dependencies..."
  pip install -r requirements.txt -q
fi

# run script
python scrape.py
