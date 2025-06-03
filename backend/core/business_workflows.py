"""
Real-world business workflow templates
"""
from .workflow import WorkflowDefinition, WorkflowTask, TaskType


class BusinessWorkflowFactory:
    """Factory for creating real-world business workflows"""
    
    @staticmethod
    def create_customer_complaint_workflow(
        customer_service_agent_id: str,
        data_analyst_agent_id: str,
        compliance_agent_id: str
    ) -> WorkflowDefinition:
        """Create workflow for handling customer complaints"""
        
        # Task 1: Analyze complaint
        analyze_complaint = WorkflowTask(
            id="analyze_complaint",
            name="Analyze Customer Complaint",
            type=TaskType.SEQUENTIAL,
            agent_id=customer_service_agent_id,
            input_mapping={"task": "complaint_text"},
            output_key="complaint_analysis",
            next_tasks=["check_compliance"]
        )
        
        # Task 2: Check compliance implications
        check_compliance = WorkflowTask(
            id="check_compliance",
            name="Check Compliance Issues",
            type=TaskType.SEQUENTIAL,
            agent_id=compliance_agent_id,
            input_mapping={
                "task": "Check if complaint involves regulatory issues",
                "complaint": "complaint_analysis"
            },
            output_key="compliance_check",
            next_tasks=["analyze_patterns"]
        )
        
        # Task 3: Analyze patterns
        analyze_patterns = WorkflowTask(
            id="analyze_patterns",
            name="Analyze Complaint Patterns",
            type=TaskType.SEQUENTIAL,
            agent_id=data_analyst_agent_id,
            input_mapping={
                "task": "Analyze if this is part of a larger pattern",
                "current_complaint": "complaint_analysis"
            },
            output_key="pattern_analysis",
            next_tasks=["route_response"]
        )
        
        # Task 4: Route based on severity
        route_response = WorkflowTask(
            id="route_response",
            name="Route Response Based on Severity",
            type=TaskType.CONDITIONAL,
            condition="${compliance_check.severity} == 'high'",
            next_tasks=["escalate_response", "standard_response"]
        )
        
        # Task 5a: Escalated response
        escalate_response = WorkflowTask(
            id="escalate_response",
            name="Generate Escalated Response",
            type=TaskType.SEQUENTIAL,
            agent_id=customer_service_agent_id,
            input_mapping={
                "task": "Generate high-priority response with compensation offer",
                "analysis": "complaint_analysis",
                "compliance": "compliance_check"
            },
            output_key="response"
        )
        
        # Task 5b: Standard response
        standard_response = WorkflowTask(
            id="standard_response",
            name="Generate Standard Response",
            type=TaskType.SEQUENTIAL,
            agent_id=customer_service_agent_id,
            input_mapping={
                "task": "Generate standard customer response",
                "analysis": "complaint_analysis"
            },
            output_key="response"
        )
        
        return WorkflowDefinition(
            name="Customer Complaint Resolution",
            description="End-to-end workflow for analyzing and resolving customer complaints",
            tasks=[
                analyze_complaint, check_compliance, analyze_patterns,
                route_response, escalate_response, standard_response
            ],
            entry_task_id="analyze_complaint",
            variables={
                "response_time_sla": "24 hours",
                "escalation_threshold": "high"
            }
        )
    
    @staticmethod
    def create_financial_reporting_workflow(
        financial_analyst_id: str,
        data_analyst_id: str,
        compliance_officer_id: str
    ) -> WorkflowDefinition:
        """Create workflow for monthly financial reporting"""
        
        # Task 1: Gather financial data
        gather_data = WorkflowTask(
            id="gather_data",
            name="Gather Financial Data",
            type=TaskType.SEQUENTIAL,
            agent_id=financial_analyst_id,
            input_mapping={"task": "reporting_period"},
            output_key="raw_financial_data",
            next_tasks=["parallel_analysis"]
        )
        
        # Task 2: Parallel analysis
        parallel_analysis = WorkflowTask(
            id="parallel_analysis",
            name="Run Parallel Analysis",
            type=TaskType.PARALLEL,
            next_tasks=["analyze_trends", "check_compliance", "calculate_metrics"]
        )
        
        # Task 3a: Analyze trends
        analyze_trends = WorkflowTask(
            id="analyze_trends",
            name="Analyze Financial Trends",
            type=TaskType.SEQUENTIAL,
            agent_id=data_analyst_id,
            input_mapping={
                "task": "Analyze YoY and QoQ trends",
                "data": "raw_financial_data"
            },
            output_key="trend_analysis"
        )
        
        # Task 3b: Check compliance
        check_compliance = WorkflowTask(
            id="check_compliance",
            name="Verify Financial Compliance",
            type=TaskType.SEQUENTIAL,
            agent_id=compliance_officer_id,
            input_mapping={
                "task": "Check financial reporting compliance",
                "data": "raw_financial_data"
            },
            output_key="compliance_report"
        )
        
        # Task 3c: Calculate metrics
        calculate_metrics = WorkflowTask(
            id="calculate_metrics",
            name="Calculate Key Financial Metrics",
            type=TaskType.SEQUENTIAL,
            agent_id=financial_analyst_id,
            input_mapping={
                "task": "Calculate KPIs and financial ratios",
                "data": "raw_financial_data"
            },
            output_key="financial_metrics",
            next_tasks=["generate_report"]
        )
        
        # Task 4: Generate final report
        generate_report = WorkflowTask(
            id="generate_report",
            name="Generate Financial Report",
            type=TaskType.SEQUENTIAL,
            agent_id=financial_analyst_id,
            input_mapping={
                "task": "Generate comprehensive financial report",
                "trends": "trend_analysis",
                "compliance": "compliance_report",
                "metrics": "financial_metrics"
            },
            output_key="final_report"
        )
        
        return WorkflowDefinition(
            name="Monthly Financial Reporting",
            description="Automated workflow for generating comprehensive financial reports",
            tasks=[
                gather_data, parallel_analysis, analyze_trends,
                check_compliance, calculate_metrics, generate_report
            ],
            entry_task_id="gather_data",
            variables={
                "report_format": "executive_summary",
                "include_forecasts": True
            }
        )
    
    @staticmethod
    def create_recruitment_workflow(
        hr_agent_id: str,
        data_analyst_id: str,
        decision_agent_id: str
    ) -> WorkflowDefinition:
        """Create workflow for candidate recruitment process"""
        
        # Task 1: Screen resumes
        screen_resumes = WorkflowTask(
            id="screen_resumes",
            name="Initial Resume Screening",
            type=TaskType.SEQUENTIAL,
            agent_id=hr_agent_id,
            input_mapping={
                "task": "Screen resumes against job requirements",
                "resumes": "candidate_resumes",
                "requirements": "job_requirements"
            },
            output_key="screening_results",
            next_tasks=["analyze_candidates"]
        )
        
        # Task 2: Analyze candidate pool
        analyze_candidates = WorkflowTask(
            id="analyze_candidates",
            name="Analyze Candidate Pool",
            type=TaskType.SEQUENTIAL,
            agent_id=data_analyst_id,
            input_mapping={
                "task": "Analyze diversity, skills distribution, and candidate quality",
                "candidates": "screening_results"
            },
            output_key="candidate_analysis",
            next_tasks=["rank_candidates"]
        )
        
        # Task 3: Rank and decide
        rank_candidates = WorkflowTask(
            id="rank_candidates",
            name="Rank and Select Top Candidates",
            type=TaskType.SEQUENTIAL,
            agent_id=decision_agent_id,
            input_mapping={
                "task": "Rank candidates and select top 5 for interviews",
                "screening": "screening_results",
                "analysis": "candidate_analysis"
            },
            output_key="top_candidates",
            next_tasks=["schedule_interviews"]
        )
        
        # Task 4: Schedule interviews
        schedule_interviews = WorkflowTask(
            id="schedule_interviews",
            name="Schedule Interview Process",
            type=TaskType.SEQUENTIAL,
            agent_id=hr_agent_id,
            input_mapping={
                "task": "Create interview schedule and send invitations",
                "candidates": "top_candidates"
            },
            output_key="interview_schedule"
        )
        
        return WorkflowDefinition(
            name="Recruitment Pipeline",
            description="End-to-end recruitment workflow from resume screening to interview scheduling",
            tasks=[
                screen_resumes, analyze_candidates,
                rank_candidates, schedule_interviews
            ],
            entry_task_id="screen_resumes",
            variables={
                "interview_rounds": 3,
                "diversity_target": 0.4
            }
        )
    
    @staticmethod
    def create_risk_assessment_workflow(
        compliance_officer_id: str,
        data_analyst_id: str,
        financial_analyst_id: str,
        decision_agent_id: str
    ) -> WorkflowDefinition:
        """Create workflow for comprehensive risk assessment"""
        
        # Task 1: Identify risk factors
        identify_risks = WorkflowTask(
            id="identify_risks",
            name="Identify Risk Factors",
            type=TaskType.SEQUENTIAL,
            agent_id=compliance_officer_id,
            input_mapping={
                "task": "Identify all potential risk factors",
                "context": "business_context"
            },
            output_key="risk_factors",
            next_tasks=["parallel_assessment"]
        )
        
        # Task 2: Parallel risk assessment
        parallel_assessment = WorkflowTask(
            id="parallel_assessment",
            name="Parallel Risk Assessment",
            type=TaskType.PARALLEL,
            next_tasks=["analyze_operational", "analyze_financial", "analyze_compliance"]
        )
        
        # Task 3a: Operational risk
        analyze_operational = WorkflowTask(
            id="analyze_operational",
            name="Analyze Operational Risks",
            type=TaskType.SEQUENTIAL,
            agent_id=data_analyst_id,
            input_mapping={
                "task": "Analyze operational risk exposure",
                "risks": "risk_factors"
            },
            output_key="operational_risk_analysis"
        )
        
        # Task 3b: Financial risk
        analyze_financial = WorkflowTask(
            id="analyze_financial",
            name="Analyze Financial Risks",
            type=TaskType.SEQUENTIAL,
            agent_id=financial_analyst_id,
            input_mapping={
                "task": "Analyze financial risk exposure and impact",
                "risks": "risk_factors"
            },
            output_key="financial_risk_analysis"
        )
        
        # Task 3c: Compliance risk
        analyze_compliance = WorkflowTask(
            id="analyze_compliance",
            name="Analyze Compliance Risks",
            type=TaskType.SEQUENTIAL,
            agent_id=compliance_officer_id,
            input_mapping={
                "task": "Analyze regulatory and compliance risks",
                "risks": "risk_factors"
            },
            output_key="compliance_risk_analysis",
            next_tasks=["create_mitigation"]
        )
        
        # Task 4: Create mitigation strategy
        create_mitigation = WorkflowTask(
            id="create_mitigation",
            name="Create Risk Mitigation Strategy",
            type=TaskType.SEQUENTIAL,
            agent_id=decision_agent_id,
            input_mapping={
                "task": "Create comprehensive risk mitigation strategy",
                "operational": "operational_risk_analysis",
                "financial": "financial_risk_analysis",
                "compliance": "compliance_risk_analysis"
            },
            output_key="mitigation_strategy"
        )
        
        return WorkflowDefinition(
            name="Enterprise Risk Assessment",
            description="Comprehensive risk assessment and mitigation planning workflow",
            tasks=[
                identify_risks, parallel_assessment, analyze_operational,
                analyze_financial, analyze_compliance, create_mitigation
            ],
            entry_task_id="identify_risks",
            variables={
                "risk_threshold": "medium",
                "assessment_scope": "enterprise-wide"
            }
        )