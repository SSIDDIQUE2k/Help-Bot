import requests
import logging
from typing import Dict, List, Optional, Any
import time

logger = logging.getLogger(__name__)

class ConfluenceClient:
    def __init__(self, base_url: str, username: str, api_token: str, space_key: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.space_key = space_key
        self.session = requests.Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Confluence and return detailed status"""
        try:
            # Test basic connectivity
            response = self.session.get(f"{self.base_url}/rest/api/space/{self.space_key}")
            
            if response.status_code == 200:
                space_info = response.json()
                return {
                    "status": "success",
                    "message": f"Connected to space: {space_info.get('name', 'Unknown')}",
                    "space_key": self.space_key,
                    "space_name": space_info.get('name'),
                    "base_url": self.base_url
                }
            elif response.status_code == 401:
                return {
                    "status": "error",
                    "message": "Authentication failed - check username and API token",
                    "status_code": 401
                }
            elif response.status_code == 404:
                return {
                    "status": "error", 
                    "message": f"Space '{self.space_key}' not found",
                    "status_code": 404
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Cannot connect to Confluence server - check URL and network",
                "error_type": "connection_error"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Unexpected error: {str(e)}",
                "error_type": "unknown"
            }
    
    def search_pages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for pages in the Confluence space"""
        try:
            params = {
                'cql': f'space = "{self.space_key}" AND text ~ "{query}"',
                'limit': limit,
                'expand': 'body.storage,version'
            }
            
            response = self.session.get(
                f"{self.base_url}/rest/api/content/search",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    def get_page_content(self, page_id: str) -> Optional[str]:
        """Get the full content of a specific page"""
        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/content/{page_id}",
                params={'expand': 'body.storage'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('body', {}).get('storage', {}).get('value', '')
            else:
                logger.error(f"Failed to get page {page_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            return None
    
    def get_overview_page(self) -> Optional[Dict[str, Any]]:
        """Get the main overview/index page for the space"""
        try:
            # Search for common overview page titles
            overview_queries = [
                "Error Documentation Overview",
                "Error Codes",
                "Error Reference", 
                "Documentation Index",
                "Overview"
            ]
            
            for query in overview_queries:
                pages = self.search_pages(query, limit=5)
                if pages:
                    # Return the first matching page
                    page = pages[0]
                    content = self.get_page_content(page['id'])
                    if content:
                        return {
                            'id': page['id'],
                            'title': page['title'],
                            'content': content,
                            'url': f"{self.base_url}/pages/viewpage.action?pageId={page['id']}"
                        }
            
            # If no specific overview found, get the space homepage
            response = self.session.get(f"{self.base_url}/rest/api/space/{self.space_key}")
            if response.status_code == 200:
                space_data = response.json()
                homepage_id = space_data.get('homepage', {}).get('id')
                if homepage_id:
                    content = self.get_page_content(homepage_id)
                    if content:
                        return {
                            'id': homepage_id,
                            'title': space_data.get('name', 'Space Homepage'),
                            'content': content,
                            'url': f"{self.base_url}/pages/viewpage.action?pageId={homepage_id}"
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting overview page: {str(e)}")
            return None 