# AgentFlow MVP - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- LLM Provider (choose one):
  - OpenAI API Key
  - Ollama (local LLM)
  - Mock mode (no LLM required)
- Docker & Docker Compose (optional)

## Option 1: Local Development

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Configure your LLM provider in `.env`:

**Option A: OpenAI**
```
LLM_PROVIDER=openai
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

**Option B: Ollama (Local LLM)**
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```
Run `./setup_ollama.sh` to install and configure Ollama.

**Option C: Mock Mode (Default)**
```
LLM_PROVIDER=mock
```
No API key required - provides simulated responses.

6. Run the backend:
```bash
python main.py
```

The API will be available at http://localhost:8000

### Frontend Setup

1. In a new terminal, navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The UI will be available at http://localhost:3000

## Option 2: Docker Compose

1. Create `.env` file in the root directory:
```bash
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

2. Run with Docker Compose:
```bash
docker-compose up
```

This will start:
- Backend API at http://localhost:8000
- Frontend UI at http://localhost:3000
- PostgreSQL database at localhost:5432
- Redis at localhost:6379

## Using the Application

### 1. View Available Agents
- Navigate to the "Agents" tab to see pre-configured AI agents
- Two default agents are available:
  - **Process Automation Specialist**: For automating business processes
  - **Decision Maker**: For data-driven decision making

### 2. View Workflows
- Navigate to the "Workflows" tab
- A sample "Purchase Approval Workflow" is pre-configured

### 3. Execute an Agent

1. Go to the "Execute" tab
2. Select an agent from the dropdown
3. Enter JSON input data, for example:
```json
{
  "task": "Analyze the efficiency of our invoice processing system and suggest improvements"
}
```
4. Click "Execute Agent"
5. View the results in the right panel

### 4. Execute a Workflow

1. Go to the "Execute" tab
2. Select a workflow from the dropdown
3. Enter JSON input data, for example:
```json
{
  "request_data": {
    "type": "purchase_request",
    "amount": 5000,
    "department": "IT",
    "item": "Software licenses"
  }
}
```
4. Click "Execute Workflow"
5. View the workflow execution results

### 5. Try Quick Examples

Click the "Process Invoice" or "Approval Request" buttons to see pre-configured examples in action.

## API Documentation

The FastAPI backend includes automatic API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key API Endpoints

- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `POST /api/agents/execute` - Execute an agent
- `GET /api/workflows` - List all workflows
- `POST /api/workflows` - Create new workflow
- `POST /api/workflows/execute` - Execute a workflow

## Troubleshooting

1. **OpenAI API Key Error**: Make sure you've set the `OPENAI_API_KEY` in your `.env` file
2. **Port Already in Use**: Change ports in `.env` or `docker-compose.yml`
3. **Module Not Found**: Ensure all dependencies are installed correctly
4. **CORS Issues**: The backend is configured to allow all origins in development

## Next Steps

1. Create custom agents with specific capabilities
2. Design complex multi-agent workflows
3. Add integrations with external systems
4. Implement production-ready security features
5. Add persistent storage for agent configurations

For more information, see the main README.md file.