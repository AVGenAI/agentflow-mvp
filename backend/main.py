"""
AgentFlow MVP - Main FastAPI application
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

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

class CreateWorkflowRequest(BaseModel):
    workflow: WorkflowDefinition

class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    input_data: Dict[str, Any]

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

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )