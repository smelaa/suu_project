#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <URL>"
  exit 1
fi

URL="$1"

while true; do
  echo "Requesting $URL..."
  curl -s "$URL"
  echo -e "\n------"
  sleep 0.5
done
