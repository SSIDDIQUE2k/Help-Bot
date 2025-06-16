# Backend application entry point 
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

from backend.helpbot.confluence_client import ConfluenceClient
from backend.helpbot.html_extractor import HTMLExtractor
from backend.helpbot.ollama_service import OllamaService

# Load environment variables from .env
load_dotenv('.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HelpBot - AI Error Assistant")

# Add CORS middleware for widget embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

logger.info(f"Loaded config - URL: {CONFLUENCE_URL}, User: {CONFLUENCE_USERNAME}, Space: {CONFLUENCE_SPACE_KEY}")

# Initialize clients with error handling
confluence_client = None
try:
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_username = os.getenv("CONFLUENCE_USERNAME")
    confluence_api_token = os.getenv("CONFLUENCE_API_TOKEN")
    confluence_space_key = os.getenv("CONFLUENCE_SPACE_KEY")
    
    if confluence_url and confluence_username and confluence_api_token and confluence_space_key:
        logger.info(f"Loaded config - URL: {confluence_url}, User: {confluence_username}, Space: {confluence_space_key}")
        confluence_client = ConfluenceClient(
            confluence_url, confluence_username, confluence_api_token, confluence_space_key
        )
        logger.info("Confluence client initialized successfully")
    else:
        logger.warning("Confluence environment variables not found - running in demo mode")
        logger.warning(f"Missing vars: URL={bool(confluence_url)}, User={bool(confluence_username)}, Token={bool(confluence_api_token)}, Space={bool(confluence_space_key)}")
except Exception as e:
    logger.error(f"Failed to initialize Confluence client: {e}")
    logger.warning("Continuing in demo mode")
    confluence_client = None
html_extractor = HTMLExtractor()

# Initialize Ollama service
ollama_service = None
try:
    ollama_service = OllamaService()
    if ollama_service.is_available():
        logger.info(f"Initialized Ollama with model: {ollama_service.model_name}")
    else:
        logger.warning("Ollama service not available - enhanced features disabled")
except Exception as e:
    logger.error(f"Failed to initialize Ollama service: {e}")
    logger.warning("Continuing without Ollama - basic mode only")
    ollama_service = OllamaService()  # Create instance but won't be available

# Demo data for when Confluence is not configured
DEMO_ERROR_DATA = [
    {
        'id': '3999',
        'error_code': 'Error Log #3999: AS2 Connection Timeout',
        'explanation': 'AS2 connection timed out while attempting to establish secure communication with trading partner. This typically occurs when the remote server is unresponsive or network connectivity issues prevent the handshake from completing within the configured timeout period.',
        'resolution': 'Check network connectivity to trading partner. Verify AS2 endpoint URL is correct. Increase timeout settings in AS2 configuration. Contact trading partner to verify their AS2 service is operational. Review firewall rules to ensure AS2 ports are open.'
    },
    {
        'id': '1',
        'error_code': 'Error Log 1: Database Connection Failed',
        'explanation': 'Unable to establish connection to the primary database server. Connection attempts are timing out after 30 seconds.',
        'resolution': 'Verify database server is running. Check connection string parameters. Ensure network connectivity between application and database server. Review database server logs for any errors.'
    },
    {
        'id': '2',
        'error_code': 'Error Log 2: Authentication Service Unavailable',
        'explanation': 'The authentication service is not responding to login requests. Users cannot authenticate and access the system.',
        'resolution': 'Restart the authentication service. Check service logs for errors. Verify LDAP/AD connectivity if using external authentication. Ensure authentication database is accessible.'
    },
    {
        'id': '500',
        'error_code': 'Error Log 500: Internal Server Error',
        'explanation': 'An unexpected internal server error occurred while processing the request. This is typically caused by unhandled exceptions in the application code.',
        'resolution': 'Check application logs for detailed error information. Review recent code deployments. Verify all required services and dependencies are running. Contact development team if error persists.'
    }
]

def find_demo_match(user_query: str) -> dict:
    """Find matching error from demo data using enhanced semantic matching"""
    user_query_lower = user_query.lower().strip()
    
    # Check for exact error log number matches first
    import re
    exact_match = re.search(r'error log\s*#?(\d+)', user_query_lower)
    if exact_match:
        query_log_num = exact_match.group(1)
        for entry in DEMO_ERROR_DATA:
            if entry.get('id') == query_log_num:
                return entry
    
    # Enhanced semantic matching
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cant', 'im', 'having', 'getting', 'error', 'log'}
    query_words = set(word for word in re.findall(r'\b\w{3,}\b', user_query_lower) if word not in stop_words)
    
    # Define error type keywords for better categorization
    error_types = {
        'connection': ['connection', 'connect', 'timeout', 'network', 'socket', 'unreachable', 'refused', 'disconnected'],
        'authentication': ['auth', 'login', 'password', 'credential', 'unauthorized', 'forbidden', 'access', 'permission'],
        'database': ['database', 'sql', 'query', 'table', 'connection', 'db', 'mysql', 'postgres', 'oracle'],
        'file': ['file', 'directory', 'path', 'folder', 'missing', 'not found', 'permission', 'read', 'write'],
        'server': ['server', 'internal', '500', 'service', 'unavailable', 'down', 'maintenance'],
        'validation': ['validation', 'invalid', 'format', 'required', 'missing', 'empty', 'null'],
        'api': ['api', 'endpoint', 'request', 'response', 'json', 'xml', 'rest', 'soap'],
        'configuration': ['config', 'configuration', 'setting', 'property', 'parameter', 'variable']
    }
    
    best_match = None
    highest_score = 0

    for entry in DEMO_ERROR_DATA:
        score = 0
        title = entry.get('error_code', '').lower()
        explanation = entry.get('explanation', '').lower()
        resolution = entry.get('resolution', '').lower()
        
        # Extract words from entry content
        title_words = set(re.findall(r'\b\w{3,}\b', title))
        explanation_words = set(re.findall(r'\b\w{3,}\b', explanation))
        resolution_words = set(re.findall(r'\b\w{3,}\b', resolution))
        
        # Basic keyword matching (weighted by importance)
        score += len(query_words.intersection(title_words)) * 5
        score += len(query_words.intersection(explanation_words)) * 3
        score += len(query_words.intersection(resolution_words)) * 1
        
        # Error type matching
        query_error_types = set()
        entry_error_types = set()
        
        for error_type, keywords in error_types.items():
            if any(keyword in user_query_lower for keyword in keywords):
                query_error_types.add(error_type)
            if any(keyword in title or keyword in explanation for keyword in keywords):
                entry_error_types.add(error_type)
        
        # Boost score for matching error types
        common_types = query_error_types.intersection(entry_error_types)
        score += len(common_types) * 4
        
        # Fuzzy matching for common error patterns
        fuzzy_patterns = [
            (r'timeout|time.*out', r'timeout|time.*out', 3),
            (r'connection.*failed|failed.*connection', r'connection.*failed|failed.*connection', 3),
            (r'not.*found|missing|does.*not.*exist', r'not.*found|missing|does.*not.*exist', 3),
            (r'unauthorized|access.*denied|permission.*denied', r'unauthorized|access.*denied|permission.*denied', 3),
            (r'internal.*server.*error|500.*error', r'internal.*server.*error|500.*error', 3),
            (r'invalid.*format|format.*invalid', r'invalid.*format|format.*invalid', 2),
            (r'database.*error|sql.*error', r'database.*error|sql.*error', 3),
            (r'network.*error|network.*issue', r'network.*error|network.*issue', 3)
        ]
        
        for query_pattern, entry_pattern, boost in fuzzy_patterns:
            if re.search(query_pattern, user_query_lower) and re.search(entry_pattern, title + ' ' + explanation):
                score += boost
        
        if score > highest_score:
            highest_score = score
            best_match = entry

    return best_match if highest_score > 0 else DEMO_ERROR_DATA[0]

class QueryRequest(BaseModel):
    query: str

class ErrorResponse(BaseModel):
    user_issue: str
    explanation: str
    resolution_steps: str
    resolution: str | None = None
    status: str = "success"
    enhanced: bool = False
    severity: str = "medium"
    category: str = "general"
    conversational_response: str | None = None
    suggestions: list[str] = []

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("backend/templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error("Frontend template 'templates/index.html' not found.")
        raise HTTPException(status_code=500, detail="UI template file not found on server.")

@app.get("/widget", response_class=HTMLResponse)
async def read_widget():
    """Serve the widget version of HelpBot"""
    try:
        with open("backend/templates/widget.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error("Widget template 'templates/widget.html' not found.")
        raise HTTPException(status_code=500, detail="Widget template file not found on server.")

@app.get("/widget.js")
async def get_widget_js():
    """Serve the embeddable widget JavaScript file"""
    try:
        with open("backend/static/helpbot-widget.js", "r") as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="application/javascript")
    except FileNotFoundError:
        logger.error("Widget JavaScript file 'static/helpbot-widget.js' not found.")
        raise HTTPException(status_code=500, detail="Widget JavaScript file not found on server.")



@app.get("/test-connection")
async def test_connection():
    """Test connection to Confluence and return detailed status."""
    try:
        if not confluence_client:
            return {
                "status": "error",
                "message": "Confluence client not initialized - running in demo mode",
                "confluence_configured": False
            }
        result = confluence_client.test_connection()
        logger.info(f"Connection test result: {result}")
        return result
    except Exception as e:
        logger.error(f"Connection test endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test connection.")

@app.get("/debug-search")
async def debug_search():
    """Debug Confluence search functionality"""
    if not confluence_client:
        return {"status": "error", "message": "Confluence not configured"}
    
    try:
        # Test basic search
        results = confluence_client.search_pages("Error", limit=5)
        return {
            "status": "success",
            "search_query": "Error",
            "results_count": len(results) if results else 0,
            "results": results[:3] if results else [],  # First 3 results only
            "message": f"Found {len(results) if results else 0} results for 'Error'"
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@app.post("/query")
async def process_query(request: QueryRequest) -> ErrorResponse:
    """Processes user query using the multi-format extraction engine."""
    try:
        user_query = request.query.strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
        logger.info(f"Processing query: '{user_query}'")
        
        # Extract error log number from query if present
        import re
        error_log_match = re.search(r'error log\s*#?(\d+)', user_query.lower())
        extracted_error_num = error_log_match.group(1) if error_log_match else None
        
        if extracted_error_num:
            logger.info(f"Extracted error log number: {extracted_error_num}")
        
        # Extract meaningful keywords for semantic search
        def extract_search_keywords(query: str) -> str:
            """Extract meaningful keywords from user query for better search results"""
            query_lower = query.lower().strip()
            
            # Remove common stop words and focus on meaningful terms
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cant', 'im', 'having', 'getting', 'my', 'me', 'i'}
            
            # Extract meaningful words (3+ characters, not stop words)
            meaningful_words = [word for word in re.findall(r'\b\w{3,}\b', query_lower) if word not in stop_words]
            
            # Prioritize technical terms and error-related keywords
            priority_terms = []
            regular_terms = []
            
            technical_indicators = ['error', 'timeout', 'connection', 'failed', 'database', 'server', 'api', 'auth', 'login', 'network', 'file', 'permission', 'invalid', 'missing', 'sql', 'json', 'xml', 'config', 'service']
            
            for word in meaningful_words:
                if word in technical_indicators or len(word) > 6:  # Long words are often technical
                    priority_terms.append(word)
                else:
                    regular_terms.append(word)
            
            # Combine priority terms first, then regular terms
            search_terms = priority_terms + regular_terms
            return ' '.join(search_terms[:5])  # Limit to top 5 terms for focused search
        
        extracted_keywords = extract_search_keywords(user_query)
        logger.info(f"Extracted search keywords: '{extracted_keywords}'")
        
        # 1. Find the most relevant page in Confluence or use demo data as fallback
        if not confluence_client:
            logger.warning("Confluence not configured - using demo data as fallback")
            # Use demo data when Confluence is not available
            demo_match = find_demo_match(user_query)
            
            # Enhance with Ollama if available
            enhanced_data = ollama_service.enhance_error_analysis(user_query, demo_match)
            
            # Generate conversational response
            conversational_response = ollama_service.generate_conversational_response(
                user_query, enhanced_data
            )
            
            # Get suggestions
            suggestions = ollama_service.suggest_related_queries(
                user_query, enhanced_data.get('category', 'general')
            )
            
            return ErrorResponse(
                user_issue=user_query,
                explanation=enhanced_data.get("explanation", demo_match.get("explanation", "No explanation found.")),
                resolution_steps=enhanced_data.get("resolution", demo_match.get("resolution", "No resolution steps found.")),
                resolution=enhanced_data.get("resolution", demo_match.get("resolution", "No resolution steps found.")),
                enhanced=enhanced_data.get("enhanced", False),
                severity=enhanced_data.get("severity", "medium"),
                category=enhanced_data.get("category", "general"),
                conversational_response=conversational_response,
                suggestions=suggestions
            )
        
        # Try multiple search strategies for better results
        search_results = None
        
        # Strategy 1: If we have an error log number, search for it specifically
        if extracted_error_num:
            search_query = f"Error Log #{extracted_error_num}"
            logger.info(f"Strategy 1 - Searching for specific error log: '{search_query}'")
            try:
                search_results = confluence_client.search_pages(search_query, limit=1)
                logger.info(f"Strategy 1 search results: {len(search_results) if search_results else 0} results")
                if search_results:
                    logger.info(f"First result: {search_results[0].get('title', 'No title')}")
            except Exception as e:
                logger.error(f"Strategy 1 search failed: {e}")
                search_results = None
        
        # Strategy 2: Search using extracted keywords
        if not search_results and extracted_keywords:
            logger.info(f"Strategy 2 - Searching with keywords: '{extracted_keywords}'")
            try:
                search_results = confluence_client.search_pages(extracted_keywords, limit=1)
                logger.info(f"Strategy 2 search results: {len(search_results) if search_results else 0} results")
                if search_results:
                    logger.info(f"First result: {search_results[0].get('title', 'No title')}")
            except Exception as e:
                logger.error(f"Strategy 2 search failed: {e}")
                search_results = None
        
        # Strategy 3: Fallback to original query
        if not search_results:
            logger.info(f"Strategy 3 - Fallback to original query: '{user_query}'")
            try:
                search_results = confluence_client.search_pages(user_query, limit=1)
                logger.info(f"Strategy 3 search results: {len(search_results) if search_results else 0} results")
                if search_results:
                    logger.info(f"First result: {search_results[0].get('title', 'No title')}")
            except Exception as e:
                logger.error(f"Strategy 3 search failed: {e}")
                search_results = None
        
        if not search_results:
            logger.error("No search results found for either targeted or original query")
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
                logger.info(f"Found structured match: {best_match.get('error_code', 'Unknown')}")
                # Enhance with Ollama if available
                enhanced_data = ollama_service.enhance_error_analysis(user_query, best_match)
                
                # Generate conversational response
                conversational_response = ollama_service.generate_conversational_response(
                    user_query, enhanced_data
                )
                
                # Get suggestions
                suggestions = ollama_service.suggest_related_queries(
                    user_query, enhanced_data.get('category', 'general')
                )
                
                return ErrorResponse(
                    user_issue=user_query,
                    explanation=enhanced_data.get("explanation", "No explanation found."),
                    resolution_steps=enhanced_data.get("resolution", "No resolution steps found."),
                    resolution=enhanced_data.get("resolution", "No resolution steps found."),
                    enhanced=enhanced_data.get("enhanced", False),
                    severity=enhanced_data.get("severity", "medium"),
                    category=enhanced_data.get("category", "general"),
                    conversational_response=conversational_response,
                    suggestions=suggestions
                )
            else:
                logger.warning("No structured match found despite having entries")
        
        # Fallback to universal parser if no structured entries found
        logger.info(f"No structured entries found, using universal parser...")
        solution = html_extractor.find_best_solution(user_query, page_content)
        
        # Enhance with Ollama if available
        enhanced_data = ollama_service.enhance_error_analysis(user_query, solution)
        
        # Generate conversational response
        conversational_response = ollama_service.generate_conversational_response(
            user_query, enhanced_data
        )
        
        # Get suggestions
        suggestions = ollama_service.suggest_related_queries(
            user_query, enhanced_data.get('category', 'general')
        )
        
        return ErrorResponse(
            user_issue=enhanced_data.get("user_issue", user_query),
            explanation=enhanced_data.get("explanation", "No explanation found."),
            resolution_steps=enhanced_data.get("resolution_steps", "No resolution steps found."),
            resolution=enhanced_data.get("resolution_steps", "No resolution steps found."),
            enhanced=enhanced_data.get("enhanced", False),
            severity=enhanced_data.get("severity", "medium"),
            category=enhanced_data.get("category", "general"),
            conversational_response=conversational_response,
            suggestions=suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing query '{request.query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/ollama-status")
async def ollama_status():
    """Check Ollama service status."""
    try:
        is_available = ollama_service.is_available()
        return {
            "status": "available" if is_available else "unavailable",
            "model": ollama_service.model_name,
            "base_url": ollama_service.base_url,
            "message": "Ollama is ready for natural language processing" if is_available else "Ollama is not available - using basic mode"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking Ollama status: {str(e)}"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint with service status"""
    try:
        ollama_available = ollama_service.is_available()
        confluence_configured = confluence_client is not None
        
        return {
            "status": "healthy",
            "service": "helpbot",
            "mode": "confluence" if confluence_configured else "demo",
            "confluence_configured": confluence_configured,
            "ollama_available": ollama_available,
            "features": {
                "confluence_integration": confluence_configured,
                "demo_data": not confluence_configured,
                "natural_language_processing": ollama_available,
                "error_enhancement": ollama_available,
                "conversational_responses": ollama_available,
                "widget_sidebar_toggle": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Use reload=False for production deployment
    reload = os.getenv("ENVIRONMENT", "production") == "development"
    
    logger.info(f"Starting server on {host}:{port} (reload={reload})")
    uvicorn.run("backend.app:app", host=host, port=port, reload=reload) 