# AgentFlow MVP - Available Agents & Workflows Guide

## Available AI Agents

### 1. **Customer Service Specialist**
- **Purpose**: Handles customer inquiries, complaints, and provides support
- **Capabilities**: Sentiment analysis, issue resolution, customer communication
- **Example Use Cases**:
  - Analyzing customer complaints
  - Generating appropriate responses
  - Escalating critical issues

### 2. **Data Analyst**
- **Purpose**: Analyzes business data and generates actionable insights
- **Capabilities**: Statistical analysis, pattern recognition, trend identification
- **Example Use Cases**:
  - Analyzing sales trends
  - Identifying patterns in customer behavior
  - Creating data-driven recommendations

### 3. **Compliance Officer**
- **Purpose**: Monitors regulatory compliance and identifies risks
- **Capabilities**: Rule checking, risk assessment, compliance monitoring
- **Example Use Cases**:
  - GDPR compliance checking
  - Data security audits
  - Regulatory reporting

### 4. **HR Recruitment Specialist**
- **Purpose**: Screens candidates, schedules interviews, assists in hiring
- **Capabilities**: Resume scoring, candidate matching, interview scheduling
- **Example Use Cases**:
  - Initial resume screening
  - Candidate ranking
  - Diversity analysis

### 5. **Financial Analyst**
- **Purpose**: Analyzes financial data, creates forecasts, identifies trends
- **Capabilities**: Financial metrics calculation, trend analysis, forecasting
- **Example Use Cases**:
  - Monthly financial reporting
  - ROI calculations
  - Budget variance analysis

### 6. **Process Automation Specialist**
- **Purpose**: Automates business processes and improves efficiency
- **Capabilities**: Process analysis, workflow optimization, automation
- **Example Use Cases**:
  - Invoice processing
  - Order fulfillment
  - Data entry automation

### 7. **Decision Maker**
- **Purpose**: Makes data-driven decisions based on analysis
- **Capabilities**: Multi-criteria decision making, risk assessment, optimization
- **Example Use Cases**:
  - Approval decisions
  - Resource allocation
  - Strategic planning

## Available Workflows

### 1. **Customer Complaint Resolution**
**Flow**: Customer Service → Compliance Check → Pattern Analysis → Response Generation
- Analyzes customer complaints for sentiment and severity
- Checks for compliance implications
- Identifies patterns across complaints
- Generates appropriate responses (standard or escalated)

### 2. **Monthly Financial Reporting**
**Flow**: Data Gathering → Parallel Analysis (Trends, Compliance, Metrics) → Report Generation
- Collects financial data for the reporting period
- Performs parallel analysis:
  - Trend analysis (YoY, QoQ)
  - Compliance verification
  - KPI calculation
- Generates comprehensive financial report

### 3. **Recruitment Pipeline**
**Flow**: Resume Screening → Candidate Analysis → Ranking → Interview Scheduling
- Screens resumes against job requirements
- Analyzes candidate pool for diversity and skills
- Ranks candidates based on fit
- Schedules interviews with top candidates

### 4. **Enterprise Risk Assessment**
**Flow**: Risk Identification → Parallel Assessment (Operational, Financial, Compliance) → Mitigation Strategy
- Identifies potential risk factors
- Performs parallel risk assessment:
  - Operational risks
  - Financial risks
  - Compliance risks
- Creates comprehensive mitigation strategy

### 5. **Purchase Approval Workflow**
**Flow**: Request Analysis → Decision Making → Conditional Routing → Action
- Analyzes purchase requests
- Makes approval decisions based on criteria
- Routes to appropriate action (approve/reject)
- Processes the decision

## Example API Calls

### Execute a Single Agent
```json
POST /api/agents/execute
{
  "agent_id": "agent-uuid-here",
  "input_data": {
    "task": "Analyze customer feedback from Q4 2023 and identify top 3 issues"
  }
}
```

### Execute a Workflow
```json
POST /api/workflows/execute
{
  "workflow_id": "workflow-uuid-here",
  "input_data": {
    "complaint_text": "Product arrived damaged and support was unhelpful",
    "customer_id": "CUST-12345",
    "severity": "high"
  }
}
```

### Quick Examples

#### Customer Complaint
```json
POST /api/examples/customer-complaint
{
  "complaint": "Received wrong item twice, very frustrated",
  "customer_id": "CUST-54321",
  "severity": "high"
}
```

#### Financial Report
```json
POST /api/examples/financial-report
{
  "period": "Q4 2023",
  "include_forecast": true
}
```

#### Candidate Screening
```json
POST /api/examples/screen-candidates
{
  "resumes": ["Resume text 1", "Resume text 2"],
  "requirements": ["Python", "5+ years", "ML experience"],
  "position": "Senior Data Scientist"
}
```

#### Risk Assessment
```json
POST /api/examples/risk-assessment
{
  "context": "Expanding to new market in EU",
  "areas": ["regulatory", "financial", "operational"]
}
```

## Best Practices

1. **Agent Selection**: Choose agents based on their specialized capabilities
2. **Workflow Design**: Use parallel tasks when analyses are independent
3. **Input Data**: Provide clear, structured input for better results
4. **Error Handling**: Workflows include automatic error handling and retries
5. **Monitoring**: Check execution status and metrics for optimization

## Integration Tips

- All agents can be accessed via REST API
- Workflows can be customized by creating new workflow definitions
- Agents can be extended with custom tools and capabilities
- Real-time status updates available via execution endpoints