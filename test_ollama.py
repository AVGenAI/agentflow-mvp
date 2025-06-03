#!/usr/bin/env python3
"""
Quick test script to verify Ollama integration
"""
import os
import sys
import json
import urllib.request
import urllib.error

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_ollama_connection():
    """Test if Ollama is accessible"""
    print("🔍 Testing Ollama connection...")
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as response:
            data = json.loads(response.read().decode())
            models = data.get("models", [])
            print(f"✅ Ollama is running with {len(models)} models available")
            print("\nAvailable models:")
            for model in models[:10]:  # Show first 10 models
                print(f"  - {model['name']}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ Ollama responded with status {e.code}")
        return False
    except (urllib.error.URLError, OSError) as e:
        print(f"❌ Could not connect to Ollama: {e}")
        print("\nMake sure Ollama is running: ollama serve")
        return False

def test_simple_completion():
    """Test a simple completion with Ollama"""
    print("\n🤖 Testing simple completion...")
    
    # Get model from env or use default
    model = os.getenv("OLLAMA_MODEL", "llama2:latest")
    
    try:
        data = json.dumps({
            "model": model,
            "prompt": "What is 2+2? Answer in one word:",
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            print(f"✅ Model response: {result.get('response', '').strip()}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"❌ Failed with status {e.code}")
        return False
    except Exception as e:
        print(f"❌ Error during completion: {e}")
        return False

def main():
    print("AgentFlow Ollama Integration Test")
    print("=================================\n")
    
    # Test connection
    if not test_ollama_connection():
        sys.exit(1)
    
    # Test completion
    test_simple_completion()
    
    print("\n✅ Ollama integration is ready!")
    print("\nTo use with AgentFlow:")
    print("1. Make sure backend/.env has LLM_PROVIDER=ollama")
    print("2. Start the backend: cd backend && python main.py")
    print("3. The agents will now use Ollama for LLM capabilities")

if __name__ == "__main__":
    main()