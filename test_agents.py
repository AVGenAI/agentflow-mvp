#!/usr/bin/env python3
"""Test agents in mock mode"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Make sure we're in mock mode
os.environ.pop('OPENAI_API_KEY', None)

try:
    from core.agent import ProcessAutomationAgent, DecisionMakingAgent
    from core.specialized_agents import CustomerServiceAgent
    
    print("Testing agent creation in mock mode...")
    print("=" * 50)
    
    # Test creating agents
    agents = [
        ProcessAutomationAgent(),
        DecisionMakingAgent(),
        CustomerServiceAgent()
    ]
    
    print(f"✅ Created {len(agents)} agents successfully")
    
    for agent in agents:
        print(f"\nAgent: {agent.config.name}")
        print(f"  ID: {agent.id}")
        print(f"  Status: {agent.status}")
        print(f"  LLM: {'Mock mode' if agent.llm is None else 'Connected'}")
    
    # Test executing an agent
    print("\n" + "=" * 50)
    print("Testing agent execution...")
    
    import asyncio
    
    async def test_execution():
        agent = agents[0]  # Process automation agent
        result = await agent.execute({"task": "Process invoice #123"})
        print(f"\n✅ Execution completed")
        print(f"  Status: {result.status}")
        print(f"  Output: {result.output_data.get('result', 'No result')}")
        return result
    
    # Run the test
    asyncio.run(test_execution())
    
    print("\n✅ All tests passed! Agents work in mock mode.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()