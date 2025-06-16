#!/bin/bash

# Build script for Netlify deployment
echo "Starting HelpBot build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating required directories..."
mkdir -p backend/static
mkdir -p netlify/functions

# Copy static files if they exist
if [ -d "backend/templates" ]; then
    echo "Copying templates to static directory..."
    cp -r backend/templates/* backend/static/ 2>/dev/null || true
fi

# Verify the function file exists
if [ ! -f "netlify/functions/app.py" ]; then
    echo "Error: netlify/functions/app.py not found!"
    exit 1
fi

echo "Build completed successfully!"
echo "Function handler: netlify/functions/app.py"
echo "Static files: backend/static/" 