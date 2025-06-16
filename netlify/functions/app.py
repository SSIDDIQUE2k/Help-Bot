import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from mangum import Mangum
from backend.app import app

# Create the Netlify function handler
handler = Mangum(app, lifespan="off") 