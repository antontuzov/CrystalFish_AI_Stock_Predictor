"""
User schemas for CrystalFish
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    use_default_models: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_verified: bool
    use_default_models: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: Optional[int] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None