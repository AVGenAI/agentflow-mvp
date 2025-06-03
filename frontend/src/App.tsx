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
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [activeTab, setActiveTab] = useState<'agents' | 'workflows' | 'execute'>('agents');
  const [loading, setLoading] = useState(false);
  const [showRawOutput, setShowRawOutput] = useState(false);
  const [showFullHistory, setShowFullHistory] = useState(false);
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
    if (!selectedAgent || (!inputData && uploadedFiles.length === 0)) return;

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
      } else if (inputMode === 'file' && uploadedFiles.length > 0) {
        // For file mode, read all file contents
        const fileContents = await Promise.all(
          uploadedFiles.map(async (file) => ({
            name: file.name,
            type: file.type,
            content: await readFileContent(file)
          }))
        );
        parsedInput = { 
          task: inputData || `Process these ${uploadedFiles.length} files`,
          files: fileContents,
          file_count: uploadedFiles.length
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
    const files = event.target.files;
    if (files) {
      const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint',
        'text/plain'
      ];
      
      const validFiles = Array.from(files).filter(file => allowedTypes.includes(file.type));
      const invalidFiles = Array.from(files).filter(file => !allowedTypes.includes(file.type));
      
      if (invalidFiles.length > 0) {
        alert(`Some files were not added. Please upload only PDF, Word, PowerPoint, or text files.`);
      }
      
      if (validFiles.length > 0) {
        setUploadedFiles(prev => [...prev, ...validFiles]);
      }
    }
  };
  
  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const readFileContent = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      // For text files, read as text
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        reader.onload = (e) => {
          const content = e.target?.result;
          if (typeof content === 'string') {
            resolve(content);
          } else {
            resolve(`[File: ${file.name}] - Error reading text content`);
          }
        };
        reader.readAsText(file);
      } else {
        // For binary files (PDF, Word, PowerPoint), convert to base64
        reader.onload = (e) => {
          const arrayBuffer = e.target?.result;
          if (arrayBuffer instanceof ArrayBuffer) {
            // Convert ArrayBuffer to base64
            const bytes = new Uint8Array(arrayBuffer);
            let binary = '';
            bytes.forEach((byte) => binary += String.fromCharCode(byte));
            const base64 = btoa(binary);
            
            // Send as base64 with metadata
            resolve(JSON.stringify({
              type: 'binary',
              format: file.type,
              name: file.name,
              size: file.size,
              base64: base64
            }));
          } else {
            resolve(`[File: ${file.name}] - Error reading binary content`);
          }
        };
        reader.readAsArrayBuffer(file);
      }
      
      reader.onerror = () => {
        resolve(`[File: ${file.name}] - Error reading file`);
      };
    });
  };

  const formatOutput = (output: any): React.ReactNode => {
    // Extract the main result text
    let mainText = '';
    
    if (typeof output === 'string') {
      mainText = output;
    } else if (output?.result) {
      mainText = output.result;
    } else if (output?.final_answer) {
      mainText = output.final_answer;
    } else {
      mainText = JSON.stringify(output, null, 2);
    }

    // Convert markdown-like formatting to HTML
    const formatMarkdownToHtml = (text: string): React.ReactNode => {
      const lines = text.split('\n');
      const elements: React.ReactNode[] = [];
      let currentList: string[] = [];
      let currentTable: string[][] = [];
      
      const flushList = () => {
        if (currentList.length > 0) {
          elements.push(
            <ul key={elements.length} className="list-disc list-inside mb-4 space-y-1">
              {currentList.map((item, i) => (
                <li key={i} className="text-gray-700">{item}</li>
              ))}
            </ul>
          );
          currentList = [];
        }
      };

      const flushTable = () => {
        if (currentTable.length > 0) {
          elements.push(
            <div key={elements.length} className="mb-4 overflow-x-auto">
              <table className="min-w-full border border-gray-300">
                <thead>
                  <tr className="bg-gray-50">
                    {currentTable[0]?.map((header, i) => (
                      <th key={i} className="border border-gray-300 px-3 py-2 text-left font-medium">
                        {header.trim()}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {currentTable.slice(1).map((row, i) => (
                    <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      {row.map((cell, j) => (
                        <td key={j} className="border border-gray-300 px-3 py-2">
                          {cell.trim()}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
          currentTable = [];
        }
      };

      lines.forEach((line, index) => {
        // Handle headers
        if (line.startsWith('#')) {
          flushList();
          flushTable();
          const level = line.match(/^#+/)?.[0].length || 1;
          const text = line.replace(/^#+\s*/, '');
          const HeaderTag = `h${Math.min(level, 6)}` as keyof JSX.IntrinsicElements;
          const className = level === 1 ? "text-2xl font-bold mb-3 text-gray-900" :
                           level === 2 ? "text-xl font-semibold mb-2 text-gray-800" :
                           "text-lg font-medium mb-2 text-gray-700";
          elements.push(
            <HeaderTag key={elements.length} className={className}>
              {text}
            </HeaderTag>
          );
        }
        // Handle tables
        else if (line.includes('|') && line.trim().startsWith('|')) {
          flushList();
          const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
          if (cells.length > 0) {
            currentTable.push(cells);
          }
        }
        // Handle list items
        else if (line.match(/^\s*[-*+]\s+/) || line.match(/^\s*\d+\.\s+/)) {
          flushTable();
          const text = line.replace(/^\s*[-*+\d.]+\s+/, '');
          currentList.push(text);
        }
        // Handle bold text and regular paragraphs
        else if (line.trim()) {
          flushList();
          flushTable();
          let formattedLine = line;
          
          // Replace **bold** with <strong>
          formattedLine = formattedLine.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
          
          // Handle emojis and special formatting
          elements.push(
            <p key={elements.length} className="mb-2 text-gray-700" 
               dangerouslySetInnerHTML={{ __html: formattedLine }} />
          );
        }
        // Handle empty lines
        else {
          flushList();
          flushTable();
          if (line.trim() === '') {
            elements.push(<div key={elements.length} className="mb-2"></div>);
          }
        }
      });

      // Flush any remaining lists or tables
      flushList();
      flushTable();
      
      return elements;
    };

    return formatMarkdownToHtml(mainText);
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
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-black border-b border-gray-800 flex-shrink-0">
        <div className="w-full px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <BoltIcon className="h-8 w-8 text-cyan-400 mr-3" />
              <h1 className="text-2xl font-bold text-white">AgentFlow</h1>
              <span className="ml-2 text-sm text-gray-400 font-normal">Enterprise AI Platform</span>
            </div>
            <div className="text-sm text-gray-400">
              v1.0.0
            </div>
          </div>
        </div>
      </header>

      {/* Main Layout - 20/80 Split */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - 20% */}
        <div className="w-1/5 bg-gray-900 border-r border-gray-700 flex flex-col">
          {/* Navigation */}
          <nav className="flex-shrink-0 px-4 py-6">
            <div className="space-y-2">
              <button
                onClick={() => setActiveTab('agents')}
                className={`w-full flex items-center px-4 py-3 rounded-lg font-medium text-sm transition-colors ${
                  activeTab === 'agents'
                    ? 'bg-cyan-900 text-cyan-100 border border-cyan-700'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                <CogIcon className="h-5 w-5 mr-3" />
                Agents
              </button>
              <button
                onClick={() => setActiveTab('workflows')}
                className={`w-full flex items-center px-4 py-3 rounded-lg font-medium text-sm transition-colors ${
                  activeTab === 'workflows'
                    ? 'bg-cyan-900 text-cyan-100 border border-cyan-700'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                <DocumentTextIcon className="h-5 w-5 mr-3" />
                Workflows
              </button>
              <button
                onClick={() => setActiveTab('execute')}
                className={`w-full flex items-center px-4 py-3 rounded-lg font-medium text-sm transition-colors ${
                  activeTab === 'execute'
                    ? 'bg-cyan-900 text-cyan-100 border border-cyan-700'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                <PlayIcon className="h-5 w-5 mr-3" />
                Execute
              </button>
            </div>
          </nav>

          {/* Status Panel */}
          <div className="flex-1 px-4 pb-6">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="text-white font-medium mb-3">System Status</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Agents:</span>
                  <span className="text-green-400">{agents.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Workflows:</span>
                  <span className="text-green-400">{workflows.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-green-400">Online</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content - 80% */}
        <div className="flex-1 bg-white overflow-auto">
          <div className="p-8">
            {/* Agents Tab */}
            {activeTab === 'agents' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Agents</h2>
                  <p className="text-gray-600">Specialized AI agents for enterprise automation</p>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {agents.map((agent) => (
                    <div key={agent.id} className="bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-shadow">
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center mr-3">
                              <CogIcon className="h-5 w-5 text-cyan-400" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-lg text-gray-900">{agent.name}</h3>
                              <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${
                                agent.status === 'idle' 
                                  ? 'bg-green-100 text-green-800 border border-green-200' 
                                  : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                              }`}>
                                <div className={`w-1.5 h-1.5 rounded-full mr-1 ${
                                  agent.status === 'idle' ? 'bg-green-400' : 'bg-yellow-400'
                                }`}></div>
                                {agent.status}
                              </span>
                            </div>
                          </div>
                        </div>
                        <p className="text-gray-600 text-sm mb-4 leading-relaxed">{agent.description}</p>
                        <button
                          onClick={() => {
                            setSelectedAgent(agent.id);
                            setActiveTab('execute');
                          }}
                          className="w-full px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium"
                        >
                          Execute Agent
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
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Business Workflows</h2>
                  <p className="text-gray-600">Automated multi-agent workflows for complex processes</p>
                </div>
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  {workflows.map((workflow) => (
                    <div key={workflow.id} className="bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-shadow">
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center mr-3">
                              <DocumentTextIcon className="h-5 w-5 text-cyan-400" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-lg text-gray-900">{workflow.name}</h3>
                              <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700 border border-gray-200">
                                {workflow.task_count} tasks
                              </span>
                            </div>
                          </div>
                        </div>
                        <p className="text-gray-600 text-sm mb-4 leading-relaxed">{workflow.description}</p>
                        <button
                          onClick={() => {
                            setSelectedWorkflow(workflow.id);
                            setActiveTab('execute');
                          }}
                          className="w-full px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium"
                        >
                          Execute Workflow
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
                  <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Execute AI Tasks</h2>
                    <p className="text-gray-600">Run agents or workflows with your data</p>
                  </div>
                  
                  {/* Quick Examples */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
                    <h3 className="font-semibold text-gray-900 mb-4">Quick Start Examples</h3>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => runExample('invoice')}
                        className="px-4 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium"
                      >
                        Process Invoice
                      </button>
                      <button
                        onClick={() => runExample('approval')}
                        className="px-4 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium"
                      >
                        Approval Request
                      </button>
                      <button
                        onClick={() => runExample('complaint')}
                        className="px-4 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium"
                      >
                        Customer Complaint
                      </button>
                      <button
                        onClick={() => runExample('financial')}
                        className="px-4 py-3 bg-green-700 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
                      >
                        Financial Report
                      </button>
                      <button
                        onClick={() => runExample('recruitment')}
                        className="px-4 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium"
                      >
                        Screen Candidates
                      </button>
                      <button
                        onClick={() => runExample('risk')}
                        className="px-4 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium"
                      >
                        Risk Assessment
                      </button>
                    </div>
                  </div>

                  {/* Agent Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-900 mb-3">
                      Select Agent
                    </label>
                    <select
                      value={selectedAgent}
                      onChange={(e) => setSelectedAgent(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                    >
                      <option value="">Choose an agent...</option>
                      {agents.map((agent) => (
                        <option key={agent.id} value={agent.id}>
                          {agent.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Workflow Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-900 mb-3">
                      Or Select Workflow
                    </label>
                    <select
                      value={selectedWorkflow}
                      onChange={(e) => setSelectedWorkflow(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                    >
                      <option value="">Choose a workflow...</option>
                      {workflows.map((workflow) => (
                        <option key={workflow.id} value={workflow.id}>
                          {workflow.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Input Mode Selector */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-900 mb-3">
                      Input Mode
                    </label>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setInputMode('text');
                          setUploadedFiles([]);
                        }}
                        className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                          inputMode === 'text' 
                            ? 'bg-cyan-600 text-white border border-cyan-600' 
                            : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        Text
                      </button>
                      <button
                        onClick={() => {
                          setInputMode('json');
                          setUploadedFiles([]);
                        }}
                        className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                          inputMode === 'json' 
                            ? 'bg-cyan-600 text-white border border-cyan-600' 
                            : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        JSON
                      </button>
                      <button
                        onClick={() => setInputMode('file')}
                        className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                          inputMode === 'file' 
                            ? 'bg-cyan-600 text-white border border-cyan-600' 
                            : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        File Upload
                      </button>
                    </div>
                  </div>

                  {/* Input Data */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-900 mb-3">
                      {inputMode === 'text' ? 'Enter your request' : 
                       inputMode === 'json' ? 'Input Data (JSON)' : 
                       'Upload Files'}
                    </label>
                
                {inputMode === 'file' ? (
                  <div className="space-y-4">
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileUpload}
                      accept=".pdf,.doc,.docx,.ppt,.pptx,.txt"
                      multiple
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-cyan-400 hover:bg-cyan-50 transition-colors"
                    >
                      <CloudArrowUpIcon className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600">
                        Click to upload PDF, Word, PowerPoint, or text files (multiple allowed)
                      </p>
                    </button>
                    
                    {uploadedFiles.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-700">Uploaded Files:</p>
                        {uploadedFiles.map((file, index) => (
                          <div key={index} className="flex items-center justify-between bg-gray-50 border border-gray-200 p-3 rounded-lg">
                            <div className="flex items-center">
                              <DocumentIcon className="h-4 w-4 text-cyan-600 mr-3" />
                              <span className="text-sm text-gray-900 font-medium">{file.name}</span>
                            </div>
                            <button
                              onClick={() => removeFile(index)}
                              className="text-gray-500 hover:text-gray-700 text-sm font-medium"
                            >
                              Remove
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-2">
                        What would you like to do with these files?
                      </label>
                      <textarea
                        value={inputData}
                        onChange={(e) => setInputData(e.target.value)}
                        placeholder="e.g., Compare these documents and summarize the key differences..."
                        className="w-full p-3 border border-gray-300 rounded-lg h-24 text-sm bg-white focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                      />
                    </div>
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
                      className={`w-full p-3 border border-gray-300 rounded-lg h-32 text-sm bg-white focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 ${
                        inputMode === 'json' ? 'font-mono' : ''
                      }`}
                    />
                )}
              </div>

                  {/* Execute Button */}
                  <button
                    onClick={selectedAgent ? executeAgent : executeWorkflow}
                    disabled={loading || (!selectedAgent && !selectedWorkflow) || (inputMode === 'file' && uploadedFiles.length === 0 && !inputData) || (inputMode !== 'file' && !inputData)}
                    className="w-full py-3 px-6 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center font-medium transition-colors"
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
                  <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Execution Results</h2>
                    <p className="text-gray-600">AI processing results and conversation history</p>
                  </div>
                  {executionResult ? (
                    <div className="bg-white border border-gray-200 rounded-lg">
                      <div className="p-6 border-b border-gray-200">
                        <div className="flex items-center justify-between">
                          <span className={`inline-flex items-center px-3 py-1 text-sm font-medium rounded-full ${
                            executionResult.status === 'completed' 
                              ? 'bg-green-100 text-green-800 border border-green-200' 
                              : executionResult.status === 'failed'
                              ? 'bg-red-100 text-red-800 border border-red-200'
                              : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                          }`}>
                            <div className={`w-1.5 h-1.5 rounded-full mr-2 ${
                              executionResult.status === 'completed' ? 'bg-green-400' :
                              executionResult.status === 'failed' ? 'bg-red-400' : 'bg-yellow-400'
                            }`}></div>
                            {executionResult.status}
                          </span>
                          {executionResult.metrics?.duration_seconds && (
                            <span className="text-sm text-gray-500">
                              Completed in {executionResult.metrics.duration_seconds.toFixed(2)}s
                            </span>
                          )}
                        </div>
                      </div>
                  
                      {/* Conversation History */}
                      {executionResult.output?.conversation_history && executionResult.output.conversation_history.length > 0 && (
                        <div className="p-6 border-b border-gray-200">
                          <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">Conversation History</h3>
                            <div className="text-right">
                              {(() => {
                                const messages = executionResult.output.conversation_history.filter((msg: any) => !msg.is_separator);
                                const conversations = executionResult.output.conversation_history.filter((msg: any) => msg.is_separator).length;
                                const humanMessages = messages.filter((msg: any) => msg.role === 'human').length;
                                const aiMessages = messages.filter((msg: any) => msg.role === 'ai').length;
                                return (
                                  <div className="space-y-2">
                                    <div className="text-xs text-gray-500">
                                      {conversations} conversations • {messages.length} total messages
                                    </div>
                                    <div className="text-xs text-gray-500">
                                      👤 {humanMessages} user • 🤖 {aiMessages} AI
                                    </div>
                                    {conversations > 1 && (
                                      <button
                                        onClick={() => setShowFullHistory(!showFullHistory)}
                                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs hover:bg-gray-200 transition-colors border border-gray-200"
                                      >
                                        {showFullHistory ? 'Show Current Only' : 'Show All History'}
                                      </button>
                                    )}
                                  </div>
                                );
                              })()}
                            </div>
                          </div>
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
                        {executionResult.output.conversation_history
                          .filter((msg: any) => {
                            // If showing full history, show everything
                            if (showFullHistory) return true;
                            
                            // If showing current only, filter to current conversation
                            // Current conversation is after the last "--- Current Conversation ---" separator
                            const currentSeparatorIndex = executionResult.output.conversation_history
                              .findLastIndex((m: any) => m.is_separator && m.content.includes("Current Conversation"));
                            
                            // If no current separator found, show only non-separator messages from this session
                            if (currentSeparatorIndex === -1) {
                              return !msg.is_separator || msg.content.includes("Current Conversation");
                            }
                            
                            // Show everything from current conversation separator onwards
                            return executionResult.output.conversation_history.indexOf(msg) >= currentSeparatorIndex;
                          })
                          .map((msg: any, index: number) => {
                          // Handle conversation separators
                          if (msg.is_separator) {
                            return (
                              <div key={msg.conversation_id || index} className="my-4">
                                <div className="flex items-center">
                                  <div className="flex-grow border-t border-gray-300"></div>
                                  <span className="px-3 text-xs text-gray-600 bg-white border border-gray-200 rounded-full">
                                    {msg.content}
                                  </span>
                                  <div className="flex-grow border-t border-gray-300"></div>
                                </div>
                              </div>
                            );
                          }
                          
                          // Regular messages
                          return (
                            <div key={msg.id || index} className={`mb-3 ${
                              msg.role === 'human' ? 'ml-0 mr-8' : msg.role === 'ai' ? 'ml-8 mr-0' : 'mx-4'
                            }`}>
                              <div className={`rounded-lg p-4 border ${
                                msg.role === 'human' ? 'bg-cyan-50 border-cyan-200 text-cyan-900' :
                                msg.role === 'ai' ? 'bg-green-50 border-green-200 text-green-900' :
                                'bg-gray-50 border-gray-200 text-gray-900'
                              }`}>
                                <div className="flex items-center justify-between mb-2">
                                  <span className={`font-semibold text-xs uppercase px-2 py-1 rounded-full ${
                                    msg.role === 'human' ? 'bg-cyan-100 text-cyan-800' :
                                    msg.role === 'ai' ? 'bg-green-100 text-green-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>{msg.role}</span>
                                  <div className="text-xs text-gray-500 space-x-2">
                                    <span>{new Date(msg.timestamp).toLocaleString('en-US', {
                                      timeZone: 'America/Chicago',
                                      year: 'numeric',
                                      month: 'short',
                                      day: 'numeric',
                                      hour: '2-digit',
                                      minute: '2-digit',
                                      second: '2-digit',
                                      timeZoneName: 'short'
                                    })}</span>
                                    {msg.conversation_id && (
                                      <span className="px-2 py-1 bg-white bg-opacity-70 rounded text-gray-600">
                                        ID: {msg.conversation_id.slice(0, 8)}...
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <div className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                                {(msg.model_used || msg.token_count) && (
                                  <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500 space-x-4">
                                    {msg.model_used && (
                                      <span>Model: {msg.model_used}</span>
                                    )}
                                    {msg.token_count && (
                                      <span>Tokens: {msg.token_count}</span>
                                    )}
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                          })}
                          </div>
                        </div>
                      )}
                  
                      <div className="p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-semibold text-gray-900">Output</h3>
                          <button
                            onClick={() => setShowRawOutput(!showRawOutput)}
                            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors border border-gray-200"
                          >
                            {showRawOutput ? 'Show Formatted' : 'Show Raw'}
                          </button>
                        </div>
                        
                        {showRawOutput ? (
                          <pre className="bg-gray-50 border border-gray-200 p-4 rounded-lg text-sm overflow-auto max-h-96 font-mono">
                            {JSON.stringify(executionResult.output || executionResult, null, 2)}
                          </pre>
                        ) : (
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-auto">
                            <div className="prose prose-sm max-w-none">
                              {formatOutput(executionResult.output || executionResult)}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                      <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                        <ChartBarIcon className="h-8 w-8 text-gray-400" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">No Results Yet</h3>
                      <p className="text-gray-600">Execute an agent or workflow to see results and conversation history.</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;