#!/usr/bin/env python3
"""
Test Hugging Face implementation specifically
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

from backend.helpbot.ollama_service import HuggingFaceService

def test_huggingface():
    """Test Hugging Face service specifically"""
    print("🤗 Testing Hugging Face Service")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv('.env')
    
    # Check if token is set
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        print("❌ HUGGINGFACE_API_TOKEN not set in .env file")
        print("\nTo fix this:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create a new token")
        print("3. Add HUGGINGFACE_API_TOKEN=your_token to your .env file")
        return
    
    print(f"✅ Token found: {token[:10]}...")
    
    # Initialize service
    print("\n1. Initializing Hugging Face service...")
    hf_service = HuggingFaceService()
    
    # Test availability
    print("\n2. Testing API availability...")
    is_available = hf_service.is_available()
    print(f"   Available: {is_available}")
    
    if not is_available:
        print("❌ Hugging Face API not available")
        return
    
    # Test basic query
    print("\n3. Testing basic query...")
    try:
        response = hf_service.query("What is a database error?")
        print(f"   ✅ Basic query successful")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Basic query failed: {e}")
    
    # Test error analysis format
    print("\n4. Testing error analysis prompt...")
    try:
        prompt = """
Analyze this error: Database connection timeout
Provide severity (low/medium/high) and category (connection/configuration/authentication/data/general)

Severity:
"""
        response = hf_service.query(prompt, max_length=50)
        print(f"   ✅ Error analysis test successful")
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   ❌ Error analysis test failed: {e}")
    
    print("\n✅ Hugging Face tests completed!")

if __name__ == "__main__":
    test_huggingface() 