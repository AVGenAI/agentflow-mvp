#!/usr/bin/env python3
"""
Show which models each agent will use
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.models import AGENT_MODEL_CONFIG, DEFAULT_MODEL_CONFIG

def main():
    print("🤖 AgentFlow - Agent Model Mapping")
    print("=" * 50)
    
    # Agent types created at startup
    agent_types = [
        ("ProcessAutomationAgent", "process_automation_agent"),
        ("DecisionMakingAgent", "decision_making_agent"), 
        ("CustomerServiceAgent", "customer_service_agent"),
        ("DataAnalystAgent", "data_analyst_agent"),
        ("ComplianceOfficerAgent", "compliance_officer_agent"),
        ("HRRecruitmentAgent", "hr_recruitment_agent"),
        ("FinancialAnalystAgent", "financial_analyst_agent")
    ]
    
    print("\n📋 Active Agents and Their Models:")
    print("-" * 50)
    
    for agent_name, agent_id in agent_types:
        config = AGENT_MODEL_CONFIG.get(agent_id, DEFAULT_MODEL_CONFIG)
        print(f"\n🔹 {agent_name}")
        print(f"   ID: {agent_id}")
        print(f"   Model: {config['model']}")
        print(f"   Temperature: {config['temperature']}")
        print(f"   Purpose: {config['description']}")
    
    print(f"\n📦 Default Fallback Model:")
    print(f"   Model: {DEFAULT_MODEL_CONFIG['model']}")
    print(f"   Temperature: {DEFAULT_MODEL_CONFIG['temperature']}")
    
    print(f"\n✅ Each agent will now use its optimized model!")
    print(f"💡 Restart the backend to apply changes: docker-compose restart backend")

if __name__ == "__main__":
    main()