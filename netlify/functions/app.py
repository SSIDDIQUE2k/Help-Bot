#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
backend_path = project_root / "backend"

# Add all necessary paths
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / "helpbot"))

print(f"Current dir: {current_dir}")
print(f"Project root: {project_root}")
print(f"Backend path: {backend_path}")
print(f"Python path: {sys.path[:3]}")

# Fallback HTML for debugging
FALLBACK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>HelpBot - Loading...</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .error { background: #ffe6e6; border: 1px solid #ff9999; color: #cc0000; }
        .info { background: #e6f3ff; border: 1px solid #99ccff; color: #0066cc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 HelpBot</h1>
        <div class="info status">
            <strong>Status:</strong> Application is initializing...<br>
            <strong>Deployment:</strong> Netlify Function Active
        </div>
        <div class="error status">
            <strong>Debug Mode:</strong> If you see this page, the Netlify function is working but the main app couldn't load.
        </div>
        <p>This is a fallback page shown when the main application encounters import issues.</p>
        <p><strong>Next steps:</strong></p>
        <ul>
            <li>Check the Netlify function logs for detailed error information</li>
            <li>Verify all dependencies are properly installed</li>
            <li>Ensure all required files are present in the deployment</li>
        </ul>
    </div>
</body>
</html>
"""

# Try to import and create the handler
handler = None

try:
    from mangum import Mangum
    
    # Import the FastAPI app
    from backend.app import app
    
    # Create the Netlify function handler
    handler = Mangum(app, lifespan="off")
    
    print("✅ Successfully imported app and created handler")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    
    # Fallback handler for debugging
    def handler(event, context):
        import traceback
        error_details = traceback.format_exc()
        
        # For HTML requests, return the fallback page
        if event.get('httpMethod') == 'GET' and 'text/html' in event.get('headers', {}).get('accept', ''):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                },
                'body': FALLBACK_HTML
            }
        
        # For API requests, return JSON error
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': f'{{"error": "Import failed", "details": "{str(e)}", "traceback": "{error_details}"}}'
        }

except Exception as e:
    print(f"❌ General error: {e}")
    
    # Fallback handler for other errors
    def handler(event, context):
        import traceback
        error_details = traceback.format_exc()
        
        # For HTML requests, return the fallback page
        if event.get('httpMethod') == 'GET' and 'text/html' in event.get('headers', {}).get('accept', ''):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                },
                'body': FALLBACK_HTML
            }
        
        # For API requests, return JSON error
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': f'{{"error": "General error", "details": "{str(e)}", "traceback": "{error_details}"}}'
        }

# Ensure handler is always defined (Netlify requirement)
if handler is None:
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': FALLBACK_HTML
        } 