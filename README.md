# AgentFlow MVP 🤖

A minimal viable product for an enterprise Agentic AI platform that enables autonomous business process automation.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.2+-61DAFB.svg)

## Features

- **Agent Creation**: Define autonomous AI agents with goals and capabilities
- **Workflow Orchestration**: Coordinate multiple agents to complete complex tasks
- **Integration Framework**: Connect to external systems via APIs
- **Monitoring Dashboard**: Track agent performance and decisions
- **REST API**: Programmatic agent management
- **Multiple LLM Support**: Use OpenAI, Ollama (local), or mock mode

## Tech Stack

- **Backend**: Python (FastAPI)
- **Agent Framework**: LangChain + Custom orchestration
- **Frontend**: React + TypeScript
- **Database**: PostgreSQL + Redis
- **Message Queue**: Redis/Celery
- **AI/LLM**: Multiple providers supported:
  - OpenAI (GPT-4, GPT-3.5)
  - Ollama (Llama2, Mistral, Mixtral, etc.)
  - Mock mode for testing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentflow-mvp.git
cd agentflow-mvp
```

2. Set up the backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd ../frontend
npm install
```

4. Configure environment (optional):
```bash
cd ../backend
cp .env.example .env
# Edit .env to add OpenAI API key (optional - runs in mock mode without it)
```

5. Start the application:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Access the application at http://localhost:3000

## Project Structure

```
agentflow-mvp/
├── backend/          # FastAPI backend services
├── frontend/         # React web interface
├── agents/           # Agent definitions and templates
├── examples/         # Example use cases
├── tests/           # Test suites
└── docs/            # Documentation
```

## 📋 Available Agents

1. **Process Automation Specialist** - Automates business processes
2. **Decision Maker** - Makes data-driven decisions
3. **Customer Service Specialist** - Handles complaints and inquiries
4. **Data Analyst** - Analyzes data and identifies patterns
5. **Compliance Officer** - Ensures regulatory compliance
6. **HR Recruitment Specialist** - Screens candidates and schedules interviews
7. **Financial Analyst** - Analyzes financial data and creates reports

## 🔄 Available Workflows

1. **Purchase Approval Workflow** - Multi-step approval process
2. **Customer Complaint Resolution** - End-to-end complaint handling
3. **Monthly Financial Reporting** - Automated financial analysis
4. **Recruitment Pipeline** - Candidate screening and selection
5. **Enterprise Risk Assessment** - Comprehensive risk analysis

## 📝 Input Modes

- **Text Mode**: Natural language input
- **JSON Mode**: Structured data input
- **File Upload**: Support for PDF, Word, PowerPoint, and text files

## 🔧 Configuration

### LLM Providers

The system supports multiple LLM providers:

1. **Mock Mode** (default): No API key required
2. **OpenAI**: Add your API key in `.env`
3. **Ollama**: Local LLM support (see `LLM_SETUP_GUIDE.md`)

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Optional - system runs in mock mode without these
OPENAI_API_KEY=your_openai_api_key_here
```

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Agents Guide](AGENTS_GUIDE.md)
- [Input Modes Guide](INPUT_MODES_GUIDE.md)
- [LLM Setup Guide](LLM_SETUP_GUIDE.md)
- [Running Instructions](RUN_INSTRUCTIONS.md)

## 🧪 Testing

The system includes example buttons for quick testing:
- Process Invoice
- Approval Request
- Customer Complaint
- Financial Report
- Screen Candidates
- Risk Assessment

## 🛠 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python main.py
```

### Frontend Development
```bash
cd frontend
npm start
```

### API Documentation
When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- UI components from [Heroicons](https://heroicons.com/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)