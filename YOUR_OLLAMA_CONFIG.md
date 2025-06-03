# Your Ollama Configuration for AgentFlow

## ✅ Ollama Status
- **Status**: Running and ready
- **Available Models**: 11 models installed
- **Connection**: Verified at http://localhost:11434

## Your Available Models

### For General Purpose Agents:
- **llama2:latest** - Currently configured (good balance)
- **llama3.2:latest** - Newer, potentially better quality
- **gemma3:12b** - Google's model, good for reasoning

### For Coding/Technical Agents:
- **qwen2.5-coder:7b-instruct** - Optimized for code
- **codellama:34b** - Large code-focused model
- **devstral:latest** - Development focused
- **okamototk/deepcoder:14b** - Deep coding model

### Premium Models:
- **llama4:16x17b** - Very large, high quality
- **GandalfBaum/llama3.1-claude3.7:latest** - Claude-style responses
- **deepseek-r1:7b** - Advanced reasoning

## Quick Start

Your `.env` is already configured:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2:latest
```

To use a different model, just change `OLLAMA_MODEL`. For example:
- For better quality: `OLLAMA_MODEL=llama3.2:latest`
- For coding tasks: `OLLAMA_MODEL=qwen2.5-coder:7b-instruct`
- For complex reasoning: `OLLAMA_MODEL=deepseek-r1:7b`

## Recommended Model Selection by Agent Type

### Customer Service Agent
Use: `llama3.2:latest` or `GandalfBaum/llama3.1-claude3.7:latest`

### Data Analyst Agent
Use: `gemma3:12b` or `deepseek-r1:7b`

### Financial Analyst Agent
Use: `llama4:16x17b` (for accuracy) or `gemma3:12b`

### HR Recruitment Agent
Use: `llama2:latest` or `llama3.2:latest`

### Compliance Officer Agent
Use: `llama4:16x17b` (for precision) or `deepseek-r1:7b`

### Process Automation Agent
Use: `qwen2.5-coder:7b-instruct` or `codellama:34b`

## Performance Tips

1. **Faster responses**: Use smaller models (7b parameters)
2. **Better quality**: Use larger models (12b+ parameters)
3. **Coding tasks**: Use specialized coding models
4. **Memory usage**: Monitor with `ollama ps`

## Testing Your Setup

1. Start the backend:
```bash
cd backend
python main.py
```

2. The console will show which models are being used by each agent

3. Try the examples in the UI - they'll now use your local Ollama models!

## Switching Models on the Fly

You can create agent-specific model configurations by modifying the agent initialization. For example, to use a specific model for the coding agent:

```python
config = AgentConfig(
    name="Code Expert",
    llm_provider="ollama",
    model_name="qwen2.5-coder:7b-instruct",
    # ... rest of config
)
```

Enjoy your local, private AI agents! 🚀