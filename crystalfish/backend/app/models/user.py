"""
User model for CrystalFish
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    
    # OAuth providers
    google_id = Column(String(255), unique=True, nullable=True)
    
    # API Keys
    openrouter_api_key = Column(String(255), nullable=True)
    use_default_models = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    simulations = relationship("Simulation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"