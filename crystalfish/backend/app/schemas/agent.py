"""
Agent schemas for CrystalFish
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class AgentBase(BaseModel):
    """Base agent schema"""
    name: str
    avatar_type: str
    personality: str
    persona_description: str


class AgentCreate(AgentBase):
    """Agent creation schema"""
    simulation_id: int
    initial_capital: float = 10000.0


class AgentResponse(AgentBase):
    """Agent response schema"""
    id: int
    simulation_id: int
    current_capital: float
    position: float
    current_decision: str
    current_confidence: float
    reasoning: Optional[str]
    total_return: float
    sharpe_ratio: float
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AgentDetailResponse(AgentResponse):
    """Detailed agent response with memory"""
    memory: List[Dict[str, Any]]
    trade_history: List[Dict[str, Any]]


class AgentDecision(BaseModel):
    """Agent decision schema"""
    decision: str  # buy, sell, hold
    confidence: float
    reasoning: str
    target_position: Optional[float] = None


class AgentChatMessage(BaseModel):
    """Agent chat message"""
    message: str


class AgentChatResponse(BaseModel):
    """Agent chat response"""
    agent_id: int
    agent_name: str
    response: str
    timestamp: datetime