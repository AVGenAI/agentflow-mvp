import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  PlusIcon, 
  PlayIcon, 
  CogIcon, 
  ChartBarIcon,
  BoltIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  DocumentIcon
} from '@heroicons/react/24/outline';

const API_URL = 'http://localhost:8000/api';

interface Agent {
  id: string;
  name: string;
  description: string;
  status: string;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  task_count: number;
}

interface ExecutionResult {
  execution_id: string;
  status: string;
  output: any;
  metrics: any;
}

function App() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>('');
  const [inputData, setInputData] = useState<string>('');
  const [inputMode, setInputMode] = useState<'text' | 'json' | 'file'>('text');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [activeTab, setActiveTab] = useState<'agents' | 'workflows' | 'execute'>('agents');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchAgents();
    fetchWorkflows();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${API_URL}/agents`);
      setAgents(response.data);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await axios.get(`${API_URL}/workflows`);
      setWorkflows(response.data);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const executeAgent = async () => {
    if (!selectedAgent || (!inputData && !uploadedFile)) return;

    setLoading(true);
    try {
      let parsedInput;
      
      if (inputMode === 'json') {
        try {
          parsedInput = JSON.parse(inputData);
        } catch (e) {
          alert('Invalid JSON format. Please check your input.');
          setLoading(false);
          return;
        }
      } else if (inputMode === 'file' && uploadedFile) {
        // For file mode, read the file content
        const fileContent = await readFileContent(uploadedFile);
        parsedInput = { 
          task: `Process this file: ${uploadedFile.name}`,
          file_content: fileContent,
          file_name: uploadedFile.name,
          file_type: uploadedFile.type
        };
      } else {
        // For text mode, send as a task
        parsedInput = { task: inputData };
      }

      const response = await axios.post(`${API_URL}/agents/execute`, {
        agent_id: selectedAgent,
        input_data: parsedInput
      });
      setExecutionResult(response.data);
    } catch (error) {
      console.error('Error executing agent:', error);
      alert('Error executing agent. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const executeWorkflow = async () => {
    if (!selectedWorkflow || !inputData) return;

    setLoading(true);
    try {
      let parsedInput;
      if (inputMode === 'json') {
        try {
          parsedInput = JSON.parse(inputData);
        } catch (e) {
          alert('Invalid JSON format. Please check your input.');
          setLoading(false);
          return;
        }
      } else {
        // For text mode, parse the workflow-specific fields
        parsedInput = parseTextInputForWorkflow(selectedWorkflow, inputData);
      }

      const response = await axios.post(`${API_URL}/workflows/execute`, {
        workflow_id: selectedWorkflow,
        input_data: parsedInput
      });
      setExecutionResult(response.data);
    } catch (error) {
      console.error('Error executing workflow:', error);
      alert('Error executing workflow. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const parseTextInputForWorkflow = (workflowId: string, text: string): any => {
    // Find the workflow to determine its type
    const workflow = workflows.find(w => w.id === workflowId);
    
    if (!workflow) {
      return { task: text };
    }

    // Parse based on workflow name
    if (workflow.name.toLowerCase().includes('complaint')) {
      return { complaint_text: text, customer_id: 'CUST-001', severity: 'medium' };
    } else if (workflow.name.toLowerCase().includes('approval')) {
      return { request_data: text, criteria: 'standard' };
    } else if (workflow.name.toLowerCase().includes('financial')) {
      return { reporting_period: text, include_forecast: true };
    } else if (workflow.name.toLowerCase().includes('recruitment')) {
      return { 
        candidate_resumes: [text], 
        job_requirements: ['Experience required'],
        position: 'General Position'
      };
    } else if (workflow.name.toLowerCase().includes('risk')) {
      return { business_context: text, risk_areas: ['operational', 'financial'] };
    }
    
    // Default fallback
    return { task: text };
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint',
        'text/plain'
      ];
      
      if (allowedTypes.includes(file.type)) {
        setUploadedFile(file);
        setInputData(`File uploaded: ${file.name}`);
      } else {
        alert('Please upload a PDF, Word document, PowerPoint, or text file.');
      }
    }
  };

  const readFileContent = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result;
        if (typeof content === 'string') {
          resolve(content);
        } else {
          // For binary files, we'll just send the filename and let the backend handle it
          resolve(`[File: ${file.name}] - Binary content requires server-side processing`);
        }
      };
      reader.onerror = reject;
      
      // For text files, read as text. For others, we'll need server-side processing
      if (file.type === 'text/plain') {
        reader.readAsText(file);
      } else {
        // For now, just return file info
        resolve(`[File: ${file.name}] - Type: ${file.type} - Size: ${file.size} bytes - Requires server-side processing for content extraction`);
      }
    });
  };

  const runExample = async (type: string) => {
    setLoading(true);
    try {
      let exampleData: any;
      let endpoint: string;

      switch(type) {
        case 'invoice':
          exampleData = {
            invoice_number: "INV-2024-001",
            amount: 5000,
            vendor: "Acme Corp",
            description: "Software licenses"
          };
          endpoint = `${API_URL}/examples/process-invoice`;
          break;
        
        case 'approval':
          exampleData = {
            type: "purchase_request",
            amount: 10000,
            department: "IT",
            justification: "New server equipment",
            criteria: "standard"
          };
          endpoint = `${API_URL}/examples/approval-request`;
          break;
        
        case 'complaint':
          exampleData = {
            complaint: "I received a damaged product and the customer service was unhelpful. This is unacceptable for a premium service.",
            customer_id: "CUST-12345",
            severity: "high"
          };
          endpoint = `${API_URL}/examples/customer-complaint`;
          break;
        
        case 'financial':
          exampleData = {
            period: "Q4 2023",
            include_forecast: true
          };
          endpoint = `${API_URL}/examples/financial-report`;
          break;
        
        case 'recruitment':
          exampleData = {
            resumes: ["10 years Python experience, ML expertise", "5 years full-stack, React/Node.js"],
            requirements: ["Python", "Machine Learning", "5+ years experience"],
            position: "Senior ML Engineer"
          };
          endpoint = `${API_URL}/examples/screen-candidates`;
          break;
        
        case 'risk':
          exampleData = {
            context: "Launching new AI-powered product in healthcare sector",
            areas: ["regulatory", "technical", "financial", "reputational"]
          };
          endpoint = `${API_URL}/examples/risk-assessment`;
          break;
        
        default:
          return;
      }

      const response = await axios.post(endpoint, exampleData);
      setExecutionResult(response.data);
    } catch (error) {
      console.error('Error running example:', error);
      alert('Error running example. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <BoltIcon className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">AgentFlow MVP</h1>
            </div>
            <div className="text-sm text-gray-500">
              Enterprise Agentic AI Platform
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('agents')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'agents'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <CogIcon className="h-5 w-5 inline mr-2" />
              Agents
            </button>
            <button
              onClick={() => setActiveTab('workflows')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'workflows'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <DocumentTextIcon className="h-5 w-5 inline mr-2" />
              Workflows
            </button>
            <button
              onClick={() => setActiveTab('execute')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'execute'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <PlayIcon className="h-5 w-5 inline mr-2" />
              Execute
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Agents Tab */}
        {activeTab === 'agents' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Available Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((agent) => (
                <div key={agent.id} className="bg-white p-6 rounded-lg shadow">
                  <h3 className="font-semibold text-lg mb-2">{agent.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{agent.description}</p>
                  <div className="flex items-center justify-between">
                    <span className={`px-2 py-1 text-xs rounded ${
                      agent.status === 'idle' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {agent.status}
                    </span>
                    <button
                      onClick={() => {
                        setSelectedAgent(agent.id);
                        setActiveTab('execute');
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Execute →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Workflows Tab */}
        {activeTab === 'workflows' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Available Workflows</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {workflows.map((workflow) => (
                <div key={workflow.id} className="bg-white p-6 rounded-lg shadow">
                  <h3 className="font-semibold text-lg mb-2">{workflow.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{workflow.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      {workflow.task_count} tasks
                    </span>
                    <button
                      onClick={() => {
                        setSelectedWorkflow(workflow.id);
                        setActiveTab('execute');
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Execute →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Execute Tab */}
        {activeTab === 'execute' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Execution Panel */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Execute Agent or Workflow</h2>
              
              {/* Quick Examples */}
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <h3 className="font-medium mb-3">Quick Examples</h3>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => runExample('invoice')}
                    className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                  >
                    Process Invoice
                  </button>
                  <button
                    onClick={() => runExample('approval')}
                    className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                  >
                    Approval Request
                  </button>
                  <button
                    onClick={() => runExample('complaint')}
                    className="px-3 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
                  >
                    Customer Complaint
                  </button>
                  <button
                    onClick={() => runExample('financial')}
                    className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                  >
                    Financial Report
                  </button>
                  <button
                    onClick={() => runExample('recruitment')}
                    className="px-3 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm"
                  >
                    Screen Candidates
                  </button>
                  <button
                    onClick={() => runExample('risk')}
                    className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                  >
                    Risk Assessment
                  </button>
                </div>
              </div>

              {/* Agent Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Agent
                </label>
                <select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">Select an agent...</option>
                  {agents.map((agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Workflow Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Or Select Workflow
                </label>
                <select
                  value={selectedWorkflow}
                  onChange={(e) => setSelectedWorkflow(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">Select a workflow...</option>
                  {workflows.map((workflow) => (
                    <option key={workflow.id} value={workflow.id}>
                      {workflow.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Input Mode Selector */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Input Mode
                </label>
                <div className="flex space-x-4">
                  <button
                    onClick={() => setInputMode('text')}
                    className={`px-4 py-2 rounded ${
                      inputMode === 'text' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    Text
                  </button>
                  <button
                    onClick={() => setInputMode('json')}
                    className={`px-4 py-2 rounded ${
                      inputMode === 'json' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    JSON
                  </button>
                  <button
                    onClick={() => setInputMode('file')}
                    className={`px-4 py-2 rounded ${
                      inputMode === 'file' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    File Upload
                  </button>
                </div>
              </div>

              {/* Input Data */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {inputMode === 'text' ? 'Enter your request' : 
                   inputMode === 'json' ? 'Input Data (JSON)' : 
                   'Upload File'}
                </label>
                
                {inputMode === 'file' ? (
                  <div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileUpload}
                      accept=".pdf,.doc,.docx,.ppt,.pptx,.txt"
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-gray-400 transition-colors"
                    >
                      <CloudArrowUpIcon className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600">
                        Click to upload PDF, Word, PowerPoint, or text file
                      </p>
                      {uploadedFile && (
                        <p className="text-sm text-blue-600 mt-2">
                          <DocumentIcon className="h-4 w-4 inline mr-1" />
                          {uploadedFile.name}
                        </p>
                      )}
                    </button>
                  </div>
                ) : (
                  <textarea
                    value={inputData}
                    onChange={(e) => setInputData(e.target.value)}
                    placeholder={
                      inputMode === 'text' 
                        ? 'Enter your request in plain text...\n\nExample: Analyze our Q4 sales data and identify key trends'
                        : '{"task": "Analyze this data and provide insights"}'
                    }
                    className="w-full p-2 border border-gray-300 rounded-md h-32 font-mono text-sm"
                  />
                )}
              </div>

              {/* Execute Button */}
              <button
                onClick={selectedAgent ? executeAgent : executeWorkflow}
                disabled={loading || (!selectedAgent && !selectedWorkflow)}
                className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <span>Executing...</span>
                ) : (
                  <>
                    <PlayIcon className="h-5 w-5 mr-2" />
                    Execute {selectedAgent ? 'Agent' : 'Workflow'}
                  </>
                )}
              </button>
            </div>

            {/* Results Panel */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Execution Results</h2>
              {executionResult ? (
                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="mb-4">
                    <span className={`px-2 py-1 text-sm rounded ${
                      executionResult.status === 'completed' 
                        ? 'bg-green-100 text-green-800' 
                        : executionResult.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {executionResult.status}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <h3 className="font-medium mb-2">Output</h3>
                    <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto max-h-96">
                      {JSON.stringify(executionResult.output || executionResult, null, 2)}
                    </pre>
                  </div>
                  
                  {executionResult.metrics && (
                    <div>
                      <h3 className="font-medium mb-2">Metrics</h3>
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm">
                          Duration: {executionResult.metrics.duration_seconds?.toFixed(2)}s
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-gray-100 p-6 rounded-lg text-center text-gray-500">
                  No execution results yet. Execute an agent or workflow to see results.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;