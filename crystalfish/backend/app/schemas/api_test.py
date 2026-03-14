"""
API Test Dashboard Schemas
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class ApiEndpointTest(BaseModel):
    """API endpoint test result"""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None


class ApiHealthStatus(BaseModel):
    """API health status"""
    status: str = "healthy"  # healthy, degraded, unhealthy
    version: str
    uptime_seconds: float
    timestamp: datetime
    endpoints_tested: int
    endpoints_passed: int
    average_response_time_ms: float


class ApiTestDashboardState(BaseModel):
    """API Test Dashboard state"""
    is_monitoring: bool = False
    test_interval_seconds: int = 30
    last_test_time: Optional[datetime] = None
    total_tests_run: int = 0
    success_rate: float = 0.0
    average_response_time_ms: float = 0.0
    recent_failures: List[Dict[str, Any]] = Field(default_factory=list)


class ApiTestRequest(BaseModel):
    """API test request"""
    endpoint: str = Field(..., description="API endpoint to test")
    method: str = Field(default="GET", description="HTTP method")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Request payload")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Request headers")
    timeout_seconds: int = Field(default=10, description="Request timeout")


class ApiTestResponse(BaseModel):
    """API test response"""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    response_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime


class ApiMetric(BaseModel):
    """API metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Optional[Dict[str, str]] = None


class ApiTestDashboardResponse(BaseModel):
    """API Test Dashboard response"""
    health: ApiHealthStatus
    state: ApiTestDashboardState
    recent_tests: List[ApiTestResponse]
    metrics: List[ApiMetric]
    recommendations: List[str]
