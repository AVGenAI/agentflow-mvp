import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { 
  PlusIcon, 
  PlayIcon, 
  CogIcon, 
  ChartBarIcon,
  BoltIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  DocumentIcon,
  Bars3Icon,
  ChevronLeftIcon,
  ChevronRightIcon,
  SunIcon,
  MoonIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  XMarkIcon
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

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

// Skeleton Loading Components
const AgentCardSkeleton = () => (
  <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
    <div className="h-2 bg-gray-300 dark:bg-gray-600 animate-pulse-skeleton"></div>
    <div className="p-6">
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-xl animate-pulse-skeleton mr-4"></div>
        <div>
          <div className="h-5 bg-gray-300 dark:bg-gray-600 rounded animate-pulse-skeleton w-32 mb-2"></div>
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded-full animate-pulse-skeleton w-20"></div>
        </div>
      </div>
      <div className="space-y-2 mb-6">
        <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded animate-pulse-skeleton w-full"></div>
        <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded animate-pulse-skeleton w-4/5"></div>
        <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded animate-pulse-skeleton w-3/5"></div>
      </div>
      <div className="h-10 bg-gray-300 dark:bg-gray-600 rounded-lg animate-pulse-skeleton"></div>
    </div>
  </div>
);

const WorkflowCardSkeleton = () => (
  <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
    <div className="h-2 bg-gray-300 dark:bg-gray-600 animate-pulse-skeleton"></div>
    <div className="p-6">
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-xl animate-pulse-skeleton mr-4"></div>
        <div>
          <div className="h-5 bg-gray-300 dark:bg-gray-600 rounded animate-pulse-skeleton w-40 mb-2"></div>
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded-full animate-pulse-skeleton w-24"></div>
        </div>
      </div>
      <div className="space-y-2 mb-6">
        <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded animate-pulse-skeleton w-full"></div>
        <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded animate-pulse-skeleton w-5/6"></div>
      </div>
      <div className="h-10 bg-gray-300 dark:bg-gray-600 rounded-lg animate-pulse-skeleton"></div>
    </div>
  </div>
);

// Toast Component
const ToastComponent: React.FC<{ toast: Toast; onDismiss: () => void }> = ({ toast, onDismiss }) => {
  const getIcon = () => {
    switch (toast.type) {
      case 'success': return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error': return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'warning': return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'info': return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getBgColor = () => {
    switch (toast.type) {
      case 'success': return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'error': return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'warning': return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      case 'info': return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
    }
  };

  const getTextColor = () => {
    switch (toast.type) {
      case 'success': return 'text-green-800 dark:text-green-200';
      case 'error': return 'text-red-800 dark:text-red-200';
      case 'warning': return 'text-yellow-800 dark:text-yellow-200';
      case 'info': return 'text-blue-800 dark:text-blue-200';
    }
  };

  return (
    <div className={`max-w-sm w-full ${getBgColor()} border rounded-lg shadow-lg p-4 transition-all duration-300 ease-in-out transform translate-x-0`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${getTextColor()}`}>
            {toast.title}
          </h3>
          {toast.message && (
            <p className={`mt-1 text-sm ${getTextColor()} opacity-80`}>
              {toast.message}
            </p>
          )}
        </div>
        <div className="ml-4 flex-shrink-0">
          <button
            onClick={onDismiss}
            className={`inline-flex ${getTextColor()} hover:opacity-75 transition-opacity`}
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

// Toast Container Component
const ToastContainer: React.FC<{ toasts: Toast[]; onDismiss: (id: string) => void }> = ({ toasts, onDismiss }) => {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-3">
      {toasts.map((toast) => (
        <ToastComponent key={toast.id} toast={toast} onDismiss={() => onDismiss(toast.id)} />
      ))}
    </div>
  );
};

// Status Indicator Components
const StatusIndicator: React.FC<{ 
  status: 'online' | 'offline' | 'checking' | 'processing' | 'completed' | 'error' | 'idle', 
  label: string,
  showLabel?: boolean 
}> = ({ status, label, showLabel = true }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'online':
        return { color: 'bg-green-500', animation: '', tooltip: 'API Connected' };
      case 'offline':
        return { color: 'bg-red-500', animation: '', tooltip: 'API Disconnected' };
      case 'checking':
        return { color: 'bg-yellow-500', animation: 'animate-pulse', tooltip: 'Checking Connection' };
      case 'processing':
        return { color: 'bg-blue-500', animation: 'animate-pulse', tooltip: 'Processing Request' };
      case 'completed':
        return { color: 'bg-green-500', animation: '', tooltip: 'Process Completed' };
      case 'error':
        return { color: 'bg-red-500', animation: 'animate-pulse', tooltip: 'Process Failed' };
      case 'idle':
      default:
        return { color: 'bg-gray-400', animation: '', tooltip: 'Ready' };
    }
  };

  const config = getStatusConfig();

  return (
    <div className="flex items-center space-x-2" title={config.tooltip}>
      <div className={`w-2 h-2 rounded-full ${config.color} ${config.animation}`}></div>
      {showLabel && (
        <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
          {label}: {status}
        </span>
      )}
    </div>
  );
};

// Processing Status Badge Component
const ProcessingBadge: React.FC<{ status: 'idle' | 'processing' | 'completed' | 'error' }> = ({ status }) => {
  const getConfig = () => {
    switch (status) {
      case 'processing':
        return {
          bg: 'bg-blue-100 dark:bg-blue-900/30',
          text: 'text-blue-700 dark:text-blue-400',
          border: 'border-blue-200 dark:border-blue-700',
          icon: '⚡',
          label: 'Processing'
        };
      case 'completed':
        return {
          bg: 'bg-green-100 dark:bg-green-900/30',
          text: 'text-green-700 dark:text-green-400',
          border: 'border-green-200 dark:border-green-700',
          icon: '✅',
          label: 'Completed'
        };
      case 'error':
        return {
          bg: 'bg-red-100 dark:bg-red-900/30',
          text: 'text-red-700 dark:text-red-400',
          border: 'border-red-200 dark:border-red-700',
          icon: '❌',
          label: 'Error'
        };
      case 'idle':
      default:
        return {
          bg: 'bg-gray-100 dark:bg-gray-700',
          text: 'text-gray-700 dark:text-gray-300',
          border: 'border-gray-200 dark:border-gray-600',
          icon: '⭕',
          label: 'Ready'
        };
    }
  };

  const config = getConfig();

  if (status === 'idle') return null;

  return (
    <div className={`inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full ${config.bg} ${config.text} border ${config.border} ${status === 'processing' ? 'animate-pulse' : ''}`}>
      <span className="mr-1">{config.icon}</span>
      {config.label}
    </div>
  );
};

// Empty State Components
const EmptyStateNoAgents = () => (
  <div className="text-center py-16">
    <div className="relative">
      <div className="w-24 h-24 bg-gradient-to-br from-cyan-100 to-blue-100 dark:from-cyan-900/30 dark:to-blue-900/30 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg">
        <CogIcon className="h-12 w-12 text-cyan-500 dark:text-cyan-400" />
        <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-orange-400 to-pink-500 rounded-full flex items-center justify-center">
          <span className="text-white text-xs font-bold">0</span>
        </div>
      </div>
    </div>
    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">No AI Agents Available</h3>
    <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-md mx-auto leading-relaxed">
      No AI agents have been configured yet. Agents are specialized AI assistants that can help automate various business tasks.
    </p>
    <div className="flex flex-col sm:flex-row gap-3 justify-center">
      <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg hover:from-cyan-600 hover:to-blue-700 transition-all duration-300 font-semibold shadow-lg hover:shadow-xl flex items-center justify-center">
        <PlusIcon className="h-5 w-5 mr-2" />
        Add Agent
      </button>
      <button 
        onClick={() => window.location.reload()}
        className="px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-semibold"
      >
        Refresh
      </button>
    </div>
  </div>
);

const EmptyStateNoWorkflows = () => (
  <div className="text-center py-16">
    <div className="relative">
      <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg">
        <DocumentTextIcon className="h-12 w-12 text-purple-500 dark:text-purple-400" />
        <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-orange-400 to-pink-500 rounded-full flex items-center justify-center">
          <span className="text-white text-xs font-bold">0</span>
        </div>
      </div>
    </div>
    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">No Workflows Available</h3>
    <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-md mx-auto leading-relaxed">
      No automated workflows have been created yet. Workflows combine multiple agents to handle complex multi-step processes.
    </p>
    <div className="flex flex-col sm:flex-row gap-3 justify-center">
      <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 transition-all duration-300 font-semibold shadow-lg hover:shadow-xl flex items-center justify-center">
        <PlusIcon className="h-5 w-5 mr-2" />
        Create Workflow
      </button>
      <button 
        onClick={() => window.location.reload()}
        className="px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-semibold"
      >
        Refresh
      </button>
    </div>
  </div>
);

const EmptyStateNoResults = () => (
  <div className="text-center py-16">
    <div className="relative">
      <div className="w-24 h-24 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg">
        <ChartBarIcon className="h-12 w-12 text-green-500 dark:text-green-400" />
        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
          <PlayIcon className="h-3 w-3 text-white" />
        </div>
      </div>
    </div>
    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Ready to Execute</h3>
    <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-md mx-auto leading-relaxed">
      Select an agent or workflow from the Execute panel and run it to see results and conversation history here.
    </p>
    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 max-w-sm mx-auto">
      <div className="flex items-center text-sm text-blue-700 dark:text-blue-300">
        <InformationCircleIcon className="h-5 w-5 mr-2 flex-shrink-0" />
        <span>Tip: Use <kbd className="px-1 py-0.5 bg-blue-100 dark:bg-blue-800 rounded text-xs font-mono">Cmd/Ctrl + Enter</kbd> to execute quickly</span>
      </div>
    </div>
  </div>
);

// Keyboard Shortcuts Help Modal
const KeyboardHelpModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const shortcuts = [
    { keys: 'Cmd/Ctrl + B', description: 'Toggle sidebar' },
    { keys: 'Cmd/Ctrl + D', description: 'Toggle dark mode' },
    { keys: 'Cmd/Ctrl + Enter', description: 'Execute agent/workflow' },
    { keys: 'Cmd/Ctrl + 1', description: 'Switch to Agents tab' },
    { keys: 'Cmd/Ctrl + 2', description: 'Switch to Workflows tab' },
    { keys: 'Cmd/Ctrl + 3', description: 'Switch to Execute tab' },
    { keys: '?', description: 'Show this help' },
    { keys: 'Esc', description: 'Close help or dismiss toasts' },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Keyboard Shortcuts</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
          
          <div className="space-y-3">
            {shortcuts.map((shortcut, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-300">{shortcut.description}</span>
                <kbd className="px-2 py-1 text-xs font-mono bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded border border-gray-300 dark:border-gray-600">
                  {shortcut.keys}
                </kbd>
              </div>
            ))}
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
              Press <kbd className="px-1 py-0.5 text-xs font-mono bg-gray-100 dark:bg-gray-700 rounded">?</kbd> anytime to show this help
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

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
  const [dataLoading, setDataLoading] = useState(true);
  const [showRawOutput, setShowRawOutput] = useState(false);
  const [showFullHistory, setShowFullHistory] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Panel state management
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [executePanelSplit, setExecutePanelSplit] = useState(50);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeType, setResizeType] = useState<'sidebar' | 'execute' | null>(null);
  
  // Theme state management
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage or system preference
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) return JSON.parse(saved);
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Toast state management
  const [toasts, setToasts] = useState<Toast[]>([]);
  
  // Help modal state
  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false);
  
  // Mobile responsive state
  const [isMobile, setIsMobile] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  
  // Live status indicators state
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [processingStatus, setProcessingStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');

  useEffect(() => {
    const loadInitialData = async () => {
      setDataLoading(true);
      await Promise.all([fetchAgents(), fetchWorkflows()]);
      setDataLoading(false);
    };
    loadInitialData();
    
    // Check API status on mount
    checkApiStatus();
    
    // Set up periodic API status checks
    const statusInterval = setInterval(checkApiStatus, 30000); // Check every 30 seconds
    return () => clearInterval(statusInterval);
  }, []);

  // Dark mode effect
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Mobile detection effect
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      // Auto-collapse sidebar on mobile
      if (window.innerWidth < 768) {
        setSidebarCollapsed(true);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + B: Toggle sidebar
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
        e.preventDefault();
        setSidebarCollapsed(!sidebarCollapsed);
        showToast('info', 'Sidebar Toggled', sidebarCollapsed ? 'Sidebar expanded' : 'Sidebar collapsed');
      }
      
      // Cmd/Ctrl + D: Toggle dark mode
      if ((e.metaKey || e.ctrlKey) && e.key === 'd') {
        e.preventDefault();
        toggleDarkMode();
        showToast('info', 'Theme Changed', !darkMode ? 'Dark mode enabled' : 'Light mode enabled');
      }
      
      // Cmd/Ctrl + Enter: Execute (when form is focused)
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        const executeButton = document.querySelector('[data-testid="execute-button"]') as HTMLButtonElement;
        if (executeButton && !executeButton.disabled) {
          if (selectedAgent || selectedWorkflow) {
            selectedAgent ? executeAgent() : executeWorkflow();
          }
        }
      }
      
      // Esc: Dismiss all toasts or close help
      if (e.key === 'Escape') {
        if (showKeyboardHelp) {
          setShowKeyboardHelp(false);
        } else if (toasts.length > 0) {
          setToasts([]);
          showToast('info', 'Toasts Cleared', 'All notifications dismissed');
        }
      }
      
      // ?: Show keyboard shortcuts help
      if (e.key === '?' && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        setShowKeyboardHelp(true);
      }
      
      // Cmd/Ctrl + 1/2/3: Switch tabs
      if ((e.metaKey || e.ctrlKey) && ['1', '2', '3'].includes(e.key)) {
        e.preventDefault();
        const tabMap = { '1': 'agents', '2': 'workflows', '3': 'execute' } as const;
        const newTab = tabMap[e.key as '1' | '2' | '3'];
        setActiveTab(newTab);
        showToast('info', 'Tab Switched', `Switched to ${newTab.charAt(0).toUpperCase() + newTab.slice(1)} tab`);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [sidebarCollapsed, darkMode, toasts.length, selectedAgent, selectedWorkflow, activeTab, showKeyboardHelp]);

  // Toast utility functions
  const showToast = (type: Toast['type'], title: string, message?: string, duration = 5000) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: Toast = { id, type, title, message, duration };
    
    setToasts(prev => [...prev, newToast]);
    
    // Auto dismiss
    setTimeout(() => {
      dismissToast(id);
    }, duration);
  };

  const dismissToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  // Mouse event handlers for resizing
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      if (resizeType === 'sidebar') {
        const newWidth = Math.min(Math.max(e.clientX, 200), 500);
        setSidebarWidth(newWidth);
      } else if (resizeType === 'execute') {
        const container = document.getElementById('execute-container');
        if (container) {
          const rect = container.getBoundingClientRect();
          const newSplit = Math.min(Math.max(((e.clientX - rect.left) / rect.width) * 100, 20), 80);
          setExecutePanelSplit(newSplit);
        }
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      setResizeType(null);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = resizeType === 'sidebar' ? 'col-resize' : 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, resizeType]);

  const startSidebarResize = () => {
    setIsResizing(true);
    setResizeType('sidebar');
  };

  const startExecuteResize = () => {
    setIsResizing(true);
    setResizeType('execute');
  };

  const checkApiStatus = async () => {
    try {
      setApiStatus('checking');
      const response = await axios.get(`${API_URL}/health`, { timeout: 5000 });
      setApiStatus('online');
    } catch (error) {
      console.error('API health check failed:', error);
      setApiStatus('offline');
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${API_URL}/agents`);
      setAgents(response.data);
      setApiStatus('online');
    } catch (error) {
      console.error('Error fetching agents:', error);
      setApiStatus('offline');
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await axios.get(`${API_URL}/workflows`);
      setWorkflows(response.data);
      setApiStatus('online');
    } catch (error) {
      console.error('Error fetching workflows:', error);
      setApiStatus('offline');
    }
  };

  const executeAgent = async () => {
    if (!selectedAgent || (!inputData && uploadedFiles.length === 0)) return;

    setLoading(true);
    setProcessingStatus('processing');
    try {
      let parsedInput;
      
      if (inputMode === 'json') {
        try {
          parsedInput = JSON.parse(inputData);
        } catch (e) {
          showToast('error', 'Invalid JSON Format', 'Please check your input and try again.');
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
      setProcessingStatus('completed');
      showToast('success', 'Agent Executed Successfully', 'Your agent has completed the task.');
      setApiStatus('online');
    } catch (error) {
      console.error('Error executing agent:', error);
      setProcessingStatus('error');
      showToast('error', 'Execution Failed', 'Error executing agent. Check console for details.');
      setApiStatus('offline');
    } finally {
      setLoading(false);
      // Reset processing status after a delay
      setTimeout(() => setProcessingStatus('idle'), 3000);
    }
  };

  const executeWorkflow = async () => {
    if (!selectedWorkflow || !inputData) return;

    setLoading(true);
    setProcessingStatus('processing');
    try {
      let parsedInput;
      if (inputMode === 'json') {
        try {
          parsedInput = JSON.parse(inputData);
        } catch (e) {
          showToast('error', 'Invalid JSON Format', 'Please check your input and try again.');
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
      setProcessingStatus('completed');
      showToast('success', 'Workflow Executed Successfully', 'Your workflow has completed processing.');
      setApiStatus('online');
    } catch (error) {
      console.error('Error executing workflow:', error);
      setProcessingStatus('error');
      showToast('error', 'Execution Failed', 'Error executing workflow. Check console for details.');
      setApiStatus('offline');
    } finally {
      setLoading(false);
      // Reset processing status after a delay
      setTimeout(() => setProcessingStatus('idle'), 3000);
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
        showToast('warning', 'File Type Restriction', 'Some files were not added. Please upload only PDF, Word, PowerPoint, or text files.');
      }
      
      if (validFiles.length > 0) {
        setUploadedFiles(prev => [...prev, ...validFiles]);
        showToast('success', 'Files Uploaded', `${validFiles.length} file(s) uploaded successfully.`);
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

    // Ensure mainText is a string
    if (typeof mainText !== 'string') {
      mainText = String(mainText || '');
    }

    // Convert markdown-like formatting to HTML
    const formatMarkdownToHtml = (text: string): React.ReactNode => {
      // Ensure text is a string
      if (typeof text !== 'string') {
        text = String(text || '');
      }
      const lines = text.split('\n');
      const elements: React.ReactNode[] = [];
      let currentList: string[] = [];
      let currentTable: string[][] = [];
      
      const flushList = () => {
        if (currentList.length > 0) {
          elements.push(
            <ul key={elements.length} className="list-disc list-inside mb-4 space-y-1">
              {currentList.map((item, i) => (
                <li key={i} className="text-gray-700 dark:text-gray-300">{item}</li>
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
          const className = level === 1 ? "text-2xl font-bold mb-3 text-gray-900 dark:text-white" :
                           level === 2 ? "text-xl font-semibold mb-2 text-gray-800 dark:text-gray-200" :
                           "text-lg font-medium mb-2 text-gray-700 dark:text-gray-300";
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
            <p key={elements.length} className="mb-2 text-gray-700 dark:text-gray-300" 
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
      showToast('error', 'Example Failed', 'Error running example. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col transition-colors duration-200">
      {/* Header */}
      <header className="bg-black dark:bg-gray-800 border-b border-gray-800 dark:border-gray-700 flex-shrink-0 transition-colors duration-200">
        <div className="w-full px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="mr-4 p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              >
                <Bars3Icon className="h-6 w-6" />
              </button>
              <BoltIcon className="h-8 w-8 text-cyan-400 mr-3" />
              <h1 className="text-2xl font-bold text-white">AgentFlow</h1>
              <span className="ml-2 text-sm text-gray-400 font-normal">Enterprise AI Platform</span>
            </div>
            <div className="flex items-center space-x-4">
              {/* Status Indicators */}
              <div className="flex items-center space-x-4">
                <StatusIndicator status={apiStatus} label="API" showLabel={!isMobile} />
                <ProcessingBadge status={processingStatus} />
                {/* Manual refresh button */}
                <button
                  onClick={checkApiStatus}
                  disabled={apiStatus === 'checking'}
                  className="p-1 rounded text-gray-400 hover:text-white transition-colors disabled:opacity-50"
                  title="Refresh API status"
                >
                  <div className={`w-3 h-3 border border-gray-400 rounded-full ${
                    apiStatus === 'checking' ? 'animate-spin border-t-transparent' : ''
                  }`}></div>
                </button>
              </div>
              
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
              >
                {darkMode ? (
                  <SunIcon className="h-5 w-5" />
                ) : (
                  <MoonIcon className="h-5 w-5" />
                )}
              </button>
              <div className="text-sm text-gray-400">
                v2.0
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Layout - Resizable Split */}
      <div className={`${isMobile ? 'flex flex-col' : 'flex'} flex-1 overflow-hidden`}>
        {/* Left Sidebar - Collapsible & Resizable */}
        <div 
          className={`bg-gray-900 dark:bg-gray-800 border-r md:border-r border-b md:border-b-0 border-gray-700 dark:border-gray-600 flex flex-col transition-all duration-300 ease-in-out relative ${
            isMobile 
              ? (sidebarCollapsed ? 'h-0 overflow-hidden' : 'h-auto')
              : (sidebarCollapsed ? 'w-16' : '')
          }`}
          style={isMobile ? {
            height: sidebarCollapsed ? '0px' : 'auto'
          } : { 
            width: sidebarCollapsed ? '64px' : `${sidebarWidth}px`,
            minWidth: sidebarCollapsed ? '64px' : '200px',
            maxWidth: sidebarCollapsed ? '64px' : '500px'
          }}
        >
          {/* Navigation */}
          <nav className="flex-shrink-0 px-4 py-6">
            <div className={`${isMobile ? 'flex space-x-2' : 'space-y-2'}`}>
              <button
                onClick={() => {
                  setActiveTab('agents');
                  if (isMobile) setSidebarCollapsed(true);
                }}
                className={`${isMobile ? 'flex-1' : 'w-full'} flex items-center ${(sidebarCollapsed && !isMobile) ? 'px-2 py-3 justify-center' : 'px-4 py-3'} ${isMobile ? 'justify-center' : ''} rounded-lg font-medium text-sm transition-colors ${
                  activeTab === 'agents'
                    ? 'bg-cyan-900 text-cyan-100 border border-cyan-700'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
                title={(sidebarCollapsed && !isMobile) ? "Agents" : ""}
              >
                <CogIcon className={`h-5 w-5 ${(!sidebarCollapsed || isMobile) ? 'mr-3' : ''}`} />
                {(!sidebarCollapsed || isMobile) && 'Agents'}
              </button>
              <button
                onClick={() => {
                  setActiveTab('workflows');
                  if (isMobile) setSidebarCollapsed(true);
                }}
                className={`${isMobile ? 'flex-1' : 'w-full'} flex items-center ${(sidebarCollapsed && !isMobile) ? 'px-2 py-3 justify-center' : 'px-4 py-3'} ${isMobile ? 'justify-center' : ''} rounded-lg font-medium text-sm transition-colors ${
                  activeTab === 'workflows'
                    ? 'bg-cyan-900 text-cyan-100 border border-cyan-700'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
                title={(sidebarCollapsed && !isMobile) ? "Workflows" : ""}
              >
                <DocumentTextIcon className={`h-5 w-5 ${(!sidebarCollapsed || isMobile) ? 'mr-3' : ''}`} />
                {(!sidebarCollapsed || isMobile) && 'Workflows'}
              </button>
              <button
                onClick={() => {
                  setActiveTab('execute');
                  if (isMobile) setSidebarCollapsed(true);
                }}
                className={`${isMobile ? 'flex-1' : 'w-full'} flex items-center ${(sidebarCollapsed && !isMobile) ? 'px-2 py-3 justify-center' : 'px-4 py-3'} ${isMobile ? 'justify-center' : ''} rounded-lg font-medium text-sm transition-colors ${
                  activeTab === 'execute'
                    ? 'bg-cyan-900 text-cyan-100 border border-cyan-700'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
                title={(sidebarCollapsed && !isMobile) ? "Execute" : ""}
              >
                <PlayIcon className={`h-5 w-5 ${(!sidebarCollapsed || isMobile) ? 'mr-3' : ''}`} />
                {(!sidebarCollapsed || isMobile) && 'Execute'}
              </button>
            </div>
          </nav>

          {/* Status Panel */}
          {!sidebarCollapsed && !isMobile && (
            <div className="flex-1 px-4 pb-6">
              <div className="bg-gray-800 dark:bg-gray-700 rounded-lg p-4 border border-gray-700 dark:border-gray-600">
                <h3 className="text-white font-medium mb-3 flex items-center">
                  <span>System Status</span>
                  <StatusIndicator status={apiStatus} label="" showLabel={false} />
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">API Connection:</span>
                    <div className="flex items-center space-x-2">
                      <StatusIndicator status={apiStatus} label="" showLabel={false} />
                      <span className={`capitalize ${
                        apiStatus === 'online' ? 'text-green-400' : 
                        apiStatus === 'offline' ? 'text-red-400' : 
                        'text-yellow-400'
                      }`}>
                        {apiStatus}
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Processing:</span>
                    <div className="flex items-center space-x-2">
                      <StatusIndicator status={processingStatus} label="" showLabel={false} />
                      <span className={`capitalize ${
                        processingStatus === 'completed' ? 'text-green-400' : 
                        processingStatus === 'error' ? 'text-red-400' : 
                        processingStatus === 'processing' ? 'text-blue-400' : 
                        'text-gray-400'
                      }`}>
                        {processingStatus}
                      </span>
                    </div>
                  </div>
                  <div className="border-t border-gray-600 pt-3 mt-3">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Agents:</span>
                      <span className="text-cyan-400 font-medium">{agents.length}</span>
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-gray-400">Workflows:</span>
                      <span className="text-purple-400 font-medium">{workflows.length}</span>
                    </div>
                  </div>
                  {/* Live refresh indicator */}
                  <div className="flex justify-between items-center pt-2 border-t border-gray-600">
                    <span className="text-gray-400 text-xs">Last check:</span>
                    <div className="flex items-center space-x-1">
                      <div className={`w-1 h-1 rounded-full ${apiStatus === 'checking' ? 'bg-yellow-400 animate-pulse' : 'bg-gray-500'}`}></div>
                      <span className="text-gray-500 text-xs">Auto-refresh</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Resize Handle */}
          {!sidebarCollapsed && !isMobile && (
            <div
              className="absolute right-0 top-0 bottom-0 w-1 bg-gray-700 hover:bg-cyan-400 cursor-col-resize transition-colors group"
              onMouseDown={startSidebarResize}
            >
              <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-3 h-8 bg-gray-600 group-hover:bg-cyan-400 rounded-l-md opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          )}
        </div>

        {/* Main Content - 80% */}
        <div className="flex-1 bg-white dark:bg-gray-900 overflow-auto transition-colors duration-200">
          <div className="p-4 md:p-8">
            {/* Agents Tab */}
            {activeTab === 'agents' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">AI Agents</h2>
                  <p className="text-gray-600 dark:text-gray-300">Specialized AI agents for enterprise automation</p>
                </div>
                {dataLoading ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-6">
                    {Array.from({ length: 6 }, (_, i) => (
                      <AgentCardSkeleton key={i} />
                    ))}
                  </div>
                ) : agents.length === 0 ? (
                  <EmptyStateNoAgents />
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-6">
                    {agents.map((agent) => (
                    <div key={agent.id} className="group bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-cyan-300 dark:hover:border-cyan-600 hover:shadow-xl dark:hover:shadow-cyan-500/10 transition-all duration-300 hover:-translate-y-1 cursor-pointer overflow-hidden">
                      {/* Card Header with Gradient */}
                      <div className="h-2 bg-gradient-to-r from-cyan-400 to-blue-500"></div>
                      
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center">
                            <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center mr-4 shadow-lg group-hover:shadow-cyan-500/25 transition-shadow duration-300">
                              <CogIcon className="h-6 w-6 text-white" />
                            </div>
                            <div>
                              <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-1 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">{agent.name}</h3>
                              <span className={`inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full ${
                                agent.status === 'idle' 
                                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-700' 
                                  : agent.status === 'busy'
                                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-700'
                                  : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-700'
                              }`}>
                                <div className={`w-2 h-2 rounded-full mr-2 ${
                                  agent.status !== 'idle' ? 'animate-pulse' : ''
                                } ${
                                  agent.status === 'idle' ? 'bg-green-500' : 
                                  agent.status === 'busy' ? 'bg-blue-500' : 'bg-yellow-500'
                                }`}></div>
                                {agent.status}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <p className="text-gray-600 dark:text-gray-300 text-sm mb-6 leading-relaxed line-clamp-3">{agent.description}</p>
                        
                        <button
                          onClick={() => {
                            setSelectedAgent(agent.id);
                            setActiveTab('execute');
                          }}
                          className="w-full px-4 py-3 bg-gradient-to-r from-gray-900 to-gray-800 dark:from-gray-700 dark:to-gray-600 text-white rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all duration-300 text-sm font-semibold shadow-md hover:shadow-lg transform hover:scale-[1.02] flex items-center justify-center group"
                        >
                          <PlayIcon className="h-4 w-4 mr-2 group-hover:animate-pulse" />
                          Execute Agent
                        </button>
                      </div>
                    </div>
                  ))}
                  </div>
                )}
              </div>
            )}

            {/* Workflows Tab */}
            {activeTab === 'workflows' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Business Workflows</h2>
                  <p className="text-gray-600 dark:text-gray-300">Automated multi-agent workflows for complex processes</p>
                </div>
                {dataLoading ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
                    {Array.from({ length: 4 }, (_, i) => (
                      <WorkflowCardSkeleton key={i} />
                    ))}
                  </div>
                ) : workflows.length === 0 ? (
                  <EmptyStateNoWorkflows />
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
                    {workflows.map((workflow) => (
                    <div key={workflow.id} className="group bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-purple-300 dark:hover:border-purple-600 hover:shadow-xl dark:hover:shadow-purple-500/10 transition-all duration-300 hover:-translate-y-1 cursor-pointer overflow-hidden">
                      {/* Card Header with Gradient */}
                      <div className="h-2 bg-gradient-to-r from-purple-400 to-pink-500"></div>
                      
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center">
                            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mr-4 shadow-lg group-hover:shadow-purple-500/25 transition-shadow duration-300">
                              <DocumentTextIcon className="h-6 w-6 text-white" />
                            </div>
                            <div>
                              <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-1 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">{workflow.name}</h3>
                              <span className="inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-700">
                                <ChartBarIcon className="h-3 w-3 mr-1" />
                                {workflow.task_count} tasks
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <p className="text-gray-600 dark:text-gray-300 text-sm mb-6 leading-relaxed line-clamp-3">{workflow.description}</p>
                        
                        <button
                          onClick={() => {
                            setSelectedWorkflow(workflow.id);
                            setActiveTab('execute');
                          }}
                          className="w-full px-4 py-3 bg-gradient-to-r from-gray-900 to-gray-800 dark:from-gray-700 dark:to-gray-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-300 text-sm font-semibold shadow-md hover:shadow-lg transform hover:scale-[1.02] flex items-center justify-center group"
                        >
                          <PlayIcon className="h-4 w-4 mr-2 group-hover:animate-pulse" />
                          Execute Workflow
                        </button>
                      </div>
                    </div>
                  ))}
                  </div>
                )}
              </div>
            )}

            {/* Execute Tab */}
            {activeTab === 'execute' && (
              <div id="execute-container" className={`${isMobile ? 'flex flex-col' : 'flex'} h-full relative`}
                   style={{ height: isMobile ? 'auto' : 'calc(100vh - 120px)' }}
              >
                {/* Left Panel - Input */}
                <div 
                  className={`bg-white dark:bg-gray-900 ${isMobile ? 'border-b' : 'border-r'} border-gray-200 dark:border-gray-700 overflow-auto p-6 transition-colors duration-200`}
                  style={isMobile ? { height: 'auto' } : { width: `${executePanelSplit}%` }}
                >
                  <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Execute AI Tasks</h2>
                    <p className="text-gray-600 dark:text-gray-300">Run agents or workflows with your data</p>
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
                    data-testid="execute-button"
                    onClick={selectedAgent ? executeAgent : executeWorkflow}
                    disabled={loading || (!selectedAgent && !selectedWorkflow) || (inputMode === 'file' && uploadedFiles.length === 0 && !inputData) || (inputMode !== 'file' && !inputData)}
                    className={`w-full py-3 px-6 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center font-medium transition-all duration-300 ${
                      loading ? 'processing-glow' : ''
                    }`}
                  >
                    {loading ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                        <span>Executing...</span>
                        <div className="ml-2 flex space-x-1">
                          <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    ) : (
                      <>
                        <PlayIcon className="h-5 w-5 mr-2" />
                        Execute {selectedAgent ? 'Agent' : 'Workflow'}
                        {(selectedAgent || selectedWorkflow) && (
                          <div className="ml-2 w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        )}
                      </>
                    )}
                  </button>
                </div>
                
                {/* Resize Handle */}
                {!isMobile && (
                  <div
                    className="w-1 bg-gray-300 hover:bg-cyan-400 cursor-col-resize transition-colors flex-shrink-0 relative group"
                    onMouseDown={startExecuteResize}
                  >
                    <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3 h-8 bg-gray-400 group-hover:bg-cyan-400 rounded-md opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                )}

                {/* Right Panel - Results */}
                <div 
                  className="bg-gray-50 dark:bg-gray-800 overflow-auto p-6 transition-colors duration-200"
                  style={isMobile ? { height: 'auto' } : { width: `${100 - executePanelSplit}%` }}
                >
                  <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Execution Results</h2>
                    <p className="text-gray-600 dark:text-gray-300">AI processing results and conversation history</p>
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
                          <div className="text-sm text-gray-500 text-right">
                            {executionResult.metrics?.duration_seconds && (
                              <div>Completed in {executionResult.metrics.duration_seconds.toFixed(2)}s</div>
                            )}
                            {executionResult.output?.conversation_history && (() => {
                              const aiMessages = executionResult.output.conversation_history.filter((msg: any) => 
                                msg.role === 'ai' && msg.meta_data?.tokens_per_second
                              );
                              if (aiMessages.length > 0) {
                                const avgTokensPerSec = aiMessages.reduce((sum: number, msg: any) => 
                                  sum + (msg.meta_data?.tokens_per_second || 0), 0
                                ) / aiMessages.length;
                                return (
                                  <div className="text-cyan-600 font-medium">
                                    ⚡ Avg: {avgTokensPerSec.toFixed(1)} tokens/sec
                                  </div>
                                );
                              }
                              return null;
                            })()}
                          </div>
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
                                {(msg.model_used || msg.token_count || msg.meta_data?.tokens_per_second) && (
                                  <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500 space-x-4">
                                    {msg.model_used && (
                                      <span>Model: {msg.model_used}</span>
                                    )}
                                    {msg.token_count && (
                                      <span>Tokens: {msg.token_count}</span>
                                    )}
                                    {msg.meta_data?.tokens_per_second && (
                                      <span className="text-cyan-600 font-medium">
                                        ⚡ {msg.meta_data.tokens_per_second} tokens/sec
                                      </span>
                                    )}
                                    {msg.meta_data?.processing_duration && (
                                      <span>Duration: {msg.meta_data.processing_duration.toFixed(2)}s</span>
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
                    <EmptyStateNoResults />
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Toast Container */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
      
      {/* Keyboard Shortcuts Help Modal */}
      <KeyboardHelpModal isOpen={showKeyboardHelp} onClose={() => setShowKeyboardHelp(false)} />
    </div>
  );
}

export default App;