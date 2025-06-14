import re
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from . import confluence, extractor, models

app = FastAPI(title="HelpBot 2.0")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    # Trigger a connection test on startup to verify .env config
    # The result is printed to the console.
    confluence.test_connection()

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/test-connection")
async def get_test_connection():
    """Endpoint to allow the user to trigger a connection test from the UI."""
    return confluence.test_connection()

@app.post("/analyze", response_model=models.AnalyzeResponse)
async def analyze_error(req: models.AnalyzeRequest):
    """
    Analyzes the provided error text by searching the Confluence knowledge base.
    """
    print(f"--- [Analyze Request] ---")
    print(f"  Query: '{req.error_text}'")

    try:
        # 1. Fetch all pages from the configured Confluence space.
        all_pages = confluence.fetch_all_pages_in_space()

        # 2. Extract all structured "Error Log" entries from every page.
        all_issues = []
        for page in all_pages:
            issues_on_page = extractor.extract_issues_from_html(page["html"])
            for issue in issues_on_page:
                issue['source_title'] = page['title']
                issue['source_url'] = page['url']
            all_issues.extend(issues_on_page)
        
        print(f"  Found {len(all_issues)} structured logs in total.")

        # 3. Find the best match for the user's query.
        target_id_match = re.search(r"#?(\d+)", req.error_text)
        target_id = target_id_match.group(1) if target_id_match else None
        
        best_match = None
        if target_id:
            print(f"  Searching for specific Error ID: {target_id}")
            for issue in all_issues:
                if issue["id"] == target_id:
                    best_match = issue
                    break
        else:
            # If no ID, fall back to a simple text search.
            print(f"  No ID found, performing text search.")
            for issue in all_issues:
                if req.error_text.lower() in issue["issue"].lower():
                    best_match = issue
                    break
        
        if not best_match:
            print(f"  No match found for query.")
            raise HTTPException(status_code=404, detail="Could not find a matching error log in the knowledge base.")

        print(f"  Found best match: Error #{best_match['id']} from page '{best_match['source_title']}'")
        print(f"--- [Analyze End] ---")

        # 4. Return the structured response.
        return models.AnalyzeResponse(
            issue=f"Error Log #{best_match['id']}: {best_match['issue']}",
            explanation=best_match['issue'],
            resolution=best_match['resolution'],
            source_title=best_match['source_title'],
            source_url=best_match['source_url']
        )

    except confluence.ConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"  An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during analysis.") 