#!/bin/bash

python3 -m pip install --user pipx

printf "Installing pipx for the current user...\n"

python3 -m pip install --user pipx
python3 -m pipx ensurepath
echo 'eval "$(register-python-argcomplete pipx)"' >> ~/.profile
source ~/.profile

printf "Installing poetry for the current user...\n"

pipx install poetry