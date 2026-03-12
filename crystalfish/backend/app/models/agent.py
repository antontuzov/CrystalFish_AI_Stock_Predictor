"""
Agent model for CrystalFish
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Agent(Base):
    """Agent model - represents a single AI agent in the swarm"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    
    # Agent identity
    name = Column(String(100), nullable=False)
    avatar_type = Column(String(50), default="fish")  # fish, octopus, dolphin, turtle, seahorse
    
    # Personality
    personality = Column(String(50), nullable=False)  # bullish, bearish, neutral, trend_follower, contrarian
    persona_description = Column(Text, nullable=False)
    
    # Agent state
    initial_capital = Column(Float, default=10000.0)
    current_capital = Column(Float, default=10000.0)
    position = Column(Float, default=0.0)  # Current position in asset
    
    # Memory and history
    memory = Column(JSON, default=list)  # List of past observations/decisions
    trade_history = Column(JSON, default=list)  # List of trades
    
    # Current decision
    current_decision = Column(String(20), default="hold")  # buy, sell, hold
    current_confidence = Column(Float, default=0.5)
    reasoning = Column(Text, nullable=True)
    
    # Performance
    total_return = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="agents")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, personality={self.personality})>"
    
    def to_dict(self):
        """Convert agent to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "avatar_type": self.avatar_type,
            "personality": self.personality,
            "persona_description": self.persona_description,
            "current_capital": self.current_capital,
            "position": self.position,
            "current_decision": self.current_decision,
            "current_confidence": self.current_confidence,
            "reasoning": self.reasoning,
            "total_return": self.total_return,
        }