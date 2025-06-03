# Running AgentFlow MVP

## Prerequisites

Make sure you have:
- Python 3.11+
- Node.js 18+

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment (optional):
- The system runs in mock mode by default (no API key needed)
- To use OpenAI, edit `.env` and add your API key:
  ```
  OPENAI_API_KEY=your_api_key_here
  ```

5. Run the backend:
```bash
python main.py
```

The backend will start at http://localhost:8000

## Frontend Setup

1. In a new terminal, navigate to frontend:
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

The frontend will start at http://localhost:3000

## What to Expect

When running in mock mode:
- You'll see warnings in the console: "WARNING: OPENAI_API_KEY not set. Agent [Name] will run in mock mode."
- All agents will provide simulated responses
- The system is fully functional for testing and demos

## Available Agents

1. Process Automation Specialist
2. Decision Maker
3. Customer Service Specialist
4. Data Analyst
5. Compliance Officer
6. HR Recruitment Specialist
7. Financial Analyst

## Available Workflows

1. Purchase Approval Workflow
2. Customer Complaint Resolution
3. Monthly Financial Reporting
4. Recruitment Pipeline
5. Enterprise Risk Assessment

## Testing

Click any of the "Quick Examples" buttons in the Execute tab to see the system in action!

## Troubleshooting

If you see "Module not found" errors:
1. Make sure you're in the virtual environment
2. Run `pip install -r requirements.txt` again

If the frontend can't connect to backend:
1. Make sure the backend is running on port 8000
2. Check that no firewall is blocking the connection