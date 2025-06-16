#!/usr/bin/env python3
"""
Test script for AI services (Ollama + Hugging Face backup)
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

from backend.helpbot.ollama_service import OllamaService

def test_ai_services():
    """Test both AI services"""
    print("🧪 Testing AI Services Integration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv('.env')
    
    # Initialize the service
    print("\n1. Initializing AI service...")
    service = OllamaService()
    
    print(f"   Available: {service.is_available()}")
    print(f"   Current provider: {service.current_provider}")
    
    if not service.is_available():
        print("❌ No AI services available")
        print("\nTo fix this:")
        print("• For Ollama: Make sure Ollama is running locally")
        print("• For Hugging Face: Set HUGGINGFACE_API_TOKEN in your .env file")
        return
    
    # Test basic functionality
    print(f"\n2. Testing {service.current_provider} service...")
    
    # Test enhancement
    test_data = {
        'explanation': 'Database connection timeout error',
        'resolution': 'Check database server status and network connectivity'
    }
    
    try:
        enhanced = service.enhance_error_analysis("Database timeout error", test_data)
        print(f"   ✅ Enhancement test passed")
        print(f"   Severity: {enhanced.get('severity')}")
        print(f"   Category: {enhanced.get('category')}")
        print(f"   AI Provider: {enhanced.get('ai_provider')}")
    except Exception as e:
        print(f"   ❌ Enhancement test failed: {e}")
    
    # Test conversational response
    try:
        response = service.generate_conversational_response("Database error", test_data)
        print(f"   ✅ Conversational response test passed")
        print(f"   Response preview: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Conversational response test failed: {e}")
    
    # Test suggestions
    try:
        suggestions = service.suggest_related_queries("Database error", "connection")
        print(f"   ✅ Suggestions test passed")
        print(f"   Generated {len(suggestions)} suggestions")
        for i, suggestion in enumerate(suggestions[:2], 1):
            print(f"     {i}. {suggestion}")
    except Exception as e:
        print(f"   ❌ Suggestions test failed: {e}")
    
    print(f"\n✅ Tests completed with {service.current_provider} provider!")

if __name__ == "__main__":
    test_ai_services() 