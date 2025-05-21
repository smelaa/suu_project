#!/bin/bash

# Check if an address was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <URL>"
  exit 1
fi

URL="$1"

# Infinite loop to repeatedly curl the address
while true; do
  echo "Requesting $URL..."
  curl -s "$URL"   # -s for silent mode (no progress bar)
  echo -e "\n------"
  sleep 0.5
done
