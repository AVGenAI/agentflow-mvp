#!/usr/bin/env python3
"""Simple test to verify file upload functionality"""
import requests
import json

API_URL = 'http://localhost:8000/api'

# First, get available agents
print("Getting available agents...")
response = requests.get(f"{API_URL}/agents")
agents = response.json()

if not agents:
    print("No agents available. Make sure the backend is running.")
    exit(1)

# Use the first agent
agent = agents[0]
print(f"\nUsing agent: {agent['name']} (ID: {agent['id']})")

# Test multi-file upload
print("\nTesting multi-file upload...")
payload = {
    "agent_id": agent['id'],
    "input_data": {
        "task": "Compare these documents and summarize the key differences",
        "files": [
            {
                "name": "report_2023.pdf",
                "type": "application/pdf",
                "content": "[File: report_2023.pdf] - Type: application/pdf - Size: 245760 bytes - Requires server-side processing for content extraction"
            },
            {
                "name": "report_2024.pdf",
                "type": "application/pdf",
                "content": "[File: report_2024.pdf] - Type: application/pdf - Size: 312320 bytes - Requires server-side processing for content extraction"
            },
            {
                "name": "summary.docx",
                "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "content": "[File: summary.docx] - Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document - Size: 45056 bytes - Requires server-side processing for content extraction"
            }
        ],
        "file_count": 3
    }
}

try:
    response = requests.post(f"{API_URL}/agents/execute", json=payload)
    result = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Execution Status: {result.get('status', 'Unknown')}")
    
    # Pretty print the output
    if 'output' in result and 'result' in result['output']:
        print("\n" + "="*50)
        print("AGENT OUTPUT:")
        print("="*50)
        print(result['output']['result'])
    else:
        print("\nFull Response:")
        print(json.dumps(result, indent=2))
        
except Exception as e:
    print(f"Error: {e}")