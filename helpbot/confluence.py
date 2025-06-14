import os
import time
import base64
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
USERNAME = os.getenv("CONFLUENCE_USERNAME")
API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

_CACHE = {}
_CACHE_TTL_SECONDS = 300

class ConfigError(Exception):
    pass

if not all([BASE_URL, USERNAME, API_TOKEN, SPACE_KEY]):
    raise ConfigError("One or more Confluence environment variables are missing. Please check your .env file.")

def _get_auth_header() -> Dict[str, str]:
    """Creates the Basic Auth header for Confluence API calls."""
    credentials = f"{USERNAME}:{API_TOKEN}".encode()
    encoded_credentials = base64.b64encode(credentials).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}

def test_connection() -> Dict[str, Any]:
    """
    Tests the connection to Confluence by fetching space details.
    Returns a dictionary with status and a detailed message.
    """
    url = f"{BASE_URL}/rest/api/space/{SPACE_KEY}"
    print(f"--- [Connection Test] ---")
    print(f"  URL: {url}")
    try:
        headers = {"Accept": "application/json", **_get_auth_header()}
        response = requests.get(url, headers=headers, timeout=15)
        print(f"  Status Code: {response.status_code}")
        response.raise_for_status()
        space_data = response.json()
        print(f"  Success! Found space: {space_data.get('name')}")
        return {
            "status": "success",
            "message": f"Successfully connected to space '{space_data.get('name')}'."
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            message = "Authentication failed (401). Check your CONFLUENCE_USERNAME and CONFLUENCE_API_TOKEN."
        elif e.response.status_code == 404:
            message = f"Space '{SPACE_KEY}' not found (404). Check your CONFLUENCE_SPACE_KEY and that the user has access."
        else:
            message = f"An HTTP error occurred: {e.response.status_code} {e.response.reason}"
        print(f"  Error: {message}")
        return {"status": "error", "message": message}
    except requests.exceptions.RequestException as e:
        message = f"A connection error occurred. Check your CONFLUENCE_BASE_URL and network. Details: {e}"
        print(f"  Error: {message}")
        return {"status": "error", "message": message}
    finally:
        print("--- [Test End] ---")


def fetch_all_pages_in_space() -> List[Dict[str, Any]]:
    """
    Fetches all pages from the configured Confluence space with caching.
    """
    cache_key = f"space_{SPACE_KEY}_pages"
    cached = _CACHE.get(cache_key)
    if cached and (time.time() - cached['timestamp'] < _CACHE_TTL_SECONDS):
        print("--- [Fetching Pages] ---")
        print("  Returning pages from cache.")
        print("--- [Fetch End] ---")
        return cached['data']

    print("--- [Fetching Pages] ---")
    print("  Cache empty or expired. Fetching fresh from Confluence.")
    
    all_pages = []
    start = 0
    limit = 50
    headers = {"Accept": "application/json", **_get_auth_header()}
    
    while True:
        url = f"{BASE_URL}/rest/api/content/search"
        params = {
            "cql": f"space = '{SPACE_KEY}' and type = page",
            "limit": limit,
            "start": start,
            "expand": "body.view"
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            
            for page in results:
                html_content = page.get("body", {}).get("view", {}).get("value", "")
                if html_content:
                    all_pages.append({
                        "title": page.get("title", "Untitled"),
                        "url": f"{BASE_URL.rstrip('/')}{page.get('_links', {}).get('webui', '')}",
                        "html": html_content
                    })
            
            if len(results) < limit:
                break
            start += len(results)
        except requests.exceptions.RequestException as e:
            print(f"  Failed to fetch pages: {e}")
            raise  # Re-raise the exception to be handled by the caller

    _CACHE[cache_key] = {"timestamp": time.time(), "data": all_pages}
    print(f"  Fetched and cached {len(all_pages)} pages.")
    print("--- [Fetch End] ---")
    return all_pages 