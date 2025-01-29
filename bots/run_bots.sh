#!/bin/bash

# Activate the virtual environment
source ./myenv/bin/activate  # Activate the virtual environment

# pip install -r bots/requirements.txt  

# Run the scraper
python3 bots/kingston.py 

# deactivate
