import logging
import os
from typing import Dict, List, Optional

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

class OllamaService:
    """Service for interacting with Ollama for natural language processing"""
    
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.llm = None
        self.parser = ErrorAnalysisParser()
        self.available = OLLAMA_AVAILABLE
        
        if self.available:
            self._initialize_llm()
        else:
            logger.info("Ollama dependencies not available - running in basic mode")
    
    def _initialize_llm(self):
        """Initialize the Ollama LLM"""
        if not self.available:
            return
            
        try:
            self.llm = OllamaLLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.3,  # Lower temperature for more consistent responses
                num_predict=500   # Limit response length
            )
            logger.info(f"Initialized Ollama with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.llm = None
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        if not self.available or not self.llm:
            return False
            
        try:
            # Test with a simple query
            response = self.llm.invoke("Hello")
            return bool(response)
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def enhance_error_analysis(self, user_query: str, confluence_data: Dict[str, str]) -> Dict[str, str]:
        """Enhance error analysis using natural language processing"""
        if not self.llm or not self.is_available():
            logger.warning("Ollama not available, returning original data")
            return {
                **confluence_data,
                'enhanced': False,
                'severity': 'medium',
                'category': 'general',
                'status': 'success'
            }
        
        try:
            prompt_template = PromptTemplate(
                input_variables=["user_query", "error_explanation", "resolution_steps"],
                template="""
You are an expert technical support assistant. A user has encountered an error and we found some documentation about it.

User Query: {user_query}

Found Documentation:
Explanation: {error_explanation}
Resolution: {resolution_steps}

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
            )
            
            prompt = prompt_template.format(
                user_query=user_query,
                error_explanation=confluence_data.get('explanation', 'No explanation available'),
                resolution_steps=confluence_data.get('resolution_steps', 'No resolution steps available')
            )
            
            response = self.llm.invoke(prompt)
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
                'status': 'success'
            }
            
            logger.info(f"Enhanced error analysis with Ollama for query: {user_query}")
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing analysis with Ollama: {e}")
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
        if not self.llm or not self.is_available():
            return f"I found information about your error: {error_data.get('explanation', 'No details available')}"
        
        try:
            prompt_template = PromptTemplate(
                input_variables=["user_query", "explanation", "resolution"],
                template="""
You are a helpful technical support assistant. A user asked about an error and you found the solution in our knowledge base.

User asked: {user_query}

From our documentation:
Issue: {explanation}
Solution: {resolution}

Provide a brief, friendly summary that:
1. Acknowledges their problem
2. Mentions we found the solution in our knowledge base
3. Encourages them to check the detailed explanation and resolution steps

Keep it short and conversational, like you're talking to a colleague. Don't repeat the full technical details.
"""
            )
            
            prompt = prompt_template.format(
                user_query=user_query,
                explanation=error_data.get('explanation', 'Unknown error'),
                resolution=error_data.get('resolution_steps', 'No solution available')
            )
            
            response = self.llm.invoke(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            return f"I found information about your error: {error_data.get('explanation', 'No details available')}"
    
    def suggest_related_queries(self, user_query: str, error_category: str) -> List[str]:
        """Suggest related queries the user might be interested in"""
        if not self.llm or not self.is_available():
            return []
        
        try:
            prompt_template = PromptTemplate(
                input_variables=["user_query", "category"],
                template="""
Based on this user query: {user_query}
Error category: {category}

Suggest 3 related error queries that users commonly search for in this category.
Return only the queries, one per line, without numbers or bullets.
Make them specific and realistic.
"""
            )
            
            prompt = prompt_template.format(
                user_query=user_query,
                category=error_category
            )
            
            response = self.llm.invoke(prompt)
            suggestions = [line.strip() for line in response.split('\n') if line.strip()]
            return suggestions[:3]  # Limit to 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return [] 