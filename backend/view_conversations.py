#!/usr/bin/env python3
"""
View conversation history for AgentFlow agents
"""
import sys
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db
from models.conversation import Conversation, Message, AgentMemory

console = Console()

def list_agents_with_conversations():
    """List all agents that have conversations"""
    with get_db() as db:
        # Get unique agents from conversations
        agents = db.query(
            Conversation.agent_id,
            Conversation.agent_name
        ).distinct().all()
        
        if not agents:
            console.print("[yellow]No conversations found in database[/yellow]")
            return None
        
        table = Table(title="Agents with Conversations", show_header=True, header_style="bold magenta")
        table.add_column("Agent ID", style="cyan", width=40)
        table.add_column("Agent Name", style="green", width=30)
        table.add_column("Total Conversations", style="yellow", width=20)
        
        for agent_id, agent_name in agents:
            conv_count = db.query(Conversation).filter_by(agent_id=agent_id).count()
            table.add_row(agent_id, agent_name, str(conv_count))
        
        console.print(table)
        
        # Return list of agent IDs for selection
        return [(agent_id, agent_name) for agent_id, agent_name in agents]

def show_agent_conversations(agent_id: str, agent_name: str, limit: int = 10):
    """Show recent conversations for an agent"""
    with get_db() as db:
        conversations = db.query(Conversation).filter_by(
            agent_id=agent_id
        ).order_by(Conversation.started_at.desc()).limit(limit).all()
        
        if not conversations:
            console.print(f"[yellow]No conversations found for {agent_name}[/yellow]")
            return None
        
        table = Table(
            title=f"Recent Conversations for {agent_name}",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        table.add_column("ID", style="cyan", width=15)
        table.add_column("Started", style="green", width=20)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Messages", style="blue", width=10)
        table.add_column("Duration", style="white", width=15)
        
        conv_ids = []
        for conv in conversations:
            # Calculate duration
            duration = "N/A"
            if conv.ended_at and conv.started_at:
                delta = conv.ended_at - conv.started_at
                duration = f"{delta.total_seconds():.1f}s"
            
            # Count messages
            msg_count = len(conv.messages)
            
            # Format ID for display
            display_id = conv.id[:8] + "..."
            
            table.add_row(
                display_id,
                conv.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                conv.status,
                str(msg_count),
                duration
            )
            conv_ids.append(conv.id)
        
        console.print(table)
        return conv_ids

def show_conversation_messages(conversation_id: str):
    """Show messages in a conversation"""
    with get_db() as db:
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation:
            console.print("[red]Conversation not found[/red]")
            return
        
        messages = db.query(Message).filter_by(
            conversation_id=conversation_id
        ).order_by(Message.timestamp).all()
        
        # Create panel for conversation info
        info_text = f"""[bold]Agent:[/bold] {conversation.agent_name}
[bold]Started:[/bold] {conversation.started_at.strftime("%Y-%m-%d %H:%M:%S")}
[bold]Status:[/bold] {conversation.status}
[bold]Messages:[/bold] {len(messages)}"""
        
        console.print(Panel(info_text, title="Conversation Details", border_style="blue"))
        console.print("")
        
        # Display messages
        for msg in messages:
            # Format role with color
            role_color = {
                "human": "green",
                "ai": "blue",
                "system": "yellow",
                "tool": "magenta"
            }.get(msg.role, "white")
            
            # Format content (truncate if too long)
            content = msg.content
            if len(content) > 500:
                content = content[:497] + "..."
            
            # Create message panel
            title = f"[{role_color}]{msg.role.upper()}[/{role_color}] - {msg.timestamp.strftime('%H:%M:%S')}"
            if msg.model_used:
                title += f" [dim](model: {msg.model_used})[/dim]"
            
            console.print(Panel(
                content,
                title=title,
                border_style=role_color,
                box=box.ROUNDED
            ))
            console.print("")

def show_agent_memories(agent_id: str, agent_name: str):
    """Show stored memories for an agent"""
    with get_db() as db:
        memories = db.query(AgentMemory).filter_by(
            agent_id=agent_id
        ).order_by(AgentMemory.confidence.desc()).all()
        
        if not memories:
            console.print(f"[yellow]No memories found for {agent_name}[/yellow]")
            return
        
        table = Table(
            title=f"Stored Memories for {agent_name}",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Type", style="cyan", width=15)
        table.add_column("Key", style="green", width=30)
        table.add_column("Value", style="white", width=40)
        table.add_column("Confidence", style="yellow", width=12)
        table.add_column("Usage", style="blue", width=10)
        
        for memory in memories:
            # Format value (truncate if too long)
            value_str = str(memory.value)
            if len(value_str) > 40:
                value_str = value_str[:37] + "..."
            
            table.add_row(
                memory.memory_type,
                memory.key,
                value_str,
                f"{memory.confidence:.2f}",
                str(memory.usage_count)
            )
        
        console.print(table)

def interactive_mode():
    """Interactive mode to browse conversations"""
    console.print(Panel.fit(
        "[bold cyan]AgentFlow Conversation Viewer[/bold cyan]\n"
        "Browse and search through agent conversation history",
        border_style="cyan"
    ))
    
    while True:
        console.print("\n[bold]Options:[/bold]")
        console.print("1. List agents with conversations")
        console.print("2. View agent conversations")
        console.print("3. View conversation messages")
        console.print("4. View agent memories")
        console.print("5. Search conversations")
        console.print("0. Exit")
        
        choice = console.input("\n[cyan]Select option:[/cyan] ")
        
        if choice == "0":
            break
        elif choice == "1":
            list_agents_with_conversations()
        elif choice == "2":
            agents = list_agents_with_conversations()
            if agents:
                console.print("\nEnter agent number (1-{}): ".format(len(agents)), end="")
                idx = int(input()) - 1
                if 0 <= idx < len(agents):
                    agent_id, agent_name = agents[idx]
                    show_agent_conversations(agent_id, agent_name)
        elif choice == "3":
            conv_id = console.input("[cyan]Enter conversation ID:[/cyan] ")
            show_conversation_messages(conv_id)
        elif choice == "4":
            agents = list_agents_with_conversations()
            if agents:
                console.print("\nEnter agent number (1-{}): ".format(len(agents)), end="")
                idx = int(input()) - 1
                if 0 <= idx < len(agents):
                    agent_id, agent_name = agents[idx]
                    show_agent_memories(agent_id, agent_name)
        elif choice == "5":
            query = console.input("[cyan]Enter search query:[/cyan] ")
            search_conversations(query)

def search_conversations(query: str):
    """Search through all conversations"""
    with get_db() as db:
        messages = db.query(Message).filter(
            Message.content.ilike(f'%{query}%')
        ).join(Conversation).limit(20).all()
        
        if not messages:
            console.print(f"[yellow]No messages found matching '{query}'[/yellow]")
            return
        
        console.print(f"\n[bold]Found {len(messages)} messages matching '{query}':[/bold]\n")
        
        for msg in messages:
            # Get conversation info
            conv = msg.conversation
            
            # Highlight matching text
            content = msg.content
            if len(content) > 200:
                # Find position of query and show context
                pos = content.lower().find(query.lower())
                if pos > 50:
                    content = "..." + content[pos-50:pos+150] + "..."
                else:
                    content = content[:200] + "..."
            
            # Highlight the query in content
            import re
            content = re.sub(f'({re.escape(query)})', r'[bold yellow]\1[/bold yellow]', content, flags=re.IGNORECASE)
            
            panel_content = f"""[bold]Agent:[/bold] {conv.agent_name}
[bold]Date:[/bold] {msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
[bold]Role:[/bold] {msg.role}

{content}"""
            
            console.print(Panel(
                panel_content,
                title=f"Match in conversation {conv.id[:8]}...",
                border_style="yellow"
            ))
            console.print("")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View AgentFlow conversation history")
    parser.add_argument("--agent", help="Show conversations for specific agent ID")
    parser.add_argument("--conversation", help="Show messages in specific conversation")
    parser.add_argument("--search", help="Search for text in conversations")
    parser.add_argument("--memories", help="Show memories for specific agent ID")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive or not any([args.agent, args.conversation, args.search, args.memories]):
        interactive_mode()
    elif args.agent:
        show_agent_conversations(args.agent, "Agent", limit=20)
    elif args.conversation:
        show_conversation_messages(args.conversation)
    elif args.search:
        search_conversations(args.search)
    elif args.memories:
        show_agent_memories(args.memories, "Agent")