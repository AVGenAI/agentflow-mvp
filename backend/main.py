"""
AgentFlow MVP - Main FastAPI application
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from core.memory_manager import MemoryManager

from core.agent import (
    BaseAgent, 
    AgentConfig, 
    AgentExecution,
    ProcessAutomationAgent,
    DecisionMakingAgent
)
from core.workflow import (
    WorkflowOrchestrator,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowFactory
)
from core.business_workflows import BusinessWorkflowFactory
from core.specialized_agents import (
    CustomerServiceAgent,
    DataAnalystAgent,
    ComplianceOfficerAgent,
    HRRecruitmentAgent,
    FinancialAnalystAgent
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AgentFlow MVP",
    description="Enterprise Agentic AI Platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
orchestrator = WorkflowOrchestrator()
agents_registry: Dict[str, BaseAgent] = {}

# Request/Response models
class CreateAgentRequest(BaseModel):
    config: AgentConfig

class ExecuteAgentRequest(BaseModel):
    agent_id: str
    input_data: Dict[str, Any]
    model_override: Optional[str] = None

class CreateWorkflowRequest(BaseModel):
    workflow: WorkflowDefinition

class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    input_data: Dict[str, Any]
    model_override: Optional[str] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str
    task_count: int

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize default agents and workflows"""
    # Initialize database tables
    try:
        from database.connection import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        print("   Database will be initialized when PostgreSQL is available")
    # Create all specialized agents
    agents = [
        ProcessAutomationAgent(),
        DecisionMakingAgent(),
        CustomerServiceAgent(),
        DataAnalystAgent(),
        ComplianceOfficerAgent(),
        HRRecruitmentAgent(),
        FinancialAnalystAgent()
    ]
    
    # Register all agents
    for agent in agents:
        agents_registry[agent.id] = agent
        orchestrator.register_agent(agent.id, agent)
    
    # Keep references to specific agents for workflows
    process_agent = agents[0]
    decision_agent = agents[1]
    
    # Create sample workflows
    approval_workflow = WorkflowFactory.create_approval_workflow(
        name="Purchase Approval Workflow",
        description="Automated workflow for purchase approvals",
        analysis_agent_id=process_agent.id,
        decision_agent_id=decision_agent.id
    )
    orchestrator.register_workflow(approval_workflow)
    
    # Create business workflows
    # Customer complaint workflow
    complaint_workflow = BusinessWorkflowFactory.create_customer_complaint_workflow(
        customer_service_agent_id=agents[2].id,  # CustomerServiceAgent
        data_analyst_agent_id=agents[3].id,      # DataAnalystAgent
        compliance_agent_id=agents[4].id         # ComplianceOfficerAgent
    )
    orchestrator.register_workflow(complaint_workflow)
    
    # Financial reporting workflow
    financial_workflow = BusinessWorkflowFactory.create_financial_reporting_workflow(
        financial_analyst_id=agents[6].id,       # FinancialAnalystAgent
        data_analyst_id=agents[3].id,           # DataAnalystAgent
        compliance_officer_id=agents[4].id      # ComplianceOfficerAgent
    )
    orchestrator.register_workflow(financial_workflow)
    
    # Recruitment workflow
    recruitment_workflow = BusinessWorkflowFactory.create_recruitment_workflow(
        hr_agent_id=agents[5].id,               # HRRecruitmentAgent
        data_analyst_id=agents[3].id,           # DataAnalystAgent
        decision_agent_id=agents[1].id          # DecisionMakingAgent
    )
    orchestrator.register_workflow(recruitment_workflow)
    
    # Risk assessment workflow
    risk_workflow = BusinessWorkflowFactory.create_risk_assessment_workflow(
        compliance_officer_id=agents[4].id,     # ComplianceOfficerAgent
        data_analyst_id=agents[3].id,           # DataAnalystAgent
        financial_analyst_id=agents[6].id,      # FinancialAnalystAgent
        decision_agent_id=agents[1].id          # DecisionMakingAgent
    )
    orchestrator.register_workflow(risk_workflow)
    
    print(f"Initialized with {len(agents_registry)} agents and {len(orchestrator.workflows)} workflows")
    print("\nAvailable agents:")
    for agent in agents:
        print(f"  - {agent.config.name}: {agent.config.description}")
    print("\nAvailable workflows:")
    for wf_id, workflow in orchestrator.workflows.items():
        print(f"  - {workflow.name}: {workflow.description}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AgentFlow MVP",
        "version": "0.1.0",
        "status": "running"
    }

# Agent endpoints
@app.post("/api/agents", response_model=AgentResponse)
async def create_agent(request: CreateAgentRequest):
    """Create a new AI agent"""
    agent = BaseAgent(request.config)
    agents_registry[agent.id] = agent
    orchestrator.register_agent(agent.id, agent)
    
    return AgentResponse(
        id=agent.id,
        name=agent.config.name,
        description=agent.config.description,
        status=agent.status
    )

@app.get("/api/agents", response_model=List[AgentResponse])
async def list_agents():
    """List all registered agents"""
    return [
        AgentResponse(
            id=agent_id,
            name=agent.config.name,
            description=agent.config.description,
            status=agent.status
        )
        for agent_id, agent in agents_registry.items()
    ]

@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent details"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_registry[agent_id]
    return AgentResponse(
        id=agent.id,
        name=agent.config.name,
        description=agent.config.description,
        status=agent.status
    )

@app.post("/api/agents/execute")
async def execute_agent(request: ExecuteAgentRequest, background_tasks: BackgroundTasks):
    """Execute an agent with given input"""
    if request.agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_registry[request.agent_id]
    
    # Add model override to input data if provided
    if request.model_override:
        request.input_data["model_override"] = request.model_override
    
    # Execute agent asynchronously
    execution = await agent.execute(request.input_data)
    
    return {
        "execution_id": execution.execution_id,
        "status": execution.status,
        "output": execution.output_data,
        "metrics": execution.metrics
    }

# Workflow endpoints
@app.post("/api/workflows", response_model=WorkflowResponse)
async def create_workflow(request: CreateWorkflowRequest):
    """Create a new workflow"""
    workflow = request.workflow
    orchestrator.register_workflow(workflow)
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        task_count=len(workflow.tasks)
    )

@app.get("/api/workflows", response_model=List[WorkflowResponse])
async def list_workflows():
    """List all registered workflows"""
    return [
        WorkflowResponse(
            id=workflow_id,
            name=workflow.name,
            description=workflow.description,
            task_count=len(workflow.tasks)
        )
        for workflow_id, workflow in orchestrator.workflows.items()
    ]

@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details"""
    if workflow_id not in orchestrator.workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = orchestrator.workflows[workflow_id]
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "tasks": [task.dict() for task in workflow.tasks],
        "entry_task_id": workflow.entry_task_id,
        "variables": workflow.variables
    }

@app.post("/api/workflows/execute")
async def execute_workflow(request: ExecuteWorkflowRequest):
    """Execute a workflow with given input"""
    if request.workflow_id not in orchestrator.workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Add model override to input data if provided
    if request.model_override:
        request.input_data["model_override"] = request.model_override
    
    # Execute workflow
    execution = await orchestrator.execute_workflow(
        request.workflow_id,
        request.input_data
    )
    
    return {
        "execution_id": execution.id,
        "status": execution.status,
        "context": execution.context,
        "task_executions": {
            task_id: {
                "status": task_exec.status,
                "output": task_exec.output_data
            }
            for task_id, task_exec in execution.task_executions.items()
        },
        "metrics": execution.metrics
    }

@app.get("/api/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get execution details"""
    if execution_id not in orchestrator.executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    execution = orchestrator.executions[execution_id]
    return execution.dict()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agents_count": len(agents_registry),
        "workflows_count": len(orchestrator.workflows)
    }

# Models endpoint
@app.get("/api/models")
async def get_available_models():
    """Get available LLM models"""
    import subprocess
    import json
    
    try:
        # Get available Ollama models
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the output
            lines = result.stdout.strip().split('\n')
            models = []
            
            if len(lines) > 1:  # Skip header line
                for line in lines[1:]:
                    parts = line.split()
                    if parts:
                        model_name = parts[0].split(':')[0]  # Get base model name without tags
                        full_name = parts[0]  # Full name with tag
                        if not any(m['name'] == full_name for m in models):
                            models.append({
                                "name": full_name,
                                "display_name": full_name,
                                "provider": "ollama",
                                "available": True
                            })
            
            # Add some common models that might not be installed
            common_models = [
                {"name": "llama2:latest", "display_name": "Llama 2 (7B)", "provider": "ollama"},
                {"name": "deepseek-r1:latest", "display_name": "DeepSeek R1", "provider": "ollama"},
                {"name": "qwen2.5-coder:7b-instruct", "display_name": "Qwen 2.5 Coder (7B)", "provider": "ollama"},
                {"name": "gemma3:12b", "display_name": "Gemma 3 (12B)", "provider": "ollama"},
                {"name": "mistral:7b", "display_name": "Mistral (7B)", "provider": "ollama"},
            ]
            
            for common in common_models:
                if not any(m['name'] == common['name'] for m in models):
                    common['available'] = False
                    models.append(common)
            
            return models
        else:
            # Fallback to predefined list if ollama command fails
            return [
                {"name": "llama2:latest", "display_name": "Llama 2 (7B)", "provider": "ollama", "available": True},
                {"name": "deepseek-r1:latest", "display_name": "DeepSeek R1", "provider": "ollama", "available": True},
                {"name": "qwen2.5-coder:7b-instruct", "display_name": "Qwen 2.5 Coder (7B)", "provider": "ollama", "available": True},
                {"name": "gemma3:12b", "display_name": "Gemma 3 (12B)", "provider": "ollama", "available": True},
            ]
    except Exception as e:
        # Return default models if any error occurs
        return [
            {"name": "llama2:latest", "display_name": "Llama 2 (7B)", "provider": "ollama", "available": True},
            {"name": "deepseek-r1:latest", "display_name": "DeepSeek R1", "provider": "ollama", "available": True},
            {"name": "qwen2.5-coder:7b-instruct", "display_name": "Qwen 2.5 Coder (7B)", "provider": "ollama", "available": True},
            {"name": "gemma3:12b", "display_name": "Gemma 3 (12B)", "provider": "ollama", "available": True},
        ]


# Example endpoints for testing
@app.post("/api/examples/process-invoice")
async def example_process_invoice(invoice_data: Dict[str, Any]):
    """Example: Process an invoice using AI agents"""
    # Find process automation agent
    process_agent = next(
        (agent for agent in agents_registry.values() 
         if isinstance(agent, ProcessAutomationAgent)),
        None
    )
    
    if not process_agent:
        raise HTTPException(status_code=500, detail="Process agent not available")
    
    # Execute agent
    execution = await process_agent.execute({
        "task": f"Process this invoice: {invoice_data}",
        "invoice_data": invoice_data
    })
    
    return {
        "status": "processed",
        "execution_id": execution.execution_id,
        "result": execution.output_data
    }

@app.post("/api/examples/approval-request")
async def example_approval_request(request_data: Dict[str, Any]):
    """Example: Run approval workflow"""
    # Find approval workflow
    approval_workflow = next(
        (wf for wf in orchestrator.workflows.values() 
         if "approval" in wf.name.lower()),
        None
    )
    
    if not approval_workflow:
        raise HTTPException(status_code=500, detail="Approval workflow not available")
    
    # Execute workflow
    execution = await orchestrator.execute_workflow(
        approval_workflow.id,
        {
            "request_data": request_data,
            "decision_criteria": request_data.get("criteria", "standard")
        }
    )
    
    return {
        "workflow_execution_id": execution.id,
        "status": execution.status,
        "decision": execution.context.get("agent_outputs", {}).get("decision", {})
    }

@app.post("/api/examples/customer-complaint")
async def example_customer_complaint(complaint_data: Dict[str, Any]):
    """Example: Handle customer complaint"""
    complaint_workflow = next(
        (wf for wf in orchestrator.workflows.values() 
         if "complaint" in wf.name.lower()),
        None
    )
    
    if not complaint_workflow:
        raise HTTPException(status_code=500, detail="Complaint workflow not available")
    
    execution = await orchestrator.execute_workflow(
        complaint_workflow.id,
        {
            "complaint_text": complaint_data.get("complaint", ""),
            "customer_id": complaint_data.get("customer_id", ""),
            "severity": complaint_data.get("severity", "medium")
        }
    )
    
    return {
        "workflow_execution_id": execution.id,
        "status": execution.status,
        "response": execution.context.get("agent_outputs", {}).get("response", {})
    }

@app.post("/api/examples/financial-report")
async def example_financial_report(report_params: Dict[str, Any]):
    """Example: Generate financial report"""
    financial_workflow = next(
        (wf for wf in orchestrator.workflows.values() 
         if "financial" in wf.name.lower()),
        None
    )
    
    if not financial_workflow:
        raise HTTPException(status_code=500, detail="Financial workflow not available")
    
    execution = await orchestrator.execute_workflow(
        financial_workflow.id,
        {
            "reporting_period": report_params.get("period", "Q4 2023"),
            "include_forecast": report_params.get("include_forecast", True)
        }
    )
    
    return {
        "workflow_execution_id": execution.id,
        "status": execution.status,
        "report": execution.context.get("agent_outputs", {}).get("final_report", {})
    }

@app.post("/api/examples/screen-candidates")
async def example_screen_candidates(recruitment_data: Dict[str, Any]):
    """Example: Screen job candidates"""
    recruitment_workflow = next(
        (wf for wf in orchestrator.workflows.values() 
         if "recruitment" in wf.name.lower()),
        None
    )
    
    if not recruitment_workflow:
        raise HTTPException(status_code=500, detail="Recruitment workflow not available")
    
    execution = await orchestrator.execute_workflow(
        recruitment_workflow.id,
        {
            "candidate_resumes": recruitment_data.get("resumes", []),
            "job_requirements": recruitment_data.get("requirements", []),
            "position": recruitment_data.get("position", "Software Engineer")
        }
    )
    
    return {
        "workflow_execution_id": execution.id,
        "status": execution.status,
        "selected_candidates": execution.context.get("agent_outputs", {}).get("top_candidates", [])
    }

@app.post("/api/examples/risk-assessment")
async def example_risk_assessment(risk_data: Dict[str, Any]):
    """Example: Perform risk assessment"""
    risk_workflow = next(
        (wf for wf in orchestrator.workflows.values() 
         if "risk" in wf.name.lower()),
        None
    )
    
    if not risk_workflow:
        raise HTTPException(status_code=500, detail="Risk workflow not available")
    
    execution = await orchestrator.execute_workflow(
        risk_workflow.id,
        {
            "business_context": risk_data.get("context", "New product launch"),
            "risk_areas": risk_data.get("areas", ["financial", "operational", "compliance"])
        }
    )
    
    return {
        "workflow_execution_id": execution.id,
        "status": execution.status,
        "mitigation_strategy": execution.context.get("agent_outputs", {}).get("mitigation_strategy", {})
    }

# Conversation History Endpoints
@app.get("/api/agents/{agent_id}/conversations")
async def get_agent_conversations(agent_id: str, limit: int = 10):
    """Get recent conversations for an agent"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_registry[agent_id]
    if not agent.persistent_memory:
        return []
    
    return agent.persistent_memory.get_recent_conversations(limit=limit)

@app.get("/api/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, limit: int = 100):
    """Get messages for a specific conversation"""
    # We need to find which agent owns this conversation
    # For now, we'll create a temporary memory manager
    memory_manager = MemoryManager("temp", "temp")
    messages = memory_manager.get_conversation_history(conversation_id=conversation_id, limit=limit)
    
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return messages

@app.post("/api/agents/{agent_id}/search")
async def search_agent_conversations(agent_id: str, query: str, limit: int = 20):
    """Search through an agent's conversation history"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_registry[agent_id]
    if not agent.persistent_memory:
        return []
    
    return agent.persistent_memory.search_conversations(query=query, limit=limit)

@app.get("/api/agents/{agent_id}/memories")
async def get_agent_memories(agent_id: str, memory_type: Optional[str] = None):
    """Get stored memories for an agent"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_registry[agent_id]
    if not agent.persistent_memory:
        return []
    
    return agent.persistent_memory.recall_memory(memory_type=memory_type)

@app.post("/api/agents/{agent_id}/learn")
async def store_agent_memory(
    agent_id: str,
    memory_type: str,
    key: str,
    value: Any,
    confidence: float = 1.0,
    expires_in_days: Optional[int] = None
):
    """Store a new memory for an agent"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_registry[agent_id]
    if not agent.persistent_memory:
        raise HTTPException(status_code=400, detail="Agent does not have persistent memory enabled")
    
    agent.persistent_memory.store_memory(
        memory_type=memory_type,
        key=key,
        value=value,
        confidence=confidence,
        expires_in_days=expires_in_days
    )
    
    return {"status": "Memory stored successfully"}

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )