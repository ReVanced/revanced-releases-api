#!/bin/bash

# This script is used to run the application
# It is used by the Dockerfile

# get number of cores
CORES=$(grep -c ^processor /proc/cpuinfo)

# Start the application
uvicorn main:app --host="$UVICORN_HOST" --port="$UVICORN_PORT" \
--workers="$CORES" --log-level="$UVICORN_LOG_LEVEL" --server-header \
--proxy-headers --forwarded-allow-ips="*"