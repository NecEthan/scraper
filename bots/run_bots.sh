#!/bin/bash



# Activate the virtual environment
source ./myenv/bin/activate  # Activate the virtual environment

# Install the required dependencies (if not already installed)
# pip install -r bots/requirements.txt  

# Run the scraper
python3 bots/richmond.py  # Adjust this path to your script location

# Deactivate the virtual environment (optional, but good practice)
# deactivate
