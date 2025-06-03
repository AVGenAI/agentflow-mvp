#!/usr/bin/env python3
"""Test script to verify file upload functionality"""
import requests
import json

API_URL = 'http://localhost:8000/api'

def test_single_file():
    """Test single file upload (legacy format)"""
    print("Testing single file upload (legacy format)...")
    
    payload = {
        "agent_id": "test-agent-id",  # You'll need to get a real agent ID
        "input_data": {
            "task": "Analyze this document",
            "file_content": "This is the content of a test file..."
        }
    }
    
    try:
        response = requests.post(f"{API_URL}/agents/execute", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_multi_file():
    """Test multiple file upload (new format)"""
    print("\nTesting multiple file upload (new format)...")
    
    payload = {
        "agent_id": "test-agent-id",  # You'll need to get a real agent ID
        "input_data": {
            "task": "Compare these documents and summarize the differences",
            "files": [
                {
                    "name": "document1.pdf",
                    "type": "application/pdf",
                    "content": "[File: document1.pdf] - Type: application/pdf - Size: 1024 bytes - Requires server-side processing for content extraction"
                },
                {
                    "name": "document2.docx",
                    "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "content": "[File: document2.docx] - Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document - Size: 2048 bytes - Requires server-side processing for content extraction"
                }
            ],
            "file_count": 2
        }
    }
    
    try:
        response = requests.post(f"{API_URL}/agents/execute", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def get_agents():
    """Get list of available agents"""
    print("Getting available agents...")
    try:
        response = requests.get(f"{API_URL}/agents")
        agents = response.json()
        print(f"Found {len(agents)} agents:")
        for agent in agents:
            print(f"  - {agent['name']} (ID: {agent['id']})")
        return agents
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("File Upload Test Script")
    print("=" * 50)
    
    # First get available agents
    agents = get_agents()
    
    if agents:
        # Use the first agent for testing
        agent_id = agents[0]['id']
        print(f"\nUsing agent: {agents[0]['name']} (ID: {agent_id})")
        
        # Update the payloads with real agent ID
        test_single_file.__code__ = test_single_file.__code__.replace(
            co_consts=tuple(
                agent_id if const == "test-agent-id" else const
                for const in test_single_file.__code__.co_consts
            )
        )
        
        # Run tests
        test_multi_file()
    else:
        print("No agents available. Make sure the backend is running.")