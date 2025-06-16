#!/usr/bin/env python3

import json
import sys
import os
from pathlib import Path

def handler(event, context):
    """Main Netlify function handler"""
    
    # Add the backend directory to the Python path
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    backend_path = project_root / "backend"

    # Add all necessary paths
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(backend_path))
    sys.path.insert(0, str(backend_path / "helpbot"))

    print(f"Function called - Method: {event.get('httpMethod', 'Unknown')}")
    print(f"Path: {event.get('path', 'Unknown')}")
    print(f"Backend path: {backend_path}")

    # Fallback HTML for debugging
    fallback_html = """
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
            .success { background: #e6ffe6; border: 1px solid #99ff99; color: #006600; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 HelpBot</h1>
            <div class="success status">
                <strong>Status:</strong> Netlify Function is Working! ✅<br>
                <strong>Detection:</strong> Function successfully detected and deployed
            </div>
            <div class="info status">
                <strong>Debug Info:</strong><br>
                Method: """ + event.get('httpMethod', 'Unknown') + """<br>
                Path: """ + event.get('path', 'Unknown') + """<br>
                Time: """ + str(context.get('aws_request_id', 'Unknown')) + """
            </div>
            <p><strong>The function is working!</strong> Now attempting to load the main application...</p>
        </div>
    </body>
    </html>
    """

    try:
        # Try to import and use the main app
        from mangum import Mangum
        from backend.app import app
        
        print("✅ Successfully imported main app")
        
        # Create the Netlify function handler
        mangum_handler = Mangum(app, lifespan="off")
        return mangum_handler(event, context)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        
        # Return fallback HTML for browser requests
        if event.get('httpMethod') == 'GET':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                },
                'body': fallback_html
            }
        
        # Return JSON error for API requests
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                "error": "Import failed", 
                "details": str(e),
                "message": "Function is working but couldn't import main app"
            })
        }

    except Exception as e:
        print(f"❌ General error: {e}")
        
        # Return fallback for any other error
        if event.get('httpMethod') == 'GET':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                },
                'body': fallback_html
            }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                "error": "General error", 
                "details": str(e),
                "message": "Function is working but encountered an error"
            })
        } 