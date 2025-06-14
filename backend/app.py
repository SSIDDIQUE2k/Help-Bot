# Backend application entry point 
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

from helpbot.confluence_client import ConfluenceClient
from helpbot.html_extractor import HTMLExtractor

# Load environment variables from .env
load_dotenv('../.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HelpBot - AI Error Assistant")

# Configuration
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

logger.info(f"Loaded config - URL: {CONFLUENCE_URL}, User: {CONFLUENCE_USERNAME}, Space: {CONFLUENCE_SPACE_KEY}")

# Initialize clients
confluence_client = ConfluenceClient(
    base_url=CONFLUENCE_URL,
    username=CONFLUENCE_USERNAME,
    api_token=CONFLUENCE_API_TOKEN,
    space_key=CONFLUENCE_SPACE_KEY
)
html_extractor = HTMLExtractor()

class QueryRequest(BaseModel):
    query: str

class ErrorResponse(BaseModel):
    user_issue: str
    explanation: str
    resolution_steps: str
    resolution: str | None = None
    status: str = "success"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error("Frontend template 'templates/index.html' not found.")
        raise HTTPException(status_code=500, detail="UI template file not found on server.")

@app.get("/test-connection")
async def test_connection():
    """Test connection to Confluence and return detailed status."""
    try:
        result = confluence_client.test_connection()
        logger.info(f"Connection test result: {result}")
        return result
    except Exception as e:
        logger.error(f"Connection test endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test connection.")

@app.post("/query")
async def process_query(request: QueryRequest) -> ErrorResponse:
    """Processes user query using the multi-format extraction engine."""
    try:
        user_query = request.query.strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
        logger.info(f"Processing query: '{user_query}'")
        
        # 1. Find the most relevant page in Confluence
        search_results = confluence_client.search_pages(user_query, limit=1)
        if not search_results:
            return ErrorResponse(
                user_issue=user_query,
                explanation="No relevant documentation found for this error.",
                resolution_steps="Please refine your search query or check the Confluence space directly.",
                resolution="Please refine your search query or check the Confluence space directly.",
                status="error"
            )
        
        # 2. Get the content of that page
        best_page = search_results[0]
        logger.info(f"Found best page: '{best_page['title']}' (ID: {best_page['id']})")
        page_content = confluence_client.get_page_content(best_page['id'])
        
        if not page_content:
            return ErrorResponse(
                user_issue=user_query,
                explanation=f"Found page '{best_page['title']}' but could not retrieve its content.",
                resolution_steps="Please check the page permissions in Confluence or try again.",
                resolution="Please check the page permissions in Confluence or try again.",
                status="error"
            )
        
        # First try structured extraction to find specific error logs
        logger.info(f"Trying structured extraction for page content...")
        all_entries = html_extractor.extract_error_entries(page_content)
        logger.info(f"Found {len(all_entries)} structured error entries")
        
        if all_entries:
            # Find the best match for the user's query
            best_match = html_extractor.find_best_match(user_query, all_entries)
            if best_match:
                return ErrorResponse(
                    user_issue=user_query,
                    explanation=best_match.get("explanation", "No explanation found."),
                    resolution_steps=best_match.get("resolution", "No resolution steps found."),
                    resolution=best_match.get("resolution", "No resolution steps found."),
                )
        
        # Fallback to universal parser if no structured entries found
        logger.info(f"No structured entries found, using universal parser...")
        solution = html_extractor.find_best_solution(user_query, page_content)
        
        return ErrorResponse(
            user_issue=solution.get("user_issue", user_query),
            explanation=solution.get("explanation", "No explanation found."),
            resolution_steps=solution.get("resolution_steps", "No resolution steps found."),
            resolution=solution.get("resolution_steps", "No resolution steps found."),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing query '{request.query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "helpbot"}

if __name__ == "__main__":
    import uvicorn
    # Use reload=True for development to automatically apply code changes
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 