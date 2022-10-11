#!/bin/bash

# This script is used to run the application
# It is used by the Dockerfile

# get number of cores
CORES=$(grep -c ^processor /proc/cpuinfo)

# Start the application
python3 ./run.py