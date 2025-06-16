import logging
import os
from typing import Dict, List, Optional
import requests
import json

logger = logging.getLogger(__name__)

# Try to import Ollama dependencies, but make them optional
try:
    from langchain_ollama import OllamaLLM
    from langchain.prompts import PromptTemplate
    from langchain.schema import BaseOutputParser
    OLLAMA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Ollama dependencies not available: {e}")
    OLLAMA_AVAILABLE = False
    # Create dummy classes for when Ollama is not available
    class OllamaLLM:
        def __init__(self, *args, **kwargs):
            pass
        def invoke(self, prompt):
            return "Ollama not available"
    
    class PromptTemplate:
        def __init__(self, *args, **kwargs):
            pass
        def format(self, *args, **kwargs):
            return ""
    
    class BaseOutputParser:
        def parse(self, text):
            return {}

class ErrorAnalysisParser(BaseOutputParser):
    """Custom parser for error analysis responses"""
    
    def parse(self, text: str) -> Dict[str, str]:
        """Parse the LLM response into structured format"""
        try:
            # Split response into sections
            sections = text.split('\n\n')
            result = {
                'explanation': '',
                'resolution': '',
                'severity': 'medium',
                'category': 'general'
            }
            
            current_section = None
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                if section.lower().startswith('explanation:'):
                    current_section = 'explanation'
                    result['explanation'] = section[12:].strip()
                elif section.lower().startswith('resolution:'):
                    current_section = 'resolution'
                    result['resolution'] = section[11:].strip()
                elif section.lower().startswith('severity:'):
                    result['severity'] = section[9:].strip().lower()
                elif section.lower().startswith('category:'):
                    result['category'] = section[9:].strip().lower()
                elif current_section:
                    result[current_section] += ' ' + section
            
            return result
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {
                'explanation': text,
                'resolution': 'Please check the error details and try again.',
                'severity': 'medium',
                'category': 'general'
            }

class HuggingFaceService:
    """Service for interacting with Hugging Face API"""
    
    def __init__(self, api_token: Optional[str] = None, model: str = "microsoft/DialoGPT-medium"):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.headers = {}
        
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"
        
        logger.info(f"Initialized Hugging Face service with model: {model}")
    
    def is_available(self) -> bool:
        """Check if Hugging Face API is available"""
        if not self.api_token:
            logger.warning("Hugging Face API token not provided")
            return False
        
        try:
            # Test with a simple query
            response = self.query("Hello")
            return bool(response)
        except Exception as e:
            logger.warning(f"Hugging Face API not available: {e}")
            return False
    
    def query(self, prompt: str, max_length: int = 500) -> str:
        """Send query to Hugging Face API"""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": 0.3,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
                elif isinstance(result, dict):
                    return result.get('generated_text', '').strip()
                else:
                    return str(result)
            else:
                logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error querying Hugging Face API: {e}")
            return ""

class OllamaService:
    """Unified service for AI processing with Ollama primary and Hugging Face backup"""
    
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.ollama_llm = None
        self.huggingface_service = None
        self.parser = ErrorAnalysisParser()
        self.ollama_available = OLLAMA_AVAILABLE
        self.current_provider = None
        
        # Initialize Ollama
        if self.ollama_available:
            self._initialize_ollama()
        
        # Initialize Hugging Face as backup
        self._initialize_huggingface()
        
        # Determine which service to use
        self._select_provider()
    
    def _initialize_ollama(self):
        """Initialize the Ollama LLM"""
        if not self.ollama_available:
            return
            
        try:
            self.ollama_llm = OllamaLLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.3,
                num_predict=500
            )
            logger.info(f"Initialized Ollama with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.ollama_llm = None
            self.ollama_available = False
    
    def _initialize_huggingface(self):
        """Initialize Hugging Face service"""
        try:
            # Use a smaller, faster model for production
            self.huggingface_service = HuggingFaceService(model="microsoft/DialoGPT-small")
            logger.info("Initialized Hugging Face service as backup")
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face service: {e}")
            self.huggingface_service = None
    
    def _select_provider(self):
        """Select the best available provider"""
        # Try Ollama first
        if self.ollama_available and self.ollama_llm and self._test_ollama():
            self.current_provider = "ollama"
            logger.info("Using Ollama as primary AI provider")
        # Fall back to Hugging Face
        elif self.huggingface_service and self.huggingface_service.is_available():
            self.current_provider = "huggingface"
            logger.info("Using Hugging Face as AI provider (Ollama not available)")
        else:
            self.current_provider = None
            logger.warning("No AI providers available - running in basic mode")
    
    def _test_ollama(self) -> bool:
        """Test if Ollama is working"""
        try:
            response = self.ollama_llm.invoke("Hello")
            return bool(response)
        except Exception as e:
            logger.warning(f"Ollama test failed: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if any AI service is available"""
        return self.current_provider is not None
    
    def _invoke_ai(self, prompt: str) -> str:
        """Invoke the available AI service"""
        if self.current_provider == "ollama" and self.ollama_llm:
            try:
                return self.ollama_llm.invoke(prompt)
            except Exception as e:
                logger.warning(f"Ollama failed, trying Hugging Face: {e}")
                # Fall back to Hugging Face
                if self.huggingface_service:
                    self.current_provider = "huggingface"
                    return self.huggingface_service.query(prompt)
                raise e
        
        elif self.current_provider == "huggingface" and self.huggingface_service:
            return self.huggingface_service.query(prompt)
        
        else:
            return "AI services not available"
    
    def enhance_error_analysis(self, user_query: str, confluence_data: Dict[str, str]) -> Dict[str, str]:
        """Enhance error analysis using available AI service"""
        if not self.is_available():
            logger.warning("No AI services available, returning original data")
            return {
                **confluence_data,
                'enhanced': False,
                'severity': 'medium',
                'category': 'general',
                'status': 'success'
            }
        
        try:
            prompt = f"""
You are an expert technical support assistant. A user has encountered an error and we found some documentation about it.

User Query: {user_query}

Found Documentation:
Explanation: {confluence_data.get('explanation', 'No explanation available')}
Resolution: {confluence_data.get('resolution_steps', 'No resolution steps available')}

Please analyze this error and provide ONLY:
1. Severity level (low/medium/high)
2. Category (connection/configuration/authentication/data/general)

Do NOT rewrite the explanation or resolution. Just analyze and categorize.

Format your response as:

Severity:
[low/medium/high]

Category:
[connection/configuration/authentication/data/general]
"""
            
            response = self._invoke_ai(prompt)
            enhanced_data = self.parser.parse(response)
            
            # Preserve original Confluence data and add AI analysis
            result = {
                'user_issue': user_query,
                'explanation': confluence_data.get('explanation', 'No explanation available'),
                'resolution_steps': confluence_data.get('resolution', 'No resolution steps available'),
                'resolution': confluence_data.get('resolution', 'No resolution steps available'),
                'severity': enhanced_data.get('severity', 'medium'),
                'category': enhanced_data.get('category', 'general'),
                'enhanced': True,
                'ai_provider': self.current_provider,
                'status': 'success'
            }
            
            logger.info(f"Enhanced error analysis with {self.current_provider} for query: {user_query}")
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing analysis with AI: {e}")
            # Return original data if enhancement fails
            return {
                **confluence_data,
                'enhanced': False,
                'severity': 'medium',
                'category': 'general',
                'status': 'success'
            }
    
    def generate_conversational_response(self, user_query: str, error_data: Dict[str, str]) -> str:
        """Generate a conversational response for the user"""
        if not self.is_available():
            return f"I found information about your error: {error_data.get('explanation', 'No details available')}"
        
        try:
            prompt = f"""
You are a helpful technical support assistant. A user asked about an error and you found the solution in our knowledge base.

User asked: {user_query}

From our documentation:
Issue: {error_data.get('explanation', 'Unknown error')}
Solution: {error_data.get('resolution_steps', 'No solution available')}

Provide a brief, friendly summary that:
1. Acknowledges their problem
2. Mentions we found the solution in our knowledge base
3. Encourages them to check the detailed explanation and resolution steps

Keep it short and conversational, like you're talking to a colleague. Don't repeat the full technical details.
"""
            
            response = self._invoke_ai(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            return f"I found information about your error: {error_data.get('explanation', 'No details available')}"
    
    def suggest_related_queries(self, user_query: str, error_category: str) -> List[str]:
        """Suggest related queries the user might be interested in"""
        if not self.is_available():
            return []
        
        try:
            prompt = f"""
Based on this user query: {user_query}
Error category: {error_category}

Suggest 3 related error queries that users commonly search for in this category.
Return only the queries, one per line, without numbers or bullets.
Make them specific and realistic.
"""
            
            response = self._invoke_ai(prompt)
            suggestions = [line.strip() for line in response.split('\n') if line.strip()]
            return suggestions[:3]  # Limit to 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return [] 