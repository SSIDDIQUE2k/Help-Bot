import os
import sys
import requests
import base64
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Add backend directory to Python path to import helpers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from helpers import get_chroma_client, get_embedding_function
from langchain_community.docstore.document import Document

# --- Configuration ---
# Load environment variables from the project root's .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
if not os.path.exists(dotenv_path):
    # Fallback for local dev if .env is in root
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)


CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_USER_EMAIL = os.getenv("CONFLUENCE_USER_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
COLLECTION_NAME = "confluence_docs"

# --- Confluence API Functions ---

def get_confluence_auth():
    """Returns the basic auth header for Confluence API."""
    credentials = f"{CONFLUENCE_USER_EMAIL}:{CONFLUENCE_API_TOKEN}".encode()
    return {"Authorization": f"Basic {base64.b64encode(credentials).decode()}"}

def fetch_all_pages(space_key):
    """Fetches all pages from a given Confluence space."""
    all_pages = []
    start = 0
    limit = 50
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content"
    headers = {"Accept": "application/json", **get_confluence_auth()}
    
    print(f"Fetching all pages from space: {space_key}...")
    
    while True:
        params = {
            "spaceKey": space_key,
            "type": "page",
            "status": "current",
            "limit": limit,
            "start": start,
            "expand": "body.storage"
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            all_pages.extend(results)
            
            if len(results) < limit:
                break
            start += limit
        except requests.exceptions.RequestException as e:
            print(f"Error fetching pages from Confluence: {e}", file=sys.stderr)
            return []
            
    print(f"Successfully fetched {len(all_pages)} pages.")
    return all_pages

# --- Main Indexing Logic ---

def main():
    """Main function to run the indexing process."""
    if not all([CONFLUENCE_BASE_URL, CONFLUENCE_USER_EMAIL, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY]):
        print("Error: Confluence environment variables are not fully set. Check your .env file.", file=sys.stderr)
        sys.exit(1)

    pages = fetch_all_pages(CONFLUENCE_SPACE_KEY)
    if not pages:
        print("No pages found or failed to fetch. Exiting.")
        return

    print("Cleaning and preparing documents for indexing...")
    langchain_docs = []
    for page in pages:
        page_id = page['id']
        title = page['title']
        page_url = f"{CONFLUENCE_BASE_URL.rstrip('/')}{page['_links']['webui']}"
        html_body = page.get('body', {}).get('storage', {}).get('value', '')
        
        # Clean HTML to plain text
        soup = BeautifulSoup(html_body, 'html.parser')
        plain_text = soup.get_text(" ", strip=True)
        
        if plain_text:
            doc = Document(
                page_content=plain_text,
                metadata={"id": page_id, "title": title, "url": page_url}
            )
            langchain_docs.append(doc)

    if not langchain_docs:
        print("No content to index after cleaning. Exiting.")
        return

    print(f"Prepared {len(langchain_docs)} documents.")
    print("Connecting to vector store and embedding documents...")
    
    try:
        embedding_function = get_embedding_function()
        vector_store = get_chroma_client().get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function
        )
        
        # Upsert documents into Chroma
        ids = [doc.metadata["id"] for doc in langchain_docs]
        contents = [doc.page_content for doc in langchain_docs]
        metadatas = [doc.metadata for doc in langchain_docs]

        vector_store.upsert(ids=ids, documents=contents, metadatas=metadatas)
        
        print("\n--- Indexing Complete ---")
        print(f"Successfully indexed {vector_store.count()} documents in collection '{COLLECTION_NAME}'.")
        print("You can now start the backend server and use the '/ask' endpoint.")

    except Exception as e:
        print(f"\nAn error occurred during embedding or indexing: {e}", file=sys.stderr)
        print("Please ensure your local vector database (Chroma) is running and accessible.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 