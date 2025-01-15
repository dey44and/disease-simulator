#!/usr/bin/env bash

# Define the name of the virtual environment directory
VENV_DIR=".venv2"

# Name of your Python script
PYTHON_SCRIPT="main.py"

# Directory to store the log files
LOG_DIR="log_processing"

# Ensure logs directory exists
mkdir -p "$LOG_DIR"

# Create the virtual environment if it doesn't already exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "Virtual environment activated."
else
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

# Loop to run the script 10 times
for i in {51..60}
do
    echo "Running iteration $i..."
    # Run the Python script and save output to logs/log<i>.txt
    python "$PYTHON_SCRIPT" > "${LOG_DIR}/log${i}.txt" 2>&1
done

echo "All runs completed."

# Deactivate the virtual environment
deactivate
echo "Virtual environment deactivated."
