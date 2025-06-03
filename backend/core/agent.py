"""
Core Agent class for AgentFlow MVP
"""
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import uuid
import asyncio
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class AgentCapability(str, Enum):
    REASONING = "reasoning"
    DATA_ANALYSIS = "data_analysis"
    API_INTEGRATION = "api_integration"
    DECISION_MAKING = "decision_making"
    PROCESS_AUTOMATION = "process_automation"


class AgentConfig(BaseModel):
    """Configuration for an AI Agent"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    goal: str = Field(..., description="Agent's primary goal")
    capabilities: List[AgentCapability] = Field(default_factory=list)
    max_iterations: int = Field(default=10, description="Maximum execution iterations")
    temperature: float = Field(default=0.7, description="LLM temperature")
    model_name: Optional[str] = Field(default="gpt-4-turbo-preview")
    tools: List[str] = Field(default_factory=list, description="Available tool names")
    memory_enabled: bool = Field(default=True)
    

class AgentExecution(BaseModel):
    """Represents a single agent execution"""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent:
    """Base class for all AI agents"""
    
    def __init__(self, config: AgentConfig):
        self.id = str(uuid.uuid4())
        self.config = config
        self.status = AgentStatus.IDLE
        self.llm = None
        self.tools = []
        self.memory = None
        self.executor = None
        self._setup_agent()
    
    def _setup_agent(self):
        """Initialize the agent with LLM and tools"""
        # Initialize LLM
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print(f"WARNING: OPENAI_API_KEY not set. Agent {self.config.name} will run in mock mode.")
            self.llm = None  # Will use mock responses
        else:
            self.llm = ChatOpenAI(
                model=self.config.model_name if self.config.model_name else "gpt-4-turbo-preview",
                temperature=self.config.temperature,
                openai_api_key=api_key
            )
        
        # Setup memory if enabled
        if self.config.memory_enabled:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        
        # Setup tools
        self._setup_tools()
        
        # Create agent executor
        self._create_executor()
    
    def _setup_tools(self):
        """Setup available tools for the agent"""
        # Define basic tools
        available_tools = {
            "calculate": Tool(
                name="Calculator",
                func=self._calculate,
                description="Perform mathematical calculations"
            ),
            "search": Tool(
                name="Search",
                func=self._search,
                description="Search for information"
            ),
            "api_call": Tool(
                name="API Call",
                func=self._api_call,
                description="Make external API calls"
            ),
            "analyze_data": Tool(
                name="Data Analyzer",
                func=self._analyze_data,
                description="Analyze and process data"
            )
        }
        
        # Add configured tools
        self.tools = [available_tools[tool_name] 
                     for tool_name in self.config.tools 
                     if tool_name in available_tools]
    
    def _create_executor(self):
        """Create the agent executor with tools and prompt"""
        if not self.llm:
            # Mock mode - no executor needed
            self.executor = None
            return
            
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are {self.config.name}, an AI agent with the following attributes:
            
Description: {self.config.description}
Goal: {self.config.goal}
Capabilities: {', '.join(self.config.capabilities)}

Work autonomously to achieve your goal. Be proactive and make decisions based on the context.
Always explain your reasoning before taking actions."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=self.config.max_iterations,
            handle_parsing_errors=True
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentExecution:
        """Execute the agent with given input"""
        execution = AgentExecution(
            agent_id=self.id,
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        
        try:
            execution.status = AgentStatus.RUNNING
            self.status = AgentStatus.RUNNING
            
            # Format input
            formatted_input = self._format_input(input_data)
            
            if self.executor:
                # Run agent with LLM
                result = await asyncio.to_thread(
                    self.executor.invoke,
                    {"input": formatted_input}
                )
                
                # Process output
                execution.output_data = {
                    "result": result.get("output", ""),
                    "steps": self._extract_steps(result),
                    "final_answer": result.get("output", "")
                }
            else:
                # Mock mode - generate mock response
                execution.output_data = self._generate_mock_response(formatted_input)
            
            execution.status = AgentStatus.COMPLETED
            self.status = AgentStatus.IDLE
            
        except Exception as e:
            execution.status = AgentStatus.FAILED
            execution.errors.append(str(e))
            self.status = AgentStatus.IDLE
        
        finally:
            execution.completed_at = datetime.utcnow()
            execution.metrics["duration_seconds"] = (
                execution.completed_at - execution.started_at
            ).total_seconds()
        
        return execution
    
    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """Format input data for the agent"""
        if "task" in input_data:
            task = input_data["task"]
            # If file content is provided, append it to the task
            if "file_content" in input_data:
                task += f"\n\nFile Content: {input_data['file_content'][:500]}..."  # Limit content for mock mode
            return task
        elif "question" in input_data:
            return input_data["question"]
        else:
            return str(input_data)
    
    def _extract_steps(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract execution steps from result"""
        steps = []
        if "intermediate_steps" in result:
            for i, (action, observation) in enumerate(result["intermediate_steps"]):
                steps.append({
                    "step": i + 1,
                    "action": str(action),
                    "observation": str(observation)
                })
        return steps
    
    # Tool implementations
    def _calculate(self, expression: str) -> str:
        """Simple calculator tool"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error in calculation: {str(e)}"
    
    def _search(self, query: str) -> str:
        """Mock search tool"""
        # In real implementation, this would search actual data sources
        return f"Search results for '{query}': Found relevant information about business processes and automation."
    
    def _api_call(self, endpoint: str) -> str:
        """Mock API call tool"""
        # In real implementation, this would make actual API calls
        return f"API call to {endpoint}: Success - Retrieved data"
    
    def _analyze_data(self, data: str) -> str:
        """Mock data analysis tool"""
        # In real implementation, this would perform actual analysis
        return f"Data analysis complete: Identified patterns and insights in the provided data."
    
    def _generate_mock_response(self, input_text: str) -> Dict[str, Any]:
        """Generate mock response when no LLM is available"""
        agent_name = self.config.name
        
        # Check if this is a file processing request
        if "[File:" in input_text or "file:" in input_text.lower():
            if ".pdf" in input_text.lower():
                response = f"[{agent_name}] PDF document processed successfully. Extracted key information from all pages. Document appears to be well-structured with clear sections."
            elif ".doc" in input_text.lower() or ".docx" in input_text.lower():
                response = f"[{agent_name}] Word document analyzed. Found multiple sections with important content. Document formatting preserved and content extracted."
            elif ".ppt" in input_text.lower() or ".pptx" in input_text.lower():
                response = f"[{agent_name}] PowerPoint presentation processed. Analyzed slides and extracted key points from each slide. Presentation structure identified."
            else:
                response = f"[{agent_name}] File processed successfully. Content extracted and analyzed. Ready for further processing."
        # Generate context-aware mock responses
        elif "invoice" in input_text.lower():
            response = f"[{agent_name}] Processed invoice successfully. Amount verified, vendor validated, and payment scheduled."
        elif "complaint" in input_text.lower():
            response = f"[{agent_name}] Analyzed customer complaint. Sentiment: negative. Priority: high. Recommended action: personal follow-up with compensation offer."
        elif "financial" in input_text.lower():
            response = f"[{agent_name}] Financial analysis complete. Revenue up 15% YoY, expenses controlled, cash flow positive. Recommend continued investment in growth areas."
        elif "candidate" in input_text.lower() or "resume" in input_text.lower():
            response = f"[{agent_name}] Screened candidates. Top 3 candidates identified based on skills match and experience. Interview schedule proposed for next week."
        elif "risk" in input_text.lower():
            response = f"[{agent_name}] Risk assessment complete. Identified 3 high-priority risks, 5 medium risks. Mitigation strategies developed for all critical areas."
        elif "approval" in input_text.lower():
            response = f"[{agent_name}] Request analyzed. Based on amount and department budget, recommendation: APPROVED with conditions."
        else:
            response = f"[{agent_name}] Task completed successfully. Analysis performed and recommendations provided based on the input data."
        
        return {
            "result": response,
            "steps": [
                {"step": 1, "action": "Analyzed input", "observation": "Input data processed"},
                {"step": 2, "action": "Applied business logic", "observation": "Rules and criteria evaluated"},
                {"step": 3, "action": "Generated response", "observation": "Recommendations formulated"}
            ],
            "final_answer": response,
            "mock_mode": True
        }


class ProcessAutomationAgent(BaseAgent):
    """Specialized agent for business process automation"""
    
    def __init__(self):
        config = AgentConfig(
            name="Process Automation Specialist",
            description="An AI agent specialized in automating business processes",
            goal="Identify and automate repetitive business processes to improve efficiency",
            capabilities=[
                AgentCapability.PROCESS_AUTOMATION,
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.API_INTEGRATION
            ],
            tools=["analyze_data", "api_call", "search"]
        )
        super().__init__(config)


class DecisionMakingAgent(BaseAgent):
    """Specialized agent for autonomous decision making"""
    
    def __init__(self):
        config = AgentConfig(
            name="Decision Maker",
            description="An AI agent that makes data-driven decisions autonomously",
            goal="Analyze data and make optimal decisions based on business rules and objectives",
            capabilities=[
                AgentCapability.DECISION_MAKING,
                AgentCapability.REASONING,
                AgentCapability.DATA_ANALYSIS
            ],
            tools=["calculate", "analyze_data", "search"]
        )
        super().__init__(config)