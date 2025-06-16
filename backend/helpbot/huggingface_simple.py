import logging
import os
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class SimpleHuggingFaceService:
    """Simple Hugging Face service using only requests (no compilation dependencies)"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        self.available = bool(self.api_token)
        
        # Use simpler models that work well with API
        self.text_model = "google/flan-t5-small"  # Faster, smaller model
        self.chat_model = "microsoft/DialoGPT-small"  # Smaller conversational model
        
        if self.available:
            logger.info("Initialized Simple Hugging Face service with direct API calls")
        else:
            logger.warning("Hugging Face API not available - missing token")
    
    def is_available(self) -> bool:
        """Check if Hugging Face API is available"""
        if not self.available:
            return False
        
        try:
            # Test with a simple query
            response = self.query("Hello", max_length=10)
            return bool(response and len(response.strip()) > 0)
        except Exception as e:
            logger.warning(f"Hugging Face API test failed: {e}")
            return False
    
    def query(self, prompt: str, max_length: int = 100, use_chat_model: bool = False) -> str:
        """Send query to Hugging Face API"""
        if not self.available:
            return ""
        
        try:
            model = self.chat_model if use_chat_model else self.text_model
            api_url = f"{self.base_url}/{model}"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": min(max_length, 150),  # Limit to avoid timeout
                    "temperature": 0.3,
                    "do_sample": True,
                    "return_full_text": False
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": True
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'generated_text' in result[0]:
                        return result[0]['generated_text'].strip()
                    elif isinstance(result[0], str):
                        return result[0].strip()
                
                logger.warning(f"Unexpected API response format: {result}")
                return ""
            else:
                logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error calling Hugging Face API: {e}")
            return ""
    
    def enhance_error_analysis(self, user_query: str, error_data: dict) -> str:
        """Generate enhanced error analysis"""
        prompt = f"""Analyze this error and provide a solution:

User Query: {user_query}
Error: {error_data.get('error_code', 'Unknown error')}
Description: {error_data.get('explanation', 'No description')}

Provide a clear explanation and solution steps."""
        
        return self.query(prompt, max_length=200, use_chat_model=False)
    
    def generate_conversational_response(self, user_query: str, error_data: dict) -> str:
        """Generate a conversational response"""
        prompt = f"User asked about: {user_query}. The error is: {error_data.get('error_code', 'Unknown')}. Respond helpfully."
        
        return self.query(prompt, max_length=100, use_chat_model=True) 