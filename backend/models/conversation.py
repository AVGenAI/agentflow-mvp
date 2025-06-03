"""
Database models for conversation persistence
"""
from sqlalchemy import Column, String, Text, DateTime, JSON, Float, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Conversation(Base):
    """Store conversation sessions"""
    __tablename__ = 'conversations'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    workflow_id = Column(String, nullable=True)  # If part of a workflow
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default='active')  # active, completed, failed
    meta_data = Column(JSON, nullable=True)  # Store additional context
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'workflow_id': self.workflow_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'status': self.status,
            'metadata': self.meta_data,
            'message_count': len(self.messages)
        }

class Message(Base):
    """Store individual messages in conversations"""
    __tablename__ = 'messages'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey('conversations.id'), nullable=False, index=True)
    role = Column(String, nullable=False)  # human, ai, system, tool
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    token_count = Column(Integer, nullable=True)
    model_used = Column(String, nullable=True)
    temperature = Column(Float, nullable=True)
    meta_data = Column(JSON, nullable=True)  # Store tool calls, function results, etc.
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'token_count': self.token_count,
            'model_used': self.model_used,
            'temperature': self.temperature,
            'metadata': self.meta_data
        }

class AgentMemory(Base):
    """Store agent-specific learned patterns and insights"""
    __tablename__ = 'agent_memory'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, nullable=False, index=True)
    memory_type = Column(String, nullable=False)  # fact, pattern, preference, insight
    key = Column(String, nullable=False)  # What this memory is about
    value = Column(JSON, nullable=False)  # The actual memory content
    confidence = Column(Float, default=1.0)  # How confident the agent is
    usage_count = Column(Integer, default=0)  # How often this memory is accessed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    source_conversation_id = Column(String, nullable=True)  # Where this was learned
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'memory_type': self.memory_type,
            'key': self.key,
            'value': self.value,
            'confidence': self.confidence,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'source_conversation_id': self.source_conversation_id
        }