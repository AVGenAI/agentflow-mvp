#!/bin/bash

echo "🧪 Testing Conversation History Feature"
echo "========================================"
echo ""

# Test 1: Execute an agent with a simple task
echo "1. Executing agent with test task..."
curl -X POST http://localhost:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "customer_service_agent",
    "input_data": {
      "task": "Test conversation history feature"
    }
  }' > /tmp/agent_response.json

echo "✅ Agent execution completed"
echo ""

# Test 2: Check if conversation history is included
echo "2. Checking conversation history in response..."
python3 -c "
import json
with open('/tmp/agent_response.json', 'r') as f:
    data = json.load(f)
    
if 'conversation_history' in data.get('output', {}):
    history = data['output']['conversation_history']
    print(f'✅ Found {len(history)} messages in conversation history')
    for i, msg in enumerate(history):
        print(f'   Message {i+1}: {msg[\"role\"]} at {msg[\"timestamp\"]}')
else:
    print('❌ No conversation history found')
"

echo ""
echo "3. You can now view the conversation history in the frontend!"
echo "   Go to http://localhost:3000 and execute any agent to see:"
echo "   - Full conversation timeline with timestamps"
echo "   - User input and AI response"
echo "   - Model information"
echo "   - Chat-like display"
echo ""
echo "4. To view all conversations in CLI:"
echo "   cd backend && python view_conversations.py -i"