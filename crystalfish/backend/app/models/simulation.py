"""
Simulation model for CrystalFish
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class SimulationStatus(str, enum.Enum):
    """Simulation status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Simulation(Base):
    """Simulation model"""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Asset info
    asset_symbol = Column(String(50), nullable=False)  # BTC, ETH, AAPL, etc.
    asset_type = Column(String(20), nullable=False)  # crypto, stock
    
    # Simulation parameters
    time_horizon_days = Column(Integer, default=7)
    confidence_level = Column(Float, default=0.95)
    agents_count = Column(Integer, default=100)
    
    # Agent personality distribution
    personality_distribution = Column(JSON, default={
        "bullish": 0.25,
        "bearish": 0.25,
        "neutral": 0.25,
        "trend_follower": 0.15,
        "contrarian": 0.10
    })
    
    # Data sources
    data_source = Column(String(50), default="yahoo")  # yahoo, coingecko, upload
    uploaded_data_path = Column(String(500), nullable=True)
    
    # Status
    status = Column(Enum(SimulationStatus), default=SimulationStatus.PENDING)
    progress_percent = Column(Float, default=0.0)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    
    # Error info
    error_message = Column(Text, nullable=True)
    
    # Results
    results = Column(JSON, nullable=True)
    prediction_chart_data = Column(JSON, nullable=True)
    agent_sentiment_history = Column(JSON, nullable=True)
    
    # Math model results
    math_model_results = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="simulations")
    agents = relationship("Agent", back_populates="simulation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Simulation(id={self.id}, name={self.name}, status={self.status})>"