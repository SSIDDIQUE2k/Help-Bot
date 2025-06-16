#!/bin/bash

# Netlify dependency installation script - binary packages only
echo "Installing HelpBot dependencies (binary-only)..."

# Upgrade pip first
pip install --upgrade pip

# Core packages that definitely have binary wheels
echo "Installing core packages..."
pip install --only-binary=all fastapi==0.88.0
pip install --only-binary=all uvicorn==0.20.0  
pip install --only-binary=all requests==2.31.0
pip install --only-binary=all python-dotenv==1.0.0

# Web and parsing packages
echo "Installing web packages..."
pip install --only-binary=all beautifulsoup4==4.12.2
pip install --only-binary=all httpx==0.25.2
pip install --only-binary=all jinja2==3.1.2

# Utility packages
echo "Installing utility packages..."
pip install --only-binary=all python-multipart==0.0.6
pip install --only-binary=all aiofiles==23.2.1

# Pydantic v1 (no Rust required)
echo "Installing pydantic v1..."
pip install --only-binary=all pydantic==1.10.12

# Mangum for serverless
echo "Installing serverless adapter..."
pip install --only-binary=all mangum==0.17.0

# Create required directories
echo "Creating directories..."
mkdir -p backend/static
mkdir -p backend/templates

# Copy static files to publish directory if needed
echo "Setting up static files..."
if [ -f "backend/static/helpbot-widget.js" ]; then
    echo "✅ Widget JavaScript found"
else
    echo "⚠️  Widget JavaScript not found"
fi

if [ -f "backend/templates/index.html" ]; then
    echo "✅ Index template found"
else
    echo "⚠️  Index template not found"
fi

# Copy _redirects file to publish directory
echo "Setting up redirects..."
if [ -f "_redirects" ]; then
    cp _redirects backend/static/_redirects
    echo "✅ Redirects file copied to publish directory"
else
    echo "⚠️  Redirects file not found"
fi

# Verify function exists
echo "Checking function setup..."
if [ -f "netlify/functions/app.py" ]; then
    echo "✅ Netlify function found"
    # Make sure it's executable
    chmod +x netlify/functions/app.py
else
    echo "❌ Netlify function not found!"
fi

# Create a simple test file to verify publish directory
echo "Test deployment at $(date)" > backend/static/deploy-test.txt

echo "✅ All dependencies installed successfully (binary-only)!"
echo "📦 Package list:"
pip list | grep -E "(fastapi|uvicorn|requests|beautifulsoup4|httpx|pydantic|mangum)" 

echo "📁 Directory structure:"
ls -la backend/ | head -10

echo "🔧 Function directory:"
ls -la netlify/functions/ 