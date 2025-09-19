#!/bin/bash
# Run Moments on port 5000 using PDM
cd "$(dirname "$0")"

# Ensure PDM is installed
if ! command -v pdm &> /dev/null; then
  echo "PDM not found. Installing..."
  pip install pdm
fi

# Install deps if not installed
pdm install

# Initialize app + generate fake data (admin@helloflask.com / moments)
pdm run flask init-app
pdm run flask lorem

# Run app
pdm run flask run --port 5002
