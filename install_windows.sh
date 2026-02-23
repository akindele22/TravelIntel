#!/bin/bash
# Installation script for Git Bash on Windows

echo "Installing dependencies for Windows..."
echo ""

# Upgrade pip first
python -m pip install --upgrade pip

# Install numpy/pandas first using pre-built wheels (avoids compiler requirement)
echo "Installing numpy and pandas (pre-built wheels)..."
pip install numpy pandas --only-binary :all:

# Install psycopg2-binary separately (often fixes Windows issues)
echo "Installing psycopg2-binary..."
pip install psycopg2-binary --no-cache-dir

if [ $? -ne 0 ]; then
    echo ""
    echo "psycopg2-binary installation failed. Trying alternative..."
    pip install psycopg[binary]
    if [ $? -ne 0 ]; then
        echo ""
        echo "Both psycopg2-binary and psycopg failed."
        echo "Please install PostgreSQL client libraries or use a different database adapter."
        exit 1
    fi
fi

# Install remaining dependencies
echo ""
echo "Installing remaining dependencies..."
pip install -r requirements.txt

echo ""
echo "Installation complete!"
