# LLM Setup Guide for AgentFlow

AgentFlow supports multiple LLM providers for maximum flexibility. Choose the option that best fits your needs.

## Available Providers

### 1. Ollama (Recommended for Local Testing)
**Pros**: Free, runs locally, no API limits, privacy-friendly  
**Cons**: Requires local resources, slower than cloud APIs

#### Installation
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

#### Quick Setup
```bash
# Run the setup script
./setup_ollama.sh

# Or manually:
ollama serve  # Start Ollama server
ollama pull llama2  # Download a model
```

#### Configuration (.env)
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2  # or mistral, mixtral, codellama
OLLAMA_BASE_URL=http://localhost:11434
```

#### Recommended Models
- **llama2** (7B): Good balance of speed and quality
- **mistral** (7B): Fast and efficient
- **mixtral** (8x7B): Higher quality but slower
- **codellama** (7B): Optimized for code tasks
- **neural-chat** (7B): Good for conversational tasks

### 2. OpenAI
**Pros**: Best quality, fast responses  
**Cons**: Requires API key, costs money

#### Setup
1. Get API key from https://platform.openai.com/api-keys
2. Configure in `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...your-key-here...
OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo
```

### 3. Mock Mode (Default)
**Pros**: No setup required, instant responses  
**Cons**: Simulated responses only

#### Configuration
```
LLM_PROVIDER=mock
```

## Testing Your Setup

### Check Current Configuration
```bash
curl http://localhost:8000/api/llm/providers
```

### List Available Models
```bash
# For Ollama
curl http://localhost:8000/api/llm/models/ollama

# For OpenAI
curl http://localhost:8000/api/llm/models/openai
```

### Test an Agent
```bash
curl -X POST http://localhost:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "your-agent-id",
    "input_data": {"task": "Test the LLM connection"}
  }'
```

## Performance Comparison

| Provider | Speed | Quality | Cost | Privacy |
|----------|-------|---------|------|---------|
| Ollama/llama2 | Medium | Good | Free | 100% Local |
| Ollama/mistral | Fast | Good | Free | 100% Local |
| OpenAI GPT-4 | Fast | Excellent | $$$ | Cloud |
| OpenAI GPT-3.5 | Very Fast | Very Good | $$ | Cloud |
| Mock Mode | Instant | Simulated | Free | Local |

## Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# View logs
journalctl -u ollama  # Linux
brew services info ollama  # macOS

# Restart Ollama
ollama serve
```

### Memory Issues with Ollama
If you get out-of-memory errors:
1. Try a smaller model (e.g., use llama2:7b instead of llama2:13b)
2. Close other applications
3. Adjust Ollama memory settings

### OpenAI Rate Limits
If you hit rate limits:
1. Add delays between requests
2. Upgrade your OpenAI plan
3. Switch to Ollama for development

## Advanced Configuration

### Using Multiple Providers
You can configure different agents to use different providers by modifying the agent config:

```python
config = AgentConfig(
    name="My Agent",
    llm_provider="ollama",  # Override default provider
    model_name="codellama",  # Use specific model
    # ... other config
)
```

### Custom Ollama Models
Create custom models with specific parameters:
```bash
# Create a Modelfile
cat > Modelfile << EOF
FROM llama2
PARAMETER temperature 0.2
PARAMETER top_p 0.9
SYSTEM "You are a helpful business assistant."
EOF

# Create custom model
ollama create business-assistant -f Modelfile
```

Then use in `.env`:
```
OLLAMA_MODEL=business-assistant
```

## Best Practices

1. **Development**: Use Ollama for cost-free local testing
2. **Production**: Consider OpenAI for best quality
3. **Demo/POC**: Mock mode is perfect for demonstrations
4. **Privacy-sensitive**: Always use Ollama or on-premise solutions

## Next Steps

1. Choose your preferred provider
2. Run the examples to test the setup
3. Create custom agents optimized for your LLM choice
4. Monitor performance and adjust as needed