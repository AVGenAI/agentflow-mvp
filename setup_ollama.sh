#!/bin/bash
# Setup script for Ollama

echo "🚀 AgentFlow Ollama Setup"
echo "========================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo ""
    echo "Please install Ollama first:"
    echo "  - macOS: brew install ollama"
    echo "  - Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  - Or visit: https://ollama.com/download"
    exit 1
fi

echo "✅ Ollama is installed"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama server is not running. Starting it now..."
    ollama serve &
    sleep 5
fi

echo "✅ Ollama server is running"

# List available models
echo ""
echo "📦 Currently installed models:"
ollama list

# Recommend models for AgentFlow
echo ""
echo "🎯 Recommended models for AgentFlow:"
echo "  1. llama2 (7B) - Good balance of speed and quality"
echo "  2. mistral (7B) - Fast and efficient"
echo "  3. mixtral (8x7B) - Higher quality but slower"
echo "  4. codellama (7B) - Good for code-related tasks"

# Ask user which model to pull
echo ""
read -p "Which model would you like to install? (e.g., llama2): " model_choice

if [ ! -z "$model_choice" ]; then
    echo "📥 Pulling $model_choice..."
    ollama pull $model_choice
    
    # Update .env file if it exists
    if [ -f .env ]; then
        echo ""
        echo "📝 Updating .env file..."
        sed -i.bak "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$model_choice/" .env
        echo "✅ Updated OLLAMA_MODEL to $model_choice"
    fi
fi

echo ""
echo "✅ Ollama setup complete!"
echo ""
echo "To use Ollama with AgentFlow:"
echo "1. Make sure your .env file contains:"
echo "   LLM_PROVIDER=ollama"
echo "   OLLAMA_MODEL=$model_choice"
echo "2. Start the backend: python main.py"
echo ""
echo "Happy coding! 🎉"