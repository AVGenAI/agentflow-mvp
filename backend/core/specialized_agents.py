"""
Specialized AI Agents for various business functions
"""
from typing import Dict, Any, List
import json
import re
from datetime import datetime, timedelta
from .agent import BaseAgent, AgentConfig, AgentCapability


class CustomerServiceAgent(BaseAgent):
    """AI Agent specialized in customer service and support"""
    
    def __init__(self):
        config = AgentConfig(
            name="Customer Service Specialist",
            description="AI agent that handles customer inquiries, complaints, and provides support",
            goal="Resolve customer issues efficiently while maintaining high satisfaction",
            capabilities=[
                AgentCapability.REASONING,
                AgentCapability.DECISION_MAKING,
                AgentCapability.API_INTEGRATION
            ],
            tools=["search", "analyze_data", "api_call"],
            temperature=0.7
        )
        super().__init__(config, agent_id="customer_service_agent")
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze customer sentiment"""
        keywords = {
            "positive": ["happy", "satisfied", "excellent", "great", "thank"],
            "negative": ["angry", "frustrated", "terrible", "worst", "hate"],
            "neutral": ["okay", "fine", "alright", "average"]
        }
        
        text_lower = text.lower()
        sentiment_scores = {
            "positive": sum(1 for word in keywords["positive"] if word in text_lower),
            "negative": sum(1 for word in keywords["negative"] if word in text_lower),
            "neutral": sum(1 for word in keywords["neutral"] if word in text_lower)
        }
        
        return max(sentiment_scores, key=sentiment_scores.get)


class DataAnalystAgent(BaseAgent):
    """AI Agent specialized in data analysis and insights generation"""
    
    def __init__(self):
        config = AgentConfig(
            name="Data Analyst",
            description="AI agent that analyzes business data and generates actionable insights",
            goal="Transform raw data into meaningful insights for business decision-making",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.REASONING,
                AgentCapability.DECISION_MAKING
            ],
            tools=["calculate", "analyze_data", "search"],
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        super().__init__(config, agent_id="data_analyst_agent")
    
    def _calculate_statistics(self, data: List[float]) -> Dict[str, float]:
        """Calculate basic statistics"""
        if not data:
            return {}
        
        sorted_data = sorted(data)
        n = len(data)
        
        return {
            "mean": sum(data) / n,
            "median": sorted_data[n // 2] if n % 2 else (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2,
            "min": min(data),
            "max": max(data),
            "range": max(data) - min(data)
        }


class ComplianceOfficerAgent(BaseAgent):
    """AI Agent specialized in regulatory compliance and risk assessment"""
    
    def __init__(self):
        config = AgentConfig(
            name="Compliance Officer",
            description="AI agent that monitors regulatory compliance and identifies risks",
            goal="Ensure all business processes comply with regulations and minimize risk exposure",
            capabilities=[
                AgentCapability.REASONING,
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.DECISION_MAKING
            ],
            tools=["search", "analyze_data", "api_call"],
            temperature=0.2  # Very low temperature for consistent compliance checks
        )
        super().__init__(config, agent_id="compliance_officer_agent")
    
    def _check_compliance_rules(self, process_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check against compliance rules"""
        violations = []
        
        # Example compliance checks
        if process_data.get("data_retention_days", 0) > 365:
            violations.append({
                "rule": "GDPR Data Retention",
                "severity": "HIGH",
                "description": "Personal data retained longer than 365 days"
            })
        
        if not process_data.get("encryption_enabled", False):
            violations.append({
                "rule": "Data Security",
                "severity": "CRITICAL",
                "description": "Sensitive data transmission without encryption"
            })
        
        return violations


class HRRecruitmentAgent(BaseAgent):
    """AI Agent specialized in HR recruitment and talent acquisition"""
    
    def __init__(self):
        config = AgentConfig(
            name="HR Recruitment Specialist",
            description="AI agent that screens candidates, schedules interviews, and assists in hiring",
            goal="Identify and recruit top talent efficiently while ensuring fair evaluation",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.DECISION_MAKING,
                AgentCapability.PROCESS_AUTOMATION
            ],
            tools=["analyze_data", "search", "api_call"],
            temperature=0.5
        )
        super().__init__(config, agent_id="hr_recruitment_agent")
    
    def _score_resume(self, resume_text: str, requirements: List[str]) -> float:
        """Score resume based on requirements"""
        score = 0.0
        resume_lower = resume_text.lower()
        
        for req in requirements:
            if req.lower() in resume_lower:
                score += 1.0
        
        return (score / len(requirements)) * 100 if requirements else 0.0


class FinancialAnalystAgent(BaseAgent):
    """AI Agent specialized in financial analysis and forecasting"""
    
    def __init__(self):
        config = AgentConfig(
            name="Financial Analyst",
            description="AI agent that analyzes financial data, creates forecasts, and identifies trends",
            goal="Provide accurate financial insights and predictions to support business decisions",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.REASONING,
                AgentCapability.DECISION_MAKING
            ],
            tools=["calculate", "analyze_data", "search"],
            temperature=0.3
        )
        super().__init__(config, agent_id="financial_analyst_agent")
    
    def _calculate_financial_metrics(self, financial_data: Dict[str, float]) -> Dict[str, float]:
        """Calculate key financial metrics"""
        revenue = financial_data.get("revenue", 0)
        costs = financial_data.get("costs", 0)
        assets = financial_data.get("assets", 1)
        liabilities = financial_data.get("liabilities", 0)
        
        return {
            "gross_margin": ((revenue - costs) / revenue * 100) if revenue else 0,
            "net_margin": ((revenue - costs - financial_data.get("expenses", 0)) / revenue * 100) if revenue else 0,
            "roi": ((revenue - costs) / costs * 100) if costs else 0,
            "debt_to_asset_ratio": (liabilities / assets * 100) if assets else 0
        }


# Enhanced base agent with more sophisticated tools
class EnhancedBaseAgent(BaseAgent):
    """Enhanced base agent with additional business-specific tools"""
    
    def _search(self, query: str) -> str:
        """Enhanced search with more realistic results"""
        # Simulate searching different data sources
        search_contexts = {
            "customer": "Found 127 customer records matching criteria. Top issues: billing (45%), product quality (30%), delivery (25%)",
            "financial": "Q4 financial data shows 15% YoY growth, operating margin at 22%, cash flow positive for 8 consecutive quarters",
            "compliance": "Latest regulatory updates: GDPR fine increased to 4% of revenue, SOC2 audit required by Q2, ISO 27001 certification pending",
            "employee": "Employee satisfaction survey: 78% positive, main concerns: work-life balance (35%), career growth (28%)",
            "market": "Market analysis: Industry growing at 12% CAGR, main competitors gained 3% market share, emerging AI segment showing 45% growth"
        }
        
        for keyword, result in search_contexts.items():
            if keyword in query.lower():
                return result
        
        return f"Search results for '{query}': Found relevant information across multiple business domains"
    
    def _analyze_data(self, data: str) -> str:
        """Enhanced data analysis with pattern recognition"""
        try:
            # Try to parse as JSON for structured analysis
            if data.startswith("{") or data.startswith("["):
                parsed_data = json.loads(data)
                return self._perform_structured_analysis(parsed_data)
        except:
            pass
        
        # Perform text analysis
        return self._perform_text_analysis(data)
    
    def _perform_structured_analysis(self, data: Any) -> str:
        """Analyze structured data"""
        if isinstance(data, dict):
            insights = []
            
            # Analyze numerical fields
            numerical_fields = {k: v for k, v in data.items() if isinstance(v, (int, float))}
            if numerical_fields:
                avg_value = sum(numerical_fields.values()) / len(numerical_fields)
                insights.append(f"Average numerical value: {avg_value:.2f}")
                insights.append(f"Highest value: {max(numerical_fields.values())} in '{max(numerical_fields, key=numerical_fields.get)}'")
            
            # Analyze trends
            if "trend" in str(data).lower() or "time" in str(data).lower():
                insights.append("Time-series pattern detected: Showing upward trend with seasonal variations")
            
            return "Analysis complete: " + "; ".join(insights)
        
        elif isinstance(data, list):
            return f"Analyzed {len(data)} data points. Distribution appears normal with some outliers detected."
        
        return "Data structure analyzed successfully"
    
    def _perform_text_analysis(self, text: str) -> str:
        """Analyze text data"""
        word_count = len(text.split())
        
        # Sentiment indicators
        positive_words = ["good", "excellent", "improve", "success", "growth"]
        negative_words = ["bad", "poor", "decline", "failure", "loss"]
        
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        sentiment = "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"
        
        return f"Text analysis: {word_count} words, sentiment: {sentiment}, key themes identified"
    
    def _api_call(self, endpoint: str) -> str:
        """Enhanced API call simulation with realistic responses"""
        api_responses = {
            "crm": {"customers": 15420, "active_deals": 89, "conversion_rate": 0.23},
            "erp": {"inventory_value": 2500000, "pending_orders": 156, "fulfillment_rate": 0.94},
            "payment": {"processed_today": 1250000, "failed_transactions": 12, "avg_transaction": 340},
            "email": {"sent": 50000, "delivered": 48500, "open_rate": 0.31, "click_rate": 0.08}
        }
        
        for system, data in api_responses.items():
            if system in endpoint.lower():
                return f"API Response: {json.dumps(data, indent=2)}"
        
        return f"API call to {endpoint}: Success - Retrieved operational data"