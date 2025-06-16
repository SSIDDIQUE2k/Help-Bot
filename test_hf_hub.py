#!/usr/bin/env python3
"""
Test new Hugging Face Hub implementation
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

def test_hf_hub():
    """Test new Hugging Face Hub implementation"""
    print("🤗 Testing Hugging Face Hub Integration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv('.env')
    
    # Check if token is set
    token = os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
    if not token:
        print("❌ No Hugging Face token found")
        print("\nTo test with a real token:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create a new token")
        print("3. Add HF_TOKEN=your_token to your .env file")
        print("\n📝 Testing without token (fallback mode)...")
    else:
        print(f"✅ Token found: {token[:10]}...")
    
    from backend.helpbot.ollama_service import OllamaService, HuggingFaceService
    
    # Test Hugging Face service directly
    print("\n1. Testing HuggingFaceService directly...")
    hf_service = HuggingFaceService()
    print(f"   Available: {hf_service.available}")
    print(f"   Models: {hf_service.model}, {hf_service.text_model}")
    
    if hf_service.available:
        try:
            response = hf_service.query("What is an error?", use_text_model=True)
            print(f"   ✅ Direct query successful: {response[:50]}...")
        except Exception as e:
            print(f"   ❌ Direct query failed: {e}")
    
    # Test integrated service
    print("\n2. Testing OllamaService with HF backup...")
    service = OllamaService()
    print(f"   Current provider: {service.current_provider}")
    print(f"   HF service available: {service.huggingface_service.available if service.huggingface_service else False}")
    
    # Test enhancement
    print("\n3. Testing error analysis...")
    test_data = {
        'explanation': 'Database connection timeout error',
        'resolution': 'Check database server status'
    }
    
    try:
        result = service.enhance_error_analysis("Database timeout", test_data)
        print(f"   ✅ Enhancement successful")
        print(f"   Provider used: {result.get('ai_provider', 'unknown')}")
        print(f"   Severity: {result.get('severity')}")
        print(f"   Category: {result.get('category')}")
    except Exception as e:
        print(f"   ❌ Enhancement failed: {e}")
    
    print("\n✅ Hugging Face Hub tests completed!")
    
    print(f"\n📊 Integration Summary:")
    print(f"   • Hugging Face Hub Library: {'✅ Available' if hf_service.available else '❌ Not available'}")
    print(f"   • Primary AI Provider: {service.current_provider}")
    print(f"   • Fallback Ready: {'✅ Yes' if service.huggingface_service else '❌ No'}")

if __name__ == "__main__":
    test_hf_hub() 