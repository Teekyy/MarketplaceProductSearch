#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Activate the virtual environment
source .venv/bin/activate

# Set the PYTHONPATH environment variable to include the project root
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Confirm setup
echo "Virtual environment activated and PYTHONPATH set."
echo "To run scripts, make sure to execute this script using: source setup.sh"