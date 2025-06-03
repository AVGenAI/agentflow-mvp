#!/usr/bin/env python3
"""
Test script to verify Ollama integration with AgentFlow
"""
import os
import sys
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_ollama_integration():
    """Test if Ollama integration works properly"""
    print("🧪 Testing AgentFlow Ollama Integration")
    print("=" * 50)
    
    # Set environment variables for Ollama
    os.environ['LLM_PROVIDER'] = 'ollama'
    os.environ['OLLAMA_MODEL'] = 'llama2:latest'
    os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
    
    try:
        # Import and test agent creation
        from core.agent import ProcessAutomationAgent
        
        print("✅ Agent imports successful")
        
        # Create an agent
        agent = ProcessAutomationAgent()
        print(f"✅ Agent created: {agent.config.name}")
        print(f"   LLM Status: {'Ollama Connected' if agent.llm else 'Mock Mode'}")
        
        if agent.llm:
            print(f"   Model: {os.environ.get('OLLAMA_MODEL')}")
            print("🎉 SUCCESS: Ollama integration is working!")
            
            # Test a simple execution
            async def test_execution():
                print("\n🔬 Testing agent execution...")
                result = await agent.execute({"task": "Test Ollama connection"})
                print(f"   Execution Status: {result.status}")
                print(f"   Has Mock Mode Flag: {'mock_mode' in result.output_data}")
                
                if 'mock_mode' not in result.output_data:
                    print("✅ Agent is using real Ollama model!")
                else:
                    print("⚠️  Agent is still in mock mode")
                
                return result
            
            # Run the async test
            return asyncio.run(test_execution())
        else:
            print("⚠️  Agent is in mock mode - Ollama not connected")
            return None
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you have installed langchain-community:")
        print("   pip install langchain-community")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_ollama_server():
    """Check if Ollama server is running"""
    print("\n🔍 Checking Ollama server...")
    
    try:
        import urllib.request
        import json
        
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as response:
            data = json.loads(response.read().decode())
            models = data.get("models", [])
            print(f"✅ Ollama server is running with {len(models)} models")
            
            if models:
                print("Available models:")
                for model in models[:5]:  # Show first 5
                    print(f"  - {model['name']}")
                return True
            else:
                print("⚠️  No models found. Try: ollama pull llama2")
                return False
                
    except Exception as e:
        print(f"❌ Ollama server not accessible: {e}")
        print("   Start Ollama with: ollama serve")
        return False

if __name__ == "__main__":
    print("AgentFlow Ollama Integration Test")
    print("=" * 50)
    
    # Check Ollama server first
    if check_ollama_server():
        # Test the integration
        result = test_ollama_integration()
        
        if result and result.status == "completed":
            print("\n🎉 All tests passed!")
            print("Your Ollama integration is working correctly.")
        else:
            print("\n⚠️  Tests completed but check the results above.")
    else:
        print("\n❌ Cannot proceed without Ollama server running.")
        print("\nTo fix:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull a model: ollama pull llama2")
        print("3. Run this test again")