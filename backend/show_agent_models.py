#!/usr/bin/env python3
"""
Display current agent-model configuration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.models import AGENT_MODEL_CONFIG, DEFAULT_MODEL_CONFIG
from rich.console import Console
from rich.table import Table

console = Console()

def show_agent_models():
    """Display agent model configuration in a nice table"""
    
    # Create table
    table = Table(title="AgentFlow Model Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Agent ID", style="cyan", width=30)
    table.add_column("Model", style="green", width=20)
    table.add_column("Temperature", style="yellow", width=12)
    table.add_column("Optimization", style="white", width=40)
    
    # Add agent configurations
    for agent_id, config in AGENT_MODEL_CONFIG.items():
        table.add_row(
            agent_id,
            config["model"],
            str(config["temperature"]),
            config["description"]
        )
    
    # Add default configuration
    table.add_row(
        "[dim]default (fallback)[/dim]",
        DEFAULT_MODEL_CONFIG["model"],
        str(DEFAULT_MODEL_CONFIG["temperature"]),
        DEFAULT_MODEL_CONFIG.get("description", "Default configuration")
    )
    
    console.print(table)
    
    # Show memory requirements
    console.print("\n[bold]Memory Requirements:[/bold]")
    memory_map = {
        "qwen2.5:14b": "~16GB VRAM",
        "qwen2.5:7b": "~8GB VRAM",
        "llama3.1:8b": "~8GB VRAM",
        "mistral:7b": "~8GB VRAM",
        "gemma2:9b": "~10GB VRAM"
    }
    
    used_models = set(config["model"] for config in AGENT_MODEL_CONFIG.values())
    total_memory = 0
    
    for model in used_models:
        mem = memory_map.get(model, "Unknown")
        console.print(f"  • {model}: {mem}")
        if mem != "Unknown":
            total_memory += int(mem.split("~")[1].split("GB")[0])
    
    console.print(f"\n[bold]Estimated Total VRAM:[/bold] ~{total_memory}GB (if all agents run simultaneously)")
    console.print("[dim]Note: Models are loaded on-demand, actual usage will be lower[/dim]")
    
    # Show installation status
    console.print("\n[bold]Model Installation Status:[/bold]")
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            installed_models = [line.split()[0] for line in result.stdout.strip().split('\n')[1:]]
            for model in used_models:
                status = "✅ Installed" if any(model in installed for installed in installed_models) else "❌ Not installed"
                console.print(f"  • {model}: {status}")
        else:
            console.print("[red]Could not check Ollama status[/red]")
    except:
        console.print("[yellow]Ollama not available - run 'ollama list' to check installed models[/yellow]")

if __name__ == "__main__":
    show_agent_models()