# AgentFlow MVP - Enterprise Agentic AI Platform

## Overview

AgentFlow MVP is an enterprise-grade Agentic AI platform that demonstrates the power of autonomous AI agents working independently and collaboratively to automate complex business processes. Built with Python/FastAPI backend and React/TypeScript frontend, it showcases how AI agents can transform traditional workflows into intelligent, self-managing systems.

## Key Features

- **7 Specialized AI Agents** - Each designed for specific business functions
- **5 Pre-built Workflows** - Multi-agent collaboration for complex processes
- **Multiple Input Modes** - Text, JSON, or file uploads (PDF, Word, PowerPoint)
- **Ollama Integration** - Use local LLMs without API keys
- **Mock Mode** - Test without any LLM configuration
- **Real-time Execution** - See agents working and collaborating
- **Formatted Output** - Markdown rendering with tables, lists, and formatting

## Table of Contents

1. [Installation](#installation)
2. [Individual Agents](#individual-agents)
3. [Multi-Agent Workflows](#multi-agent-workflows)
4. [Use Cases by Industry](#use-cases-by-industry)
5. [Input Examples](#input-examples)
6. [Architecture](#architecture)

## Installation

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/AVGenAI/agentflow-mvp.git
cd agentflow-mvp

# Start with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Using with Ollama (Recommended)

```bash
# Install and start Ollama
ollama serve

# Install optimized models for each agent type
./install_models.sh

# Use multi-model configuration
cp .env.multi-model .env
# Edit .env if needed

# Start the application
docker-compose up -d

# View agent-model configuration
cd backend && python show_agent_models.py
```

### Multi-Model Configuration

AgentFlow supports using different specialized models for each agent type:

- **Document Intelligence**: `qwen2.5:14b` - Best for document understanding
- **Customer Service**: `llama3.1:8b` - Optimized for conversational tasks  
- **Data Analysis**: `qwen2.5:14b` - Excellent for structured data
- **Compliance**: `qwen2.5:7b` - Efficient for rule-based analysis
- **Process Automation**: `mistral:7b` - Fast for routine tasks

This allows each agent to use the most appropriate model for its specific tasks, improving both performance and efficiency.

## Individual Agents

### 1. Process Automation Agent
**Purpose**: Automates repetitive business processes and workflows

**Capabilities**:
- Document processing and data extraction
- Form filling and submission automation
- Email and notification automation
- File organization and management
- Report generation

**Use Cases**:
```text
Input: "Process all invoices from this month and create a summary report"
Output: 
- Extracts invoice data
- Validates amounts and vendors
- Creates categorized summary
- Flags anomalies
- Generates formatted report
```

**Real-World Applications**:
- Invoice processing
- Order fulfillment
- Employee onboarding
- Document classification
- Data migration

### 2. Compliance Monitor Agent
**Purpose**: Ensures adherence to regulations and company policies

**Capabilities**:
- Policy violation detection
- Regulatory compliance checking
- Audit trail generation
- Risk assessment
- Compliance reporting

**Use Cases**:
```text
Input: "Check if our data handling procedures comply with GDPR requirements"
Output:
- Reviews current procedures
- Identifies compliance gaps
- Suggests remediation steps
- Provides compliance score
- Generates audit report
```

**Real-World Applications**:
- GDPR/CCPA compliance
- Financial regulations (SOX, Basel III)
- Healthcare compliance (HIPAA)
- Industry standards (ISO, PCI-DSS)
- Internal policy enforcement

### 3. Customer Service Agent
**Purpose**: Handles customer inquiries and support requests

**Capabilities**:
- Natural language understanding
- Sentiment analysis
- Issue categorization
- Solution recommendation
- Escalation management

**Use Cases**:
```text
Input: "Customer complaining about delayed shipment and requesting refund"
Output:
- Analyzes sentiment (frustrated)
- Categorizes issue (shipping delay)
- Checks order status
- Offers solutions (expedited shipping, partial refund)
- Drafts empathetic response
```

**Real-World Applications**:
- Email support automation
- Chat support
- Complaint handling
- FAQ responses
- Customer feedback analysis

### 4. Data Analysis Agent
**Purpose**: Analyzes data to extract insights and patterns

**Capabilities**:
- Statistical analysis
- Trend identification
- Anomaly detection
- Predictive analytics
- Visualization recommendations

**Use Cases**:
```text
Input: "Analyze Q4 sales data and identify top performing products"
Output:
- Sales trend analysis
- Product performance ranking
- Regional breakdown
- Customer segment analysis
- Growth recommendations
```

**Real-World Applications**:
- Sales analytics
- Financial analysis
- Market research
- Performance metrics
- Competitive analysis

### 5. Document Intelligence Agent
**Purpose**: Extracts and processes information from documents

**Capabilities**:
- Multi-format support (PDF, Word, PowerPoint)
- Information extraction
- Document summarization
- Classification
- Translation

**Use Cases**:
```text
Input: Multiple contract files
Prompt: "Extract key terms and compare liability clauses"
Output:
- Extracts contract parties
- Identifies key dates
- Compares liability terms
- Highlights differences
- Risk assessment
```

**Real-World Applications**:
- Contract analysis
- Resume screening
- Research paper summarization
- Legal document review
- Technical documentation processing

### 6. Decision Support Agent
**Purpose**: Provides data-driven recommendations for decision making

**Capabilities**:
- Multi-criteria analysis
- Risk-benefit assessment
- Scenario planning
- Impact analysis
- Recommendation ranking

**Use Cases**:
```text
Input: "Should we expand to the European market given current conditions?"
Output:
- Market analysis
- Risk assessment
- Financial projections
- Competitive landscape
- Recommended action plan
```

**Real-World Applications**:
- Strategic planning
- Investment decisions
- Vendor selection
- Product launch decisions
- Resource allocation

### 7. Quality Assurance Agent
**Purpose**: Ensures quality standards and identifies defects

**Capabilities**:
- Quality metrics tracking
- Defect detection
- Process improvement
- Root cause analysis
- Quality reporting

**Use Cases**:
```text
Input: "Review customer feedback and identify quality issues"
Output:
- Categorizes feedback
- Identifies recurring issues
- Traces to root causes
- Suggests improvements
- Quality score trends
```

**Real-World Applications**:
- Product quality control
- Service quality monitoring
- Code review
- Content quality assurance
- Process optimization

## Multi-Agent Workflows

### 1. Customer Complaint Resolution Workflow
**Agents**: Customer Service → Data Analysis → Decision Support → Process Automation

**Process Flow**:
1. Customer Service Agent analyzes complaint sentiment and categorizes issue
2. Data Analysis Agent checks customer history and similar cases
3. Decision Support Agent recommends resolution options
4. Process Automation Agent executes resolution and sends communication

**Example Use Case**:
```text
Input: "Premium customer received damaged product, very upset, threatening to cancel subscription"
Output:
- Sentiment: Highly negative, churn risk
- Customer value: $50K annual, 5-year customer
- Recommended resolution: Full refund + 20% discount next order
- Automated: Refund processed, apology email sent, manager notified
```

### 2. Intelligent Document Approval Workflow
**Agents**: Document Intelligence → Compliance Monitor → Decision Support → Process Automation

**Process Flow**:
1. Document Intelligence extracts key information
2. Compliance Monitor checks against policies
3. Decision Support evaluates approval criteria
4. Process Automation routes to approvers or auto-approves

**Example Use Case**:
```text
Input: Purchase request for $25,000 software license
Output:
- Extracted: Vendor, amount, department, justification
- Compliance: Within budget, approved vendor
- Decision: Auto-approve (under $30K threshold)
- Action: Approved, PO generated, notifications sent
```

### 3. Financial Reporting Workflow
**Agents**: Data Analysis → Compliance Monitor → Document Intelligence → Quality Assurance

**Process Flow**:
1. Data Analysis aggregates financial metrics
2. Compliance Monitor ensures regulatory compliance
3. Document Intelligence generates formatted reports
4. Quality Assurance validates accuracy

**Example Use Case**:
```text
Input: "Generate Q4 financial report for board meeting"
Output:
- Revenue: $12.5M (+15% YoY)
- Compliance: SOX compliant, audit-ready
- Report: 25-page formatted document
- Quality: All figures verified, no discrepancies
```

### 4. Recruitment Screening Workflow
**Agents**: Document Intelligence → Data Analysis → Decision Support → Process Automation

**Process Flow**:
1. Document Intelligence extracts resume information
2. Data Analysis scores candidates against requirements
3. Decision Support ranks and recommends
4. Process Automation schedules interviews

**Example Use Case**:
```text
Input: 50 resumes for Senior Developer position
Output:
- Parsed: Skills, experience, education from all resumes
- Scored: Top 10 candidates identified
- Recommended: 5 for immediate interviews
- Automated: Interview invites sent, calendars checked
```

### 5. Risk Assessment Workflow
**Agents**: Data Analysis → Compliance Monitor → Decision Support → Quality Assurance

**Process Flow**:
1. Data Analysis identifies risk factors
2. Compliance Monitor checks regulatory implications
3. Decision Support evaluates mitigation strategies
4. Quality Assurance validates assessment

**Example Use Case**:
```text
Input: "Assess risks for new product launch in healthcare sector"
Output:
- Risks: Regulatory (HIGH), Technical (MEDIUM), Market (LOW)
- Compliance: FDA approval needed, HIPAA considerations
- Mitigation: Phased launch, additional testing
- Confidence: 85% accuracy based on similar assessments
```

## Use Cases by Industry

### Financial Services
- **Loan Processing**: Automate application review, risk assessment, approval
- **Fraud Detection**: Real-time transaction monitoring and anomaly detection
- **Regulatory Reporting**: Automated compliance reports for multiple jurisdictions
- **Customer Onboarding**: KYC/AML checks, document verification, account setup

### Healthcare
- **Patient Record Analysis**: Extract insights from medical records
- **Insurance Claims**: Automate claim review and approval
- **Clinical Trial Management**: Patient matching, protocol compliance
- **Medical Document Processing**: Summarize research papers, clinical notes

### Retail & E-commerce
- **Inventory Management**: Demand forecasting, reorder automation
- **Customer Support**: Handle returns, complaints, product inquiries
- **Price Optimization**: Competitive analysis, dynamic pricing
- **Product Description**: Generate and optimize product content

### Manufacturing
- **Quality Control**: Defect detection, root cause analysis
- **Supply Chain**: Vendor management, order optimization
- **Maintenance**: Predictive maintenance scheduling
- **Compliance**: Safety regulations, environmental standards

### Legal
- **Contract Review**: Extract terms, identify risks, compare versions
- **Due Diligence**: Automated document review and analysis
- **Compliance Monitoring**: Policy updates, regulatory changes
- **Case Research**: Summarize precedents, extract relevant citations

## Input Examples

### Text Mode
```text
"Analyze our customer support tickets from last month and identify the top 3 issues"
```

### JSON Mode
```json
{
  "task": "Process invoice",
  "invoice_data": {
    "vendor": "Acme Corp",
    "amount": 5000,
    "due_date": "2024-12-31"
  },
  "actions": ["validate", "approve", "schedule_payment"]
}
```

### Multi-File Mode
Upload multiple documents and provide instructions:
```text
Files: contract_v1.pdf, contract_v2.pdf, contract_final.pdf
Prompt: "Compare these contract versions and highlight all changes in liability and payment terms"
```

## Architecture

### Technology Stack
- **Backend**: Python 3.11, FastAPI, LangChain
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **LLM Options**: OpenAI, Ollama (local), Mock mode

### Key Components
1. **Agent Framework**: Extensible base agent class with LangChain integration
2. **Workflow Engine**: Orchestrates multi-agent collaboration
3. **Document Processor**: Handles multiple file formats
4. **API Layer**: RESTful API with WebSocket support for real-time updates
5. **UI Components**: Responsive design with markdown rendering

### Deployment Options
- **Docker Compose**: Full stack deployment
- **Kubernetes**: Scalable enterprise deployment
- **Cloud**: AWS, Azure, GCP ready
- **On-Premise**: Full data control with Ollama

## Getting Started

1. **Choose your LLM**:
   - Ollama (recommended for local/private deployment)
   - OpenAI (for maximum capability)
   - Mock mode (for testing)

2. **Start with Examples**:
   - Use the quick example buttons to see agents in action
   - Try uploading documents for analysis
   - Create custom workflows for your use cases

3. **Customize for Your Needs**:
   - Add new agents for specific tasks
   - Create custom workflows
   - Integrate with your existing systems

## Support

For issues, feature requests, or contributions:
- GitHub: https://github.com/AVGenAI/agentflow-mvp
- Documentation: See `/docs` folder
- API Reference: http://localhost:8000/docs (when running)

---

AgentFlow MVP demonstrates the future of business automation where AI agents work autonomously to handle complex tasks, make intelligent decisions, and continuously improve processes. Start exploring the possibilities today!