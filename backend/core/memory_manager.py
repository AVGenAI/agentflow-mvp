"""
Memory manager for agent conversation persistence
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import json

from models.conversation import Conversation, Message, AgentMemory
from database.connection import get_db

class MemoryManager:
    """Manages persistent memory for agents"""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.current_conversation_id = None
    
    def start_conversation(self, workflow_id: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """Start a new conversation session"""
        with get_db() as db:
            conversation = Conversation(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                workflow_id=workflow_id,
                meta_data=metadata or {}
            )
            db.add(conversation)
            db.commit()
            self.current_conversation_id = conversation.id
            return conversation.id
    
    def end_conversation(self, status: str = 'completed'):
        """End the current conversation"""
        if not self.current_conversation_id:
            return
            
        with get_db() as db:
            conversation = db.query(Conversation).filter_by(id=self.current_conversation_id).first()
            if conversation:
                conversation.ended_at = datetime.utcnow()
                conversation.status = status
                db.commit()
            self.current_conversation_id = None
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None,
                   model_used: Optional[str] = None, temperature: Optional[float] = None) -> str:
        """Add a message to the current conversation"""
        if not self.current_conversation_id:
            self.start_conversation()
        
        with get_db() as db:
            # Estimate token count (rough approximation)
            token_count = len(content.split()) * 1.3
            
            message = Message(
                conversation_id=self.current_conversation_id,
                role=role,
                content=content,
                token_count=int(token_count),
                model_used=model_used,
                temperature=temperature,
                meta_data=metadata or {}
            )
            db.add(message)
            db.commit()
            return message.id
    
    def get_conversation_history(self, conversation_id: Optional[str] = None, 
                               limit: int = 50) -> List[Dict]:
        """Get message history for a conversation"""
        conv_id = conversation_id or self.current_conversation_id
        if not conv_id:
            return []
        
        with get_db() as db:
            messages = db.query(Message).filter_by(
                conversation_id=conv_id
            ).order_by(Message.timestamp).limit(limit).all()
            
            return [msg.to_dict() for msg in messages]
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations for this agent"""
        with get_db() as db:
            conversations = db.query(Conversation).filter_by(
                agent_id=self.agent_id
            ).order_by(desc(Conversation.started_at)).limit(limit).all()
            
            return [conv.to_dict() for conv in conversations]
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Search through conversation history"""
        with get_db() as db:
            messages = db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.agent_id == self.agent_id,
                    Message.content.ilike(f'%{query}%')
                )
            ).order_by(desc(Message.timestamp)).limit(limit).all()
            
            results = []
            for msg in messages:
                result = msg.to_dict()
                result['conversation'] = msg.conversation.to_dict()
                results.append(result)
            
            return results
    
    def store_memory(self, memory_type: str, key: str, value: Any, 
                    confidence: float = 1.0, expires_in_days: Optional[int] = None):
        """Store a learned pattern or insight"""
        with get_db() as db:
            # Check if memory already exists
            existing = db.query(AgentMemory).filter_by(
                agent_id=self.agent_id,
                memory_type=memory_type,
                key=key
            ).first()
            
            if existing:
                # Update existing memory
                existing.value = value
                existing.confidence = max(existing.confidence, confidence)
                existing.usage_count += 1
                existing.updated_at = datetime.utcnow()
                if expires_in_days:
                    existing.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            else:
                # Create new memory
                memory = AgentMemory(
                    agent_id=self.agent_id,
                    memory_type=memory_type,
                    key=key,
                    value=value,
                    confidence=confidence,
                    source_conversation_id=self.current_conversation_id,
                    expires_at=datetime.utcnow() + timedelta(days=expires_in_days) if expires_in_days else None
                )
                db.add(memory)
            
            db.commit()
    
    def recall_memory(self, memory_type: Optional[str] = None, 
                     key: Optional[str] = None) -> List[Dict]:
        """Recall stored memories"""
        with get_db() as db:
            query = db.query(AgentMemory).filter_by(agent_id=self.agent_id)
            
            if memory_type:
                query = query.filter_by(memory_type=memory_type)
            if key:
                query = query.filter(AgentMemory.key.ilike(f'%{key}%'))
            
            # Filter out expired memories
            query = query.filter(
                (AgentMemory.expires_at.is_(None)) | 
                (AgentMemory.expires_at > datetime.utcnow())
            )
            
            memories = query.order_by(desc(AgentMemory.confidence)).all()
            
            # Update usage count
            for memory in memories:
                memory.usage_count += 1
            db.commit()
            
            return [mem.to_dict() for mem in memories]
    
    def get_context_summary(self, max_messages: int = 10) -> str:
        """Get a summary of recent context for the agent"""
        recent_messages = self.get_conversation_history(limit=max_messages)
        
        if not recent_messages:
            return "No previous context available."
        
        summary = f"Recent conversation context ({len(recent_messages)} messages):\n"
        for msg in recent_messages[-5:]:  # Last 5 messages
            role = msg['role'].upper()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            summary += f"{role}: {content}\n"
        
        # Add relevant memories
        memories = self.recall_memory()[:3]  # Top 3 memories
        if memories:
            summary += "\nRelevant memories:\n"
            for mem in memories:
                summary += f"- {mem['key']}: {json.dumps(mem['value'])[:100]}...\n"
        
        return summary
    
    def cleanup_old_conversations(self, days_to_keep: int = 30):
        """Clean up old conversations and messages"""
        with get_db() as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old conversations (messages cascade delete)
            old_conversations = db.query(Conversation).filter(
                and_(
                    Conversation.agent_id == self.agent_id,
                    Conversation.ended_at < cutoff_date
                )
            ).all()
            
            for conv in old_conversations:
                db.delete(conv)
            
            # Delete expired memories
            expired_memories = db.query(AgentMemory).filter(
                and_(
                    AgentMemory.agent_id == self.agent_id,
                    AgentMemory.expires_at < datetime.utcnow()
                )
            ).all()
            
            for mem in expired_memories:
                db.delete(mem)
            
            db.commit()
            
            return {
                'conversations_deleted': len(old_conversations),
                'memories_deleted': len(expired_memories)
            }