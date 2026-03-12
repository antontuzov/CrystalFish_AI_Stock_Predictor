"""
Simulation schemas for CrystalFish
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SimulationStatus(str, Enum):
    """Simulation status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PersonalityDistribution(BaseModel):
    """Personality distribution for agents"""
    bullish: float = Field(0.25, ge=0, le=1)
    bearish: float = Field(0.25, ge=0, le=1)
    neutral: float = Field(0.25, ge=0, le=1)
    trend_follower: float = Field(0.15, ge=0, le=1)
    contrarian: float = Field(0.10, ge=0, le=1)


class SimulationCreate(BaseModel):
    """Simulation creation schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    asset_symbol: str = Field(..., min_length=1, max_length=50)
    asset_type: str = Field(..., pattern="^(crypto|stock)$")
    time_horizon_days: int = Field(7, ge=1, le=90)
    confidence_level: float = Field(0.95, ge=0.5, le=0.99)
    agents_count: int = Field(100, ge=10, le=500)
    personality_distribution: PersonalityDistribution = Field(default_factory=PersonalityDistribution)
    data_source: str = Field("yahoo", pattern="^(yahoo|coingecko|upload)$")


class SimulationUpdate(BaseModel):
    """Simulation update schema"""
    name: Optional[str] = None
    description: Optional[str] = None


class SimulationResponse(BaseModel):
    """Simulation response schema"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    asset_symbol: str
    asset_type: str
    time_horizon_days: int
    confidence_level: float
    agents_count: int
    personality_distribution: Dict[str, float]
    data_source: str
    status: SimulationStatus
    progress_percent: float
    current_step: int
    total_steps: int
    error_message: Optional[str]
    results: Optional[Dict[str, Any]]
    prediction_chart_data: Optional[Dict[str, Any]]
    agent_sentiment_history: Optional[List[Dict[str, Any]]]
    math_model_results: Optional[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SimulationListResponse(BaseModel):
    """Simulation list response"""
    id: int
    name: str
    asset_symbol: str
    asset_type: str
    status: SimulationStatus
    progress_percent: float
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SimulationProgressUpdate(BaseModel):
    """Simulation progress update (WebSocket)"""
    simulation_id: int
    status: SimulationStatus
    progress_percent: float
    current_step: int
    total_steps: int
    message: Optional[str] = None
    log_entry: Optional[str] = None


class PredictionResult(BaseModel):
    """Prediction result schema"""
    date: str
    predicted_price: float
    lower_bound: float
    upper_bound: float
    confidence: float


class AgentSentimentPoint(BaseModel):
    """Agent sentiment at a point in time"""
    step: int
    date: str
    bullish_percent: float
    bearish_percent: float
    neutral_percent: float
    average_confidence: float


class SimulationResults(BaseModel):
    """Complete simulation results"""
    simulation_id: int
    predictions: List[PredictionResult]
    sentiment_history: List[AgentSentimentPoint]
    final_price_prediction: float
    price_change_percent: float
    confidence_interval: Dict[str, float]
    key_factors: List[str]
    top_agents: List[Dict[str, Any]]
    math_model_comparison: Dict[str, Any]