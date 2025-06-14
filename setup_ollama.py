#!/usr/bin/env python3
"""
Setup script for Ollama integration with HelpBot
This script helps users install and configure Ollama for natural language processing
"""

import subprocess
import sys
import platform
import requests
import time
import json

def run_command(command, shell=False):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_ollama_installed():
    """Check if Ollama is installed"""
    success, stdout, stderr = run_command(["ollama", "--version"])
    return success

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    print("🔧 Installing Ollama...")
    
    if system == "darwin":  # macOS
        print("📱 Detected macOS - Installing via Homebrew...")
        success, stdout, stderr = run_command(["brew", "install", "ollama"])
        if not success:
            print("❌ Homebrew installation failed. Trying curl method...")
            success, stdout, stderr = run_command([
                "curl", "-fsSL", "https://ollama.ai/install.sh"
            ], shell=True)
            if success:
                success, stdout, stderr = run_command(["sh"], shell=True, input=stdout)
    
    elif system == "linux":
        print("🐧 Detected Linux - Installing via curl...")
        success, stdout, stderr = run_command([
            "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
        ], shell=True)
    
    elif system == "windows":
        print("🪟 Detected Windows - Please download Ollama from https://ollama.ai/download")
        print("   After installation, restart this script.")
        return False
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False
    
    return success

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False

def pull_model(model_name="llama3.2"):
    """Pull the specified model"""
    print(f"📥 Pulling model: {model_name}")
    print("   This may take several minutes depending on your internet connection...")
    
    success, stdout, stderr = run_command(["ollama", "pull", model_name])
    
    if success:
        print(f"✅ Successfully pulled {model_name}")
        return True
    else:
        print(f"❌ Failed to pull {model_name}: {stderr}")
        return False

def test_ollama_integration():
    """Test Ollama integration with a simple query"""
    print("🧪 Testing Ollama integration...")
    
    try:
        # Test the API endpoint
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": "Hello, respond with just 'Hello back!'",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                print(f"✅ Ollama is working! Response: {result['response'][:50]}...")
                return True
        
        print(f"❌ Ollama test failed: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 HelpBot Ollama Setup")
    print("=" * 50)
    
    # Check if Ollama is already installed
    if check_ollama_installed():
        print("✅ Ollama is already installed")
    else:
        print("❌ Ollama not found")
        install_choice = input("Would you like to install Ollama? (y/n): ").lower().strip()
        
        if install_choice != 'y':
            print("⚠️  Ollama installation skipped. HelpBot will run in basic mode.")
            return
        
        if not install_ollama():
            print("❌ Failed to install Ollama")
            return
    
    # Check if Ollama service is running
    if not check_ollama_running():
        print("⚠️  Ollama service is not running")
        start_choice = input("Would you like to start Ollama service? (y/n): ").lower().strip()
        
        if start_choice == 'y':
            print("🚀 Starting Ollama service in background...")
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            print("⏳ Waiting for Ollama service to start...")
            for i in range(10):
                if check_ollama_running():
                    print("✅ Ollama service is running")
                    break
                time.sleep(2)
                print(f"   Waiting... ({i+1}/10)")
            else:
                print("❌ Ollama service failed to start")
                print("   Please run 'ollama serve' manually in a separate terminal")
                return
    else:
        print("✅ Ollama service is running")
    
    # Pull the model
    model_choice = input("Which model would you like to use? (llama3.2/llama3.1/codellama) [llama3.2]: ").strip()
    if not model_choice:
        model_choice = "llama3.2"
    
    if not pull_model(model_choice):
        print("❌ Failed to pull model")
        return
    
    # Test integration
    if test_ollama_integration():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Make sure Ollama service is running: ollama serve")
        print("2. Start your HelpBot: cd backend && python app.py")
        print("3. Visit http://localhost:8000 to use HelpBot with AI enhancement")
        print("\nFeatures enabled:")
        print("✅ Natural language error analysis")
        print("✅ Conversational responses")
        print("✅ Error categorization and severity assessment")
        print("✅ Related query suggestions")
    else:
        print("❌ Setup completed but Ollama integration test failed")
        print("   HelpBot will still work in basic mode")

if __name__ == "__main__":
    main() 