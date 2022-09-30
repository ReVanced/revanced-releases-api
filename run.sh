#!/bin/bash

# This script is used to run the application
# It is used by the Dockerfile

# get number of cores
CORES=$(grep -c ^processor /proc/cpuinfo)

# Start the application
hypercorn main:app --bind="${HYPERCORN_HOST}:${HYPERCORN_PORT}" \
--workers="$CORES" --log-level="$HYPERCORN_LOG_LEVEL" \
--worker-class uvloop