#!/bin/bash

# Define the directory for the virtual environment
VENV_DIR="venv"

# Define the Python script to run
PYTHON_SCRIPT="main.py"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install Python 3."
    exit
fi

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if the virtual environment was activated
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Failed to activate virtual environment."
    exit 1
fi

# Run the Python script
if [ -f "$PYTHON_SCRIPT" ]; then
    echo "Running $PYTHON_SCRIPT..."
    python "$PYTHON_SCRIPT"
else
    echo "Python script $PYTHON_SCRIPT not found."
    deactivate
    exit 1
fi

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate
