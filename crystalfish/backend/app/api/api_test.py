"""
API Test Dashboard routes for CrystalFish
Provides real-time API testing and monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from datetime import datetime
import asyncio

from app.schemas.api_test import (
    ApiTestRequest,
    ApiTestResponse,
    ApiTestDashboardResponse,
    ApiHealthStatus,
    ApiTestDashboardState
)
from app.services.api_test import get_api_tester, ApiTester
from app.services.api_dashboard_agent import get_api_dashboard_agent, ApiTestDashboardAgent

router = APIRouter(prefix="/api-test", tags=["API Test Dashboard"])


@router.get("/health", response_model=ApiHealthStatus)
async def get_health_status(api_tester: ApiTester = Depends(get_api_tester)):
    """Get current API health status (public endpoint)"""
    return api_tester.get_health_status()


@router.get("/dashboard")
async def get_dashboard(
    api_tester: ApiTester = Depends(get_api_tester)
):
    """Get complete API test dashboard data (public endpoint)"""
    return api_tester.get_dashboard_data()


@router.post("/test", response_model=ApiTestResponse)
async def test_endpoint(
    test_request: ApiTestRequest,
    api_tester: ApiTester = Depends(get_api_tester)
):
    """
    Test a specific API endpoint

    - **endpoint**: API endpoint path (e.g., /health, /api/v1/auth/login)
    - **method**: HTTP method (GET, POST, PUT, DELETE)
    - **payload**: Optional JSON payload for POST/PUT requests
    - **headers**: Optional HTTP headers
    - **timeout_seconds**: Request timeout in seconds
    """
    result = await api_tester.test_endpoint(
        endpoint=test_request.endpoint,
        method=test_request.method,
        payload=test_request.payload,
        headers=test_request.headers,
        timeout=test_request.timeout_seconds
    )

    return ApiTestResponse(
        endpoint=result["endpoint"],
        method=result["method"],
        status_code=result["status_code"],
        response_time_ms=result["response_time_ms"],
        success=result["success"],
        response_data=result.get("response_data"),
        error=result.get("error"),
        timestamp=datetime.fromisoformat(result["timestamp"])
    )


@router.post("/test-all", response_model=List[ApiTestResponse])
async def test_all_endpoints(
    api_tester: ApiTester = Depends(get_api_tester)
):
    """Run tests on all monitored endpoints"""
    results = await api_tester.run_full_test_suite()

    return [
        ApiTestResponse(
            endpoint=r["endpoint"],
            method=r["method"],
            status_code=r["status_code"],
            response_time_ms=r["response_time_ms"],
            success=r["success"],
            response_data=r.get("response_data"),
            error=r.get("error"),
            timestamp=datetime.fromisoformat(r["timestamp"])
        )
        for r in results
    ]


@router.post("/monitoring/start")
async def start_monitoring(
    interval: int = 30,
    api_tester: ApiTester = Depends(get_api_tester)
):
    """
    Start continuous API monitoring

    - **interval**: Test interval in seconds (default: 30)
    """
    await api_tester.start_monitoring(interval=interval)
    return {
        "status": "monitoring_started",
        "interval_seconds": interval,
        "message": f"API monitoring started with {interval}s interval"
    }


@router.post("/monitoring/stop")
async def stop_monitoring(
    api_tester: ApiTester = Depends(get_api_tester)
):
    """Stop continuous API monitoring"""
    await api_tester.stop_monitoring()
    return {
        "status": "monitoring_stopped",
        "message": "API monitoring stopped"
    }


@router.get("/monitoring/status")
async def get_monitoring_status(
    api_tester: ApiTester = Depends(get_api_tester)
):
    """Get current monitoring status"""
    return {
        "is_monitoring": api_tester.is_monitoring,
        "test_interval_seconds": api_tester.test_interval,
        "total_tests_run": len(api_tester.test_results),
        "monitored_endpoints": api_tester.monitored_endpoints
    }


@router.get("/metrics")
async def get_metrics(
    api_tester: ApiTester = Depends(get_api_tester)
):
    """Get API performance metrics"""
    return {
        "response_times": api_tester.metrics["response_times"][-50:],  # Last 50
        "success_rates": api_tester.metrics["success_rates"][-50:],
        "error_counts": api_tester.metrics["error_counts"][-50:]
    }


@router.get("/recent-tests", response_model=List[ApiTestResponse])
async def get_recent_tests(
    limit: int = 20,
    api_tester: ApiTester = Depends(get_api_tester)
):
    """Get recent test results"""
    recent = api_tester.test_results[-limit:] if api_tester.test_results else []

    return [
        ApiTestResponse(
            endpoint=r["endpoint"],
            method=r["method"],
            status_code=r["status_code"],
            response_time_ms=r["response_time_ms"],
            success=r["success"],
            response_data=r.get("response_data"),
            error=r.get("error"),
            timestamp=datetime.fromisoformat(r["timestamp"])
        )
        for r in recent
    ]


@router.get("/endpoints")
async def get_monitored_endpoints(
    api_tester: ApiTester = Depends(get_api_tester)
):
    """Get list of monitored endpoints"""
    return {
        "endpoints": api_tester.monitored_endpoints,
        "total": len(api_tester.monitored_endpoints)
    }


@router.get("/agent/summary")
async def get_agent_summary(
    agent: ApiTestDashboardAgent = Depends(get_api_dashboard_agent)
):
    """Get API Dashboard Agent summary"""
    return await agent.get_dashboard_summary()


@router.post("/agent/analyze")
async def run_analysis(
    agent: ApiTestDashboardAgent = Depends(get_api_dashboard_agent)
):
    """Run API health analysis"""
    return await agent.analyze_api_health()


@router.post("/agent/chat")
async def chat_with_agent(
    message: str,
    agent: ApiTestDashboardAgent = Depends(get_api_dashboard_agent)
):
    """Chat with the API Dashboard Agent"""
    response = await agent.chat_about_api(message)
    return {
        "agent_name": agent.name,
        "response": response,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/agent/alerts")
async def get_alerts(
    limit: int = 20,
    agent: ApiTestDashboardAgent = Depends(get_api_dashboard_agent)
):
    """Get recent alerts"""
    return {
        "alerts": agent.alerts[-limit:],
        "total": len(agent.alerts)
    }
