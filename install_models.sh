#!/bin/bash

echo "🚀 Installing Ollama models for AgentFlow MVP"
echo "============================================"
echo ""
echo "This will install optimized models for each agent type."
echo "Total download size: ~40GB (all models)"
echo ""

# Function to install a model with status
install_model() {
    local model=$1
    local description=$2
    echo -n "📦 Installing $model - $description... "
    if ollama pull "$model" > /dev/null 2>&1; then
        echo "✅ Done"
    else
        echo "❌ Failed"
    fi
}

# Check if Ollama is running
if ! ollama list > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start it with: ollama serve"
    exit 1
fi

echo "Starting model installation..."
echo ""

# Install models based on priority and usage
echo "🔷 Core Models (Recommended):"
install_model "qwen2.5:14b" "Best for document processing & analysis"
install_model "qwen2.5:7b" "Lighter version for compliance & automation"
install_model "llama3.1:8b" "Customer service & HR tasks"

echo ""
echo "🔶 Additional Models (Optional):"
read -p "Install additional specialized models? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    install_model "mistral:7b" "Fast process automation"
    install_model "gemma2:9b" "Quality assurance"
fi

echo ""
echo "📊 Model Installation Summary:"
echo "=============================="
ollama list

echo ""
echo "✅ Model installation complete!"
echo ""
echo "🎯 Agent-Model Mapping:"
echo "- Document Intelligence → qwen2.5:14b"
echo "- Data Analysis → qwen2.5:14b"
echo "- Financial Analysis → qwen2.5:14b"
echo "- Decision Support → qwen2.5:14b"
echo "- Customer Service → llama3.1:8b"
echo "- HR Recruitment → llama3.1:8b"
echo "- Compliance Monitor → qwen2.5:7b"
echo "- Process Automation → mistral:7b (or qwen2.5:7b)"
echo "- Quality Assurance → gemma2:9b (or qwen2.5:7b)"
echo ""
echo "🔧 To test: docker-compose up -d"