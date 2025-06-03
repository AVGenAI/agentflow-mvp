# Input Modes Guide

AgentFlow MVP now supports three different input modes for maximum flexibility:

## 1. Text Mode (Default)

The simplest way to interact with agents - just type your request in plain English.

### Examples:

**For Agents:**
```
Analyze our Q4 sales performance and identify areas for improvement

Process the invoice from Acme Corp for $5,000

Review this customer complaint and suggest a response

Generate a financial report for December 2023
```

**For Workflows:**
- Customer Complaint: "The product arrived damaged and customer service was unhelpful"
- Financial Report: "Q4 2023"
- Risk Assessment: "We're planning to launch a new AI product in healthcare"

## 2. JSON Mode

For precise control over input parameters, use JSON format.

### Examples:

**For Agents:**
```json
{
  "task": "Analyze sales data",
  "period": "Q4 2023",
  "focus_areas": ["revenue", "customer acquisition", "churn"]
}
```

**For Workflows:**
```json
{
  "complaint_text": "Product quality issues",
  "customer_id": "CUST-12345",
  "severity": "high",
  "product": "Premium Widget"
}
```

## 3. File Upload Mode

Upload documents directly for processing. Supported formats:
- **PDF** (.pdf) - Reports, invoices, contracts
- **Word** (.doc, .docx) - Documents, proposals, memos
- **PowerPoint** (.ppt, .pptx) - Presentations, slide decks
- **Text** (.txt) - Plain text files

### How it works:
1. Click the "File Upload" button
2. Select your file
3. The agent will process the document and extract relevant information

### Use Cases:

**Invoice Processing:**
- Upload PDF invoices for automatic processing
- Agent extracts amounts, vendors, dates

**Document Analysis:**
- Upload Word documents for summarization
- Agent identifies key points and recommendations

**Presentation Review:**
- Upload PowerPoint files for content extraction
- Agent analyzes slide content and structure

## Tips for Best Results

### Text Mode Tips:
- Be specific about what you want
- Include relevant context
- Use natural language

### JSON Mode Tips:
- Follow the expected structure for each agent/workflow
- Include all required fields
- Use proper JSON syntax

### File Upload Tips:
- Ensure files are not password-protected
- Keep file sizes reasonable (< 10MB recommended)
- Use clear, descriptive filenames

## Mode Selection Guide

| Use Case | Recommended Mode |
|----------|-----------------|
| Quick questions | Text |
| Simple requests | Text |
| Complex data with multiple parameters | JSON |
| Document processing | File Upload |
| Invoices, reports, presentations | File Upload |
| Precise API-like interactions | JSON |
| Natural conversation | Text |

## Examples by Agent Type

### Customer Service Agent
- **Text**: "Handle complaint about delayed shipping"
- **JSON**: `{"complaint": "Delayed shipping", "order_id": "ORD-123"}`
- **File**: Upload customer email as PDF

### Financial Analyst
- **Text**: "Analyze Q4 financial performance"
- **JSON**: `{"period": "Q4 2023", "metrics": ["revenue", "profit", "cash_flow"]}`
- **File**: Upload financial report PDF

### HR Recruitment Agent
- **Text**: "Screen candidates for Senior Developer position"
- **JSON**: `{"position": "Senior Developer", "requirements": ["Python", "5+ years"]}`
- **File**: Upload resume as Word document

## Workflow-Specific Formats

When using text mode with workflows, the system automatically converts your text into the appropriate format:

- **Complaint Workflow**: Your text becomes the complaint_text
- **Financial Workflow**: Your text becomes the reporting_period
- **Recruitment Workflow**: Your text becomes the candidate resume
- **Risk Assessment**: Your text becomes the business_context

This automatic conversion makes it easy to use workflows without memorizing JSON structures!