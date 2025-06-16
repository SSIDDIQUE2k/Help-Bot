import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
backend_path = project_root / "backend"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

try:
    from mangum import Mangum
    from backend.app import app
    
    # Create the Netlify function handler
    handler = Mangum(app, lifespan="off")
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback handler
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': f'Import error: {e}'
        } 