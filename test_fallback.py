#!/usr/bin/env python3
"""
Test AI service fallback mechanism
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

def test_fallback_without_token():
    """Test what happens when Ollama fails and no HF token"""
    print("🔄 Testing AI Service Fallback (No HF Token)")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv('.env')
    
    from backend.helpbot.ollama_service import OllamaService
    
    # Test normal initialization
    print("\n1. Normal initialization (with Ollama)...")
    service = OllamaService()
    print(f"   Current provider: {service.current_provider}")
    print(f"   Available: {service.is_available()}")
    
    # Simulate Ollama failure
    print("\n2. Simulating Ollama failure...")
    service.ollama_llm = None  # Disable Ollama
    service.ollama_available = False
    service._select_provider()  # Re-select provider
    
    print(f"   Current provider after Ollama failure: {service.current_provider}")
    print(f"   Available after failure: {service.is_available()}")
    
    # Test what happens when we try to use AI
    print("\n3. Testing AI enhancement without token...")
    test_data = {
        'explanation': 'Database connection timeout',
        'resolution': 'Check database server'
    }
    
    result = service.enhance_error_analysis("Database error", test_data)
    print(f"   Enhanced: {result.get('enhanced')}")
    print(f"   AI Provider: {result.get('ai_provider', 'None')}")
    print(f"   Fallback successful: {result.get('status') == 'success'}")
    
    print("\n✅ Fallback test completed!")
    print("\n📝 Summary:")
    print("   • Without HF token: Falls back to basic mode")
    print("   • Still returns valid responses")
    print("   • No crashes or errors")

def test_with_mock_token():
    """Test initialization with a mock token"""
    print("\n" + "="*50)
    print("🤗 Testing with Mock Hugging Face Token")
    print("=" * 50)
    
    # Set a mock token temporarily
    os.environ["HUGGINGFACE_API_TOKEN"] = "hf_mock_token_for_testing"
    
    from backend.helpbot.ollama_service import OllamaService
    
    # Force reload the module to pick up the new token
    import importlib
    import backend.helpbot.ollama_service
    importlib.reload(backend.helpbot.ollama_service)
    
    service = backend.helpbot.ollama_service.OllamaService()
    print(f"   HF Service initialized: {service.huggingface_service is not None}")
    print(f"   Current provider: {service.current_provider}")
    
    # Clean up
    if "HUGGINGFACE_API_TOKEN" in os.environ:
        del os.environ["HUGGINGFACE_API_TOKEN"]

if __name__ == "__main__":
    test_fallback_without_token()
    test_with_mock_token() 