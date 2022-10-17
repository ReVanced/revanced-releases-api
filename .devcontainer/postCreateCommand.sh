#!/bin/bash

python3 -m pip install --user pipx

printf "Installing pipx for the current user...\n"

python3 -m pip install --user pipx
python3 -m pipx ensurepath
echo 'eval "$(register-python-argcomplete pipx)"' >> ~/.profile
source ~/.profile

printf "Installing poetry for the current user...\n"

pipx install poetry

printf "Starting Redis...\n"

docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

printf "Installing dependencies...\n"

poetry install --all-extras
