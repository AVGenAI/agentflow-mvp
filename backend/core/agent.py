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

# Import model configurations
try:
    from config.models import AGENT_MODEL_CONFIG, DEFAULT_MODEL_CONFIG
except ImportError:
    AGENT_MODEL_CONFIG = {}
    DEFAULT_MODEL_CONFIG = {"model": "llama2:latest", "temperature": 0.5}

# Import memory manager
try:
    from core.memory_manager import MemoryManager
except ImportError:
    MemoryManager = None


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
        self.persistent_memory = None
        
        self._setup_agent()
    
    def _setup_agent(self):
        """Initialize the agent with LLM and tools"""
        # Initialize LLM
        import os
        llm_provider = os.getenv("LLM_PROVIDER", "mock").lower()
        
        if llm_provider == "ollama":
            try:
                from langchain_community.chat_models import ChatOllama
                
                # Get agent-specific model configuration
                agent_config = AGENT_MODEL_CONFIG.get(self.id, DEFAULT_MODEL_CONFIG)
                
                # Override with environment variable if set
                ollama_model = os.getenv("OLLAMA_MODEL", agent_config["model"])
                ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                
                # Use agent-specific temperature unless overridden
                temperature = agent_config.get("temperature", self.config.temperature)
                
                print(f"Initializing {self.config.name} with Ollama model: {ollama_model} (temp: {temperature})")
                print(f"  Model optimized for: {agent_config.get('description', 'General purpose')}")
                
                self.llm = ChatOllama(
                    model=ollama_model,
                    temperature=temperature,
                    base_url=ollama_base_url
                )
            except Exception as e:
                print(f"ERROR: Failed to initialize Ollama: {e}")
                print(f"Agent {self.config.name} will run in mock mode.")
                self.llm = None
        elif llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm = ChatOpenAI(
                    model=self.config.model_name if self.config.model_name else "gpt-4-turbo-preview",
                    temperature=self.config.temperature,
                    openai_api_key=api_key
                )
            else:
                print(f"WARNING: OPENAI_API_KEY not set. Agent {self.config.name} will run in mock mode.")
                self.llm = None
        else:
            print(f"Agent {self.config.name} running in mock mode (LLM_PROVIDER={llm_provider})")
            self.llm = None
        
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
        
        # Initialize persistent memory after agent is fully set up
        self._setup_persistent_memory()
    
    def _setup_persistent_memory(self):
        """Initialize persistent memory manager"""
        if MemoryManager:
            try:
                self.persistent_memory = MemoryManager(
                    agent_id=self.id,
                    agent_name=self.config.name
                )
                print(f"Persistent memory initialized for {self.config.name} (ID: {self.id})")
            except Exception as e:
                print(f"Warning: Could not initialize persistent memory: {e}")
    
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
        
        # Start a new conversation in persistent memory
        if self.persistent_memory:
            workflow_id = input_data.get('workflow_id')
            metadata = {
                'input_type': 'file' if 'files' in input_data else 'text',
                'file_count': input_data.get('file_count', 0)
            }
            self.persistent_memory.start_conversation(workflow_id=workflow_id, metadata=metadata)
        
        try:
            execution.status = AgentStatus.RUNNING
            self.status = AgentStatus.RUNNING
            
            # Format input
            formatted_input = self._format_input(input_data)
            
            # Store user message in persistent memory
            if self.persistent_memory:
                self.persistent_memory.add_message(
                    role="human",
                    content=formatted_input,
                    metadata=input_data
                )
            
            if self.executor:
                # Track AI processing time
                ai_start_time = datetime.utcnow()
                
                # Run agent with LLM
                result = await asyncio.to_thread(
                    self.executor.invoke,
                    {"input": formatted_input}
                )
                
                # Calculate AI processing duration
                ai_end_time = datetime.utcnow()
                ai_processing_duration = (ai_end_time - ai_start_time).total_seconds()
                
                # Process output
                execution.output_data = {
                    "result": result.get("output", ""),
                    "steps": self._extract_steps(result),
                    "final_answer": result.get("output", "")
                }
                
                # Store AI response in persistent memory
                if self.persistent_memory:
                    model_info = None
                    if hasattr(self, 'llm') and self.llm:
                        model_info = getattr(self.llm, 'model', 'unknown')
                    
                    self.persistent_memory.add_message(
                        role="ai",
                        content=result.get("output", ""),
                        metadata={"steps": self._extract_steps(result)},
                        model_used=model_info,
                        temperature=self.config.temperature,
                        processing_duration=ai_processing_duration
                    )
            else:
                # Mock mode - generate mock response with simulated processing time
                mock_start_time = datetime.utcnow()
                execution.output_data = self._generate_mock_response(formatted_input)
                mock_end_time = datetime.utcnow()
                mock_processing_duration = (mock_end_time - mock_start_time).total_seconds()
                
                # Store mock response in persistent memory
                if self.persistent_memory:
                    self.persistent_memory.add_message(
                        role="ai",
                        content=execution.output_data.get("result", ""),
                        metadata={"mock_mode": True},
                        model_used="mock",
                        temperature=0.5,
                        processing_duration=mock_processing_duration
                    )
            
            execution.status = AgentStatus.COMPLETED
            self.status = AgentStatus.IDLE
            
            # Add conversation history to the execution output BEFORE ending conversation
            if self.persistent_memory:
                # Get current conversation
                current_conversation = self.persistent_memory.get_conversation_history()
                
                # Get recent conversations for this agent (last 10 conversations)
                recent_conversations = self.persistent_memory.get_recent_conversations(limit=10)
                
                # Build complete history with conversation boundaries
                complete_history = []
                
                # Add previous conversations
                for conv in reversed(recent_conversations[1:]):  # Skip current conversation (first one)
                    conv_messages = self.persistent_memory.get_conversation_history(
                        conversation_id=conv['id'], limit=100
                    )
                    if conv_messages:
                        # Add conversation separator
                        complete_history.append({
                            "role": "system",
                            "content": f"--- Previous Conversation (Started: {conv['started_at']}) ---",
                            "timestamp": conv['started_at'],
                            "conversation_id": conv['id'],
                            "is_separator": True
                        })
                        complete_history.extend(conv_messages)
                
                # Add current conversation separator
                if current_conversation:
                    complete_history.append({
                        "role": "system", 
                        "content": "--- Current Conversation ---",
                        "timestamp": current_conversation[0]['timestamp'] if current_conversation else None,
                        "conversation_id": self.persistent_memory.current_conversation_id,
                        "is_separator": True
                    })
                    complete_history.extend(current_conversation)
                
                execution.output_data["conversation_history"] = complete_history
                
                # End conversation in persistent memory
                self.persistent_memory.end_conversation(status='completed')
            
        except Exception as e:
            execution.status = AgentStatus.FAILED
            execution.errors.append(str(e))
            self.status = AgentStatus.IDLE
            
            # Store error in persistent memory
            if self.persistent_memory:
                self.persistent_memory.add_message(
                    role="system",
                    content=f"Error: {str(e)}",
                    metadata={"error": True, "error_type": type(e).__name__}
                )
                self.persistent_memory.end_conversation(status='failed')
        
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
            
            # Handle new multi-file format
            if "files" in input_data and isinstance(input_data["files"], list):
                file_count = input_data.get("file_count", len(input_data["files"]))
                task += f"\n\n[Processing {file_count} files]"
                
                for i, file_info in enumerate(input_data["files"]):
                    task += f"\n\nFile {i+1}: {file_info.get('name', 'Unknown')}"
                    task += f"\nType: {file_info.get('type', 'Unknown')}"
                    if 'content' in file_info:
                        content = file_info['content']
                        # Check if content is JSON-encoded binary data
                        try:
                            import json
                            content_data = json.loads(content)
                            if isinstance(content_data, dict) and content_data.get('type') == 'binary':
                                task += f"\nFormat: {content_data.get('format', 'Unknown')}"
                                task += f"\nSize: {content_data.get('size', 0)} bytes"
                                # In a real implementation, we would decode base64 and extract text
                                # For now, indicate that we received the binary file
                                task += f"\n[Binary file received - would extract text content in production]"
                            else:
                                # Regular text content
                                content_preview = content[:500] if len(content) > 500 else content
                                task += f"\nContent: {content_preview}..."
                        except:
                            # Not JSON, treat as regular text
                            content_preview = content[:500] if len(content) > 500 else content
                            task += f"\nContent: {content_preview}..."
            
            # Handle legacy single file format
            elif "file_content" in input_data:
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
        if "[Processing" in input_text and "files]" in input_text:
            # Extract file count from the formatted input
            import re
            match = re.search(r'\[Processing (\d+) files\]', input_text)
            file_count = int(match.group(1)) if match else 1
            
            response = f"""# Multi-File Processing Report

## Agent: {agent_name}

### 📁 File Processing Summary
- **Status**: ✅ Successfully processed all {file_count} files
- **Files Analyzed**: {file_count}
- **Processing Time**: 2.3 seconds

### File Analysis Results

"""
            # Extract file information from the input text
            file_sections = input_text.split("\n\nFile ")
            for i, section in enumerate(file_sections[1:], 1):  # Skip the first split which is before "File 1"
                lines = section.split("\n")
                if lines:
                    file_name = lines[0].split(": ", 1)[1] if ": " in lines[0] else f"File {i}"
                    file_type = "Unknown"
                    for line in lines:
                        if line.startswith("Type: "):
                            file_type = line.split("Type: ", 1)[1]
                            break
                    
                    response += f"""#### File {i}: {file_name}
- **Type**: {file_type}
- **Status**: ✅ Processed successfully
- **Key Findings**: Content analyzed and key information extracted

"""

            response += f"""### Consolidated Analysis
1. **Common Themes**: Identified patterns across all documents
2. **Key Differences**: Notable variations documented
3. **Recommendations**: Based on comprehensive multi-file analysis

### Next Steps
- All files have been processed and analyzed
- Results are ready for review
- Consider implementing suggested actions
"""
        elif "[File:" in input_text or "file:" in input_text.lower():
            if ".pdf" in input_text.lower():
                response = f"""# Document Processing Report

## Agent: {agent_name}

### 📄 PDF Analysis Summary
- **Status**: ✅ Successfully processed
- **Pages**: Analyzed all pages
- **Structure**: Well-organized with clear sections
- **Content**: Key information extracted

### Key Findings
1. Document appears to be professionally formatted
2. All text content has been extracted
3. Tables and charts identified
4. Ready for further analysis

### Recommendations
- Content is suitable for automated processing
- Consider implementing OCR validation for critical data
"""
            elif ".doc" in input_text.lower() or ".docx" in input_text.lower():
                response = f"""# Document Processing Report

## Agent: {agent_name}

### 📝 Word Document Analysis
- **Status**: ✅ Successfully analyzed
- **Format**: Microsoft Word (.docx)
- **Content**: Multiple sections with rich formatting

### Processing Results
1. **Text Extraction**: Complete
2. **Formatting**: Preserved
3. **Structure**: Identified headers and paragraphs
4. **Tables**: Detected and processed

### Next Steps
- Document is ready for content analysis
- Formatting elements maintained for context
"""
            elif ".ppt" in input_text.lower() or ".pptx" in input_text.lower():
                response = f"""# Presentation Analysis Report

## Agent: {agent_name}

### 🎯 PowerPoint Processing Results
- **Status**: ✅ Successfully processed
- **Slides**: All slides analyzed
- **Content**: Key points extracted from each slide

### Slide Analysis
1. **Title Slides**: Identified
2. **Content Slides**: Text and bullet points extracted
3. **Charts/Graphs**: Detected (content descriptions available)
4. **Speaker Notes**: Included if present

### Summary
- Presentation structure mapped
- Key messages identified
- Ready for content summarization
"""
            else:
                response = f"""# File Processing Complete

## Agent: {agent_name}

### ✅ Processing Status
- **File**: Successfully processed
- **Content**: Extracted and analyzed
- **Format**: Compatible with system

### Ready for next steps in the workflow.
"""
        # Generate context-aware mock responses
        elif "invoice" in input_text.lower():
            response = f"""# Invoice Processing Report

## Agent: {agent_name}

### ✅ Processing Complete
- **Status**: Successfully processed
- **Verification**: Amount and vendor validated
- **Action**: Payment scheduled

### Details
| Field | Status |
|-------|--------|
| Amount | ✅ Verified |
| Vendor | ✅ Validated |
| Payment | 🕒 Scheduled |

**Next Steps**: Payment will be processed according to standard terms.
"""
        elif "complaint" in input_text.lower():
            response = f"""# Customer Complaint Analysis

## Agent: {agent_name}

### 📊 Analysis Results
- **Sentiment**: ⚠️ Negative
- **Priority**: 🔴 High
- **Category**: Service Issue

### Recommended Actions
1. **Immediate**: Personal follow-up call
2. **Compensation**: Offer appropriate remedy
3. **Follow-up**: Schedule satisfaction check

### Risk Assessment
- **Escalation Risk**: Medium-High
- **Customer Retention**: At risk
- **Reputation Impact**: Contained with proper response
"""
        elif "financial" in input_text.lower():
            response = f"""# Financial Analysis Report

## Agent: {agent_name}

### 📈 Key Performance Indicators
- **Revenue Growth**: +15% YoY
- **Cost Control**: ✅ On target
- **Cash Flow**: 💰 Positive

### Financial Health
| Metric | Status | Change |
|--------|--------|--------|
| Revenue | Strong | +15% |
| Expenses | Controlled | Stable |
| Cash Flow | Positive | Improving |

### Strategic Recommendations
1. **Investment Areas**: Continue growth investments
2. **Risk Management**: Maintain current controls
3. **Opportunities**: Explore expansion in profitable segments
"""
        elif "candidate" in input_text.lower() or "resume" in input_text.lower():
            response = f"""# Candidate Screening Report

## Agent: {agent_name}

### 🎯 Screening Results
- **Total Candidates**: Reviewed
- **Top Candidates**: 3 identified
- **Match Score**: High compatibility

### Candidate Rankings
1. **Candidate A**: 95% match - Strong technical skills
2. **Candidate B**: 88% match - Excellent experience
3. **Candidate C**: 85% match - Good cultural fit

### Next Steps
- **Interviews**: Scheduled for next week
- **Reference Checks**: To be conducted
- **Final Selection**: Expected within 5 business days
"""
        elif "risk" in input_text.lower():
            response = f"""# Risk Assessment Report

## Agent: {agent_name}

### 🎯 Risk Analysis Overview
- **High Priority Risks**: 3 identified
- **Medium Risks**: 5 identified
- **Overall Risk Level**: Manageable

### Risk Categories
| Priority | Category | Count | Status |
|----------|----------|-------|--------|
| 🔴 High | Critical | 3 | Mitigation planned |
| 🟡 Medium | Moderate | 5 | Monitoring required |
| 🟢 Low | Minor | 2 | Acceptable |

### Mitigation Strategies
1. **Immediate Actions**: Address critical risks
2. **Monitoring**: Implement tracking systems
3. **Contingency Plans**: Develop response procedures

### Timeline
- **Action Plan**: Ready for implementation
- **Review Cycle**: Monthly assessments recommended
"""
        elif "approval" in input_text.lower():
            response = f"""# Approval Decision Report

## Agent: {agent_name}

### ✅ Decision Summary
- **Status**: **APPROVED** with conditions
- **Amount**: Within budget parameters
- **Department**: Authorized for request

### Approval Details
| Criteria | Assessment | Status |
|----------|------------|--------|
| Budget Impact | ✅ Acceptable | Approved |
| Business Case | ✅ Justified | Approved |
| Authority Level | ✅ Sufficient | Approved |

### Conditions
1. Monthly progress reporting required
2. Budget tracking must be maintained
3. Final review in 90 days

**Effective Date**: Immediate
"""
        else:
            response = f"""# Task Completion Report

## Agent: {agent_name}

### ✅ Task Status: Complete

**Analysis**: Successfully performed comprehensive analysis
**Recommendations**: Data-driven insights provided
**Quality**: High confidence in results

### Summary
- All required processing completed
- Recommendations formulated based on best practices
- Ready for implementation or further review

*This is a mock response - actual implementation would provide specific analysis based on your input.*
"""
        
        return {
            "result": response,
            "steps": [
                {"step": 1, "action": "Analyzed input", "observation": "Input data processed and validated"},
                {"step": 2, "action": "Applied business logic", "observation": "Rules, criteria, and context evaluated"},
                {"step": 3, "action": "Generated response", "observation": "Structured recommendations formulated"}
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
        # Use consistent ID for persistent memory
        self.id = "process_automation_agent"
        # Re-initialize persistent memory with the new ID
        self._setup_persistent_memory()


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
        # Use consistent ID for persistent memory
        self.id = "decision_making_agent"
        # Re-initialize persistent memory with the new ID
        self._setup_persistent_memory()