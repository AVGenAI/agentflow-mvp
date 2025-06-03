"""
Workflow orchestration system for coordinating multiple agents
"""
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import uuid
import asyncio
from dataclasses import dataclass

from .agent import BaseAgent, AgentExecution, AgentStatus


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class WorkflowContext:
    """Shared context across workflow execution"""
    variables: Dict[str, Any]
    agent_outputs: Dict[str, Any]
    execution_history: List[Dict[str, Any]]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context"""
        if key in self.variables:
            return self.variables[key]
        elif key in self.agent_outputs:
            return self.agent_outputs[key]
        return default
    
    def set(self, key: str, value: Any):
        """Set value in context"""
        self.variables[key] = value
    
    def set_agent_output(self, agent_id: str, output: Any):
        """Store agent output"""
        self.agent_outputs[agent_id] = output


class WorkflowTask(BaseModel):
    """Individual task in a workflow"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: TaskType
    agent_id: Optional[str] = None
    agent_config: Optional[Dict[str, Any]] = None
    input_mapping: Dict[str, str] = Field(default_factory=dict)
    output_key: Optional[str] = None
    condition: Optional[str] = None
    next_tasks: List[str] = Field(default_factory=list)
    max_retries: int = 3
    timeout_seconds: int = 300


class WorkflowDefinition(BaseModel):
    """Definition of a complete workflow"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    tasks: List[WorkflowTask]
    entry_task_id: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    
    def get_task(self, task_id: str) -> Optional[WorkflowTask]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None


class WorkflowExecution(BaseModel):
    """Represents a workflow execution instance"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    task_executions: Dict[str, AgentExecution] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class WorkflowOrchestrator:
    """Orchestrates workflow execution across multiple agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
    
    def register_agent(self, agent_id: str, agent: BaseAgent):
        """Register an agent for use in workflows"""
        self.agents[agent_id] = agent
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """Register a workflow definition"""
        self.workflows[workflow.id] = workflow
    
    async def execute_workflow(
        self, 
        workflow_id: str, 
        input_data: Dict[str, Any]
    ) -> WorkflowExecution:
        """Execute a workflow with given input"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Create execution instance
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        # Initialize context
        context = WorkflowContext(
            variables={**workflow.variables, **input_data},
            agent_outputs={},
            execution_history=[]
        )
        
        try:
            # Execute workflow starting from entry task
            await self._execute_task(
                workflow=workflow,
                task_id=workflow.entry_task_id,
                context=context,
                execution=execution
            )
            
            execution.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.errors.append(str(e))
        
        finally:
            execution.completed_at = datetime.utcnow()
            execution.context = {
                "variables": context.variables,
                "agent_outputs": context.agent_outputs
            }
            execution.metrics["duration_seconds"] = (
                execution.completed_at - execution.started_at
            ).total_seconds()
        
        self.executions[execution.id] = execution
        return execution
    
    async def _execute_task(
        self,
        workflow: WorkflowDefinition,
        task_id: str,
        context: WorkflowContext,
        execution: WorkflowExecution
    ):
        """Execute a single task in the workflow"""
        task = workflow.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found in workflow")
        
        # Record task start
        context.execution_history.append({
            "task_id": task.id,
            "task_name": task.name,
            "started_at": datetime.utcnow().isoformat(),
            "type": task.type
        })
        
        try:
            if task.type == TaskType.SEQUENTIAL:
                await self._execute_sequential_task(task, context, execution)
            elif task.type == TaskType.PARALLEL:
                await self._execute_parallel_tasks(workflow, task, context, execution)
            elif task.type == TaskType.CONDITIONAL:
                await self._execute_conditional_task(workflow, task, context, execution)
            elif task.type == TaskType.LOOP:
                await self._execute_loop_task(workflow, task, context, execution)
            
            # Execute next tasks
            for next_task_id in task.next_tasks:
                await self._execute_task(workflow, next_task_id, context, execution)
                
        except Exception as e:
            context.execution_history[-1]["error"] = str(e)
            raise
    
    async def _execute_sequential_task(
        self,
        task: WorkflowTask,
        context: WorkflowContext,
        execution: WorkflowExecution
    ):
        """Execute a sequential task with an agent"""
        if not task.agent_id or task.agent_id not in self.agents:
            raise ValueError(f"Agent {task.agent_id} not found")
        
        agent = self.agents[task.agent_id]
        
        # Prepare input from context
        input_data = {}
        for target_key, source_key in task.input_mapping.items():
            value = context.get(source_key)
            if value is not None:
                input_data[target_key] = value
        
        # Execute agent
        agent_execution = await agent.execute(input_data)
        execution.task_executions[task.id] = agent_execution
        
        # Store output in context
        if task.output_key and agent_execution.status == AgentStatus.COMPLETED:
            context.set_agent_output(
                task.output_key,
                agent_execution.output_data
            )
    
    async def _execute_parallel_tasks(
        self,
        workflow: WorkflowDefinition,
        task: WorkflowTask,
        context: WorkflowContext,
        execution: WorkflowExecution
    ):
        """Execute multiple tasks in parallel"""
        parallel_tasks = []
        
        for next_task_id in task.next_tasks:
            parallel_tasks.append(
                self._execute_task(workflow, next_task_id, context, execution)
            )
        
        # Clear next_tasks to prevent double execution
        task.next_tasks = []
        
        # Execute all tasks in parallel
        await asyncio.gather(*parallel_tasks)
    
    async def _execute_conditional_task(
        self,
        workflow: WorkflowDefinition,
        task: WorkflowTask,
        context: WorkflowContext,
        execution: WorkflowExecution
    ):
        """Execute conditional branching"""
        if not task.condition:
            raise ValueError("Conditional task requires a condition")
        
        # Evaluate condition (simple implementation)
        condition_result = self._evaluate_condition(task.condition, context)
        
        if condition_result and len(task.next_tasks) > 0:
            # Execute first branch if condition is true
            await self._execute_task(
                workflow, task.next_tasks[0], context, execution
            )
        elif not condition_result and len(task.next_tasks) > 1:
            # Execute second branch if condition is false
            await self._execute_task(
                workflow, task.next_tasks[1], context, execution
            )
    
    async def _execute_loop_task(
        self,
        workflow: WorkflowDefinition,
        task: WorkflowTask,
        context: WorkflowContext,
        execution: WorkflowExecution
    ):
        """Execute loop task"""
        # Simple loop implementation - would be more sophisticated in production
        max_iterations = context.get("max_loop_iterations", 10)
        
        for i in range(max_iterations):
            context.set("loop_index", i)
            
            # Check loop condition
            if task.condition:
                if not self._evaluate_condition(task.condition, context):
                    break
            
            # Execute loop body (first next task)
            if task.next_tasks:
                await self._execute_task(
                    workflow, task.next_tasks[0], context, execution
                )
    
    def _evaluate_condition(self, condition: str, context: WorkflowContext) -> bool:
        """Evaluate a simple condition"""
        # Simple implementation - in production, use a proper expression evaluator
        try:
            # Replace context variables in condition
            for key, value in context.variables.items():
                condition = condition.replace(f"${{{key}}}", str(value))
            
            # Evaluate the condition
            return eval(condition, {"__builtins__": {}}, {})
        except:
            return False


# Example workflow factory
class WorkflowFactory:
    """Factory for creating common workflow patterns"""
    
    @staticmethod
    def create_approval_workflow(
        name: str,
        description: str,
        analysis_agent_id: str,
        decision_agent_id: str
    ) -> WorkflowDefinition:
        """Create a simple approval workflow"""
        
        # Define tasks
        analyze_task = WorkflowTask(
            id="analyze",
            name="Analyze Request",
            type=TaskType.SEQUENTIAL,
            agent_id=analysis_agent_id,
            input_mapping={"task": "request_data"},
            output_key="analysis_result",
            next_tasks=["decide"]
        )
        
        decide_task = WorkflowTask(
            id="decide",
            name="Make Decision",
            type=TaskType.SEQUENTIAL,
            agent_id=decision_agent_id,
            input_mapping={
                "analysis": "analysis_result",
                "criteria": "decision_criteria"
            },
            output_key="decision",
            next_tasks=["route"]
        )
        
        route_task = WorkflowTask(
            id="route",
            name="Route Based on Decision",
            type=TaskType.CONDITIONAL,
            condition="${decision.approved} == True",
            next_tasks=["approve", "reject"]
        )
        
        approve_task = WorkflowTask(
            id="approve",
            name="Process Approval",
            type=TaskType.SEQUENTIAL,
            agent_id=analysis_agent_id,
            input_mapping={"task": "Process approval actions"},
            output_key="approval_result"
        )
        
        reject_task = WorkflowTask(
            id="reject",
            name="Process Rejection",
            type=TaskType.SEQUENTIAL,
            agent_id=analysis_agent_id,
            input_mapping={"task": "Process rejection actions"},
            output_key="rejection_result"
        )
        
        return WorkflowDefinition(
            name=name,
            description=description,
            tasks=[analyze_task, decide_task, route_task, approve_task, reject_task],
            entry_task_id="analyze",
            variables={
                "decision_criteria": "Standard approval criteria"
            }
        )