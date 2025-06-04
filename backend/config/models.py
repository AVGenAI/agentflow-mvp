"""
Model configuration for different agents
Each agent can use a specialized model optimized for its tasks
"""

# Agent-specific model configurations using available models
AGENT_MODEL_CONFIG = {
    # Document processing and analysis
    "document_intelligence_agent": {
        "model": "qwen2.5-coder:7b-instruct",  # Available, good for structured analysis
        "temperature": 0.3,      # Lower for accuracy
        "description": "Optimized for document extraction and analysis"
    },
    
    # Customer interaction and sentiment
    "customer_service_agent": {
        "model": "llama2:latest",  # Available, good for conversational tasks
        "temperature": 0.7,        # Higher for natural responses
        "description": "Optimized for empathetic customer interactions"
    },
    
    # Data and financial analysis
    "data_analyst_agent": {
        "model": "qwen2.5-coder:7b-instruct",  # Available, excellent for structured data
        "temperature": 0.2,      # Very low for precision
        "description": "Optimized for numerical and statistical analysis"
    },
    
    # Compliance and regulations
    "compliance_officer_agent": {
        "model": "deepseek-r1:7b",   # Available, good for rule-based analysis
        "temperature": 0.1,          # Minimal creativity needed
        "description": "Optimized for regulatory compliance checking"
    },
    
    # Process automation
    "process_automation_agent": {
        "model": "llama2:latest",   # Available, fast for routine tasks
        "temperature": 0.3,         # Consistent outputs
        "description": "Optimized for speed in routine automation"
    },
    
    # Decision making and strategy
    "decision_making_agent": {
        "model": "deepseek-r1:latest",  # Available, strong reasoning capabilities
        "temperature": 0.5,             # Balanced creativity
        "description": "Optimized for complex decision analysis"
    },
    
    # HR and recruitment
    "hr_recruitment_agent": {
        "model": "llama2:latest",  # Available, good for understanding human context
        "temperature": 0.4,        # Some creativity for matching
        "description": "Optimized for resume parsing and candidate matching"
    },
    
    # Financial analysis
    "financial_analyst_agent": {
        "model": "qwen2.5-coder:7b-instruct",  # Available, excellent for financial data
        "temperature": 0.2,      # High precision needed
        "description": "Optimized for financial modeling and analysis"
    },
    
    # Quality assurance
    "quality_assurance_agent": {
        "model": "gemma3:12b",    # Available, good for pattern detection
        "temperature": 0.3,       # Consistent evaluation
        "description": "Optimized for quality checks and validation"
    }
}

# Fallback configuration if agent-specific model not found
DEFAULT_MODEL_CONFIG = {
    "model": "llama2:latest",
    "temperature": 0.5,
    "description": "Default balanced model"
}

# Model installation commands for easy setup (currently using available models)
MODEL_INSTALL_COMMANDS = [
    "# Current models in use (already available):",
    "# ollama pull llama2:latest",
    "# ollama pull deepseek-r1:latest", 
    "# ollama pull deepseek-r1:7b",
    "# ollama pull qwen2.5-coder:7b-instruct",
    "# ollama pull gemma3:12b",
    "",
    "# Optional optimized models (for better performance):",
    "ollama pull qwen2.5:14b",
    "ollama pull qwen2.5:7b", 
    "ollama pull llama3.1:8b",
    "ollama pull mistral:7b",
    "ollama pull gemma2:9b"
]