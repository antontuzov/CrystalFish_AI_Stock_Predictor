"""
API Test Dashboard Agent for CrystalFish
Special agent that monitors API health and provides intelligent recommendations
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.services.api_test import get_api_tester
from app.services.openrouter import get_openrouter_client, OpenRouterClient
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class ApiTestDashboardAgent:
    """
    API Test Dashboard Agent - Monitors API health and provides intelligent analysis
    """

    def __init__(self, openrouter_client: Optional[OpenRouterClient] = None):
        self.name = "API Guardian"
        self.role = "API Performance Monitor"
        self.avatar_type = "owl"  # Wise observer
        self.llm_client = openrouter_client or get_openrouter_client()
        self.api_tester = get_api_tester()

        # Analysis state
        self.last_analysis: Optional[Dict[str, Any]] = None
        self.analysis_count = 0
        self.alerts: List[Dict[str, Any]] = []

        # Thresholds
        self.thresholds = {
            "response_time_warning_ms": 300,
            "response_time_critical_ms": 1000,
            "success_rate_warning": 95.0,
            "success_rate_critical": 80.0,
            "error_rate_warning": 5.0,
            "error_rate_critical": 20.0
        }

        logger.info("API Test Dashboard Agent initialized")

    async def analyze_api_health(self) -> Dict[str, Any]:
        """
        Analyze current API health and generate insights

        Returns:
            Analysis result dict
        """
        logger.info("Starting API health analysis")

        # Get current dashboard data
        dashboard_data = self.api_tester.get_dashboard_data()
        health = dashboard_data["health"]
        state = dashboard_data["state"]

        # Analyze metrics
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "health_status": health["status"],
            "version": health["version"],
            "endpoints_tested": health["endpoints_tested"],
            "endpoints_passed": health["endpoints_passed"],
            "pass_rate": (health["endpoints_passed"] / health["endpoints_tested"] * 100) if health["endpoints_tested"] > 0 else 0,
            "average_response_time_ms": health["average_response_time_ms"],
            "total_tests_run": state["total_tests_run"],
            "success_rate": state["success_rate"],
            "is_monitoring": state["is_monitoring"],
            "alerts": [],
            "recommendations": dashboard_data["recommendations"],
            "performance_score": 100.0
        }

        # Check thresholds and generate alerts
        if health["average_response_time_ms"] > self.thresholds["response_time_critical_ms"]:
            analysis["alerts"].append({
                "level": "critical",
                "type": "high_response_time",
                "message": f"Critical: Average response time is {health['average_response_time_ms']:.0f}ms (>1000ms)",
                "timestamp": datetime.utcnow().isoformat()
            })
            analysis["performance_score"] -= 30
        elif health["average_response_time_ms"] > self.thresholds["response_time_warning_ms"]:
            analysis["alerts"].append({
                "level": "warning",
                "type": "elevated_response_time",
                "message": f"Warning: Average response time is {health['average_response_time_ms']:.0f}ms (>300ms)",
                "timestamp": datetime.utcnow().isoformat()
            })
            analysis["performance_score"] -= 15

        if state["success_rate"] < self.thresholds["success_rate_critical"]:
            analysis["alerts"].append({
                "level": "critical",
                "type": "low_success_rate",
                "message": f"Critical: Success rate is {state['success_rate']:.1f}% (<80%)",
                "timestamp": datetime.utcnow().isoformat()
            })
            analysis["performance_score"] -= 40
        elif state["success_rate"] < self.thresholds["success_rate_warning"]:
            analysis["alerts"].append({
                "level": "warning",
                "type": "elevated_failure_rate",
                "message": f"Warning: Success rate is {state['success_rate']:.1f}% (<95%)",
                "timestamp": datetime.utcnow().isoformat()
            })
            analysis["performance_score"] -= 20

        # Analyze recent failures
        if state["recent_failures"]:
            failure_endpoints = list(set(f["endpoint"] for f in state["recent_failures"]))
            analysis["alerts"].append({
                "level": "info",
                "type": "recent_failures",
                "message": f"{len(state['recent_failures'])} recent failures detected on endpoints: {', '.join(failure_endpoints)}",
                "timestamp": datetime.utcnow().isoformat(),
                "failed_endpoints": failure_endpoints
            })

        # Cap performance score
        analysis["performance_score"] = max(0, min(100, analysis["performance_score"]))

        # Store analysis
        self.last_analysis = analysis
        self.analysis_count += 1

        # Store alerts
        self.alerts.extend(analysis["alerts"])
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]

        logger.info(f"API health analysis completed", score=analysis["performance_score"], alerts=len(analysis["alerts"]))
        return analysis

    async def generate_intelligent_recommendations(self) -> List[str]:
        """
        Generate intelligent recommendations using LLM

        Returns:
            List of recommendation strings
        """
        if not self.last_analysis:
            await self.analyze_api_health()

        # Prepare context for LLM
        context = {
            "health_status": self.last_analysis["health_status"],
            "performance_score": self.last_analysis["performance_score"],
            "average_response_time_ms": self.last_analysis["average_response_time_ms"],
            "success_rate": self.last_analysis["success_rate"],
            "alerts": [a["message"] for a in self.last_analysis["alerts"]],
            "current_recommendations": self.last_analysis["recommendations"]
        }

        # Try to get LLM-enhanced recommendations
        try:
            prompt = f"""You are an API performance expert. Analyze this API health data and provide specific, actionable recommendations:

Health Status: {context['health_status']}
Performance Score: {context['performance_score']}/100
Average Response Time: {context['average_response_time_ms']:.0f}ms
Success Rate: {context['success_rate']:.1f}%

Current Alerts:
{chr(10).join('- ' + alert for alert in context['alerts'])}

Current Recommendations:
{chr(10).join('- ' + rec for rec in context['current_recommendations'])}

Provide 3-5 specific, actionable recommendations to improve API performance and reliability. Be concise and technical."""

            response = await self.llm_client._make_request(prompt)

            # Parse response into list
            recommendations = [line.strip() for line in response.split('\n') if line.strip() and not line.startswith('#')]
            recommendations = [r.lstrip('- *•') for r in recommendations]  # Remove bullet points
            recommendations = [r for r in recommendations if len(r) > 10]  # Filter short lines

            logger.info("LLM-enhanced recommendations generated", count=len(recommendations))
            return recommendations[:5]  # Return top 5

        except Exception as e:
            logger.error(f"Failed to generate LLM recommendations: {str(e)}")
            # Return rule-based recommendations
            return self._generate_rule_based_recommendations()

    def _generate_rule_based_recommendations(self) -> List[str]:
        """Generate recommendations based on rules"""
        recommendations = []

        if not self.last_analysis:
            return ["Start API monitoring to collect performance data"]

        # Response time recommendations
        avg_time = self.last_analysis["average_response_time_ms"]
        if avg_time > 500:
            recommendations.append("Implement Redis caching for frequently accessed endpoints to reduce response times")
        if avg_time > 200:
            recommendations.append("Review database query performance and add appropriate indexes")

        # Success rate recommendations
        success_rate = self.last_analysis["success_rate"]
        if success_rate < 90:
            recommendations.append("Investigate and fix failing endpoints - check error logs for root causes")
        if success_rate < 95:
            recommendations.append("Implement circuit breakers to prevent cascade failures")

        # Monitoring recommendations
        if not self.last_analysis["is_monitoring"]:
            recommendations.append("Enable continuous monitoring to track API performance trends")

        # General best practices
        if len(recommendations) < 3:
            recommendations.append("Set up alerting for critical metrics (response time >1s, success rate <95%)")
            recommendations.append("Consider implementing rate limiting to protect against traffic spikes")
            recommendations.append("Review API documentation and ensure all endpoints are properly documented")

        return recommendations[:5]

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get a concise dashboard summary

        Returns:
            Dashboard summary dict
        """
        if not self.last_analysis:
            await self.analyze_api_health()

        return {
            "agent_name": self.name,
            "agent_role": self.role,
            "timestamp": datetime.utcnow().isoformat(),
            "health_status": self.last_analysis["health_status"],
            "performance_score": self.last_analysis["performance_score"],
            "success_rate": self.last_analysis["success_rate"],
            "average_response_time_ms": self.last_analysis["average_response_time_ms"],
            "active_alerts": len([a for a in self.last_analysis["alerts"] if a["level"] in ["critical", "warning"]]),
            "total_alerts": len(self.alerts),
            "analysis_count": self.analysis_count,
            "recommendations": await self.generate_intelligent_recommendations()
        }

    async def chat_about_api(self, user_message: str) -> str:
        """
        Chat about API performance with the agent

        Args:
            user_message: User's question or comment

        Returns:
            Agent's response
        """
        if not self.last_analysis:
            await self.analyze_api_health()

        # Prepare context
        context = f"""Current API Status:
- Health: {self.last_analysis['health_status']}
- Performance Score: {self.last_analysis['performance_score']}/100
- Success Rate: {self.last_analysis['success_rate']:.1f}%
- Avg Response Time: {self.last_analysis['average_response_time_ms']:.0f}ms
- Tests Run: {self.last_analysis['total_tests_run']}
- Active Alerts: {len(self.last_analysis['alerts'])}

Recent Alerts:
{chr(10).join(f"- {a['message']}" for a in self.last_analysis['alerts'][-5:])}

User Question: {user_message}

Provide a helpful, technical answer about the API performance."""

        try:
            response = await self.llm_client._make_request(context)
            return response
        except Exception as e:
            logger.error(f"Failed to generate chat response: {str(e)}")
            return f"As the API Guardian, I monitor our API health. Currently, our performance score is {self.last_analysis['performance_score']}/100 with a {self.last_analysis['success_rate']:.1f}% success rate. How can I help you understand our API performance?"


# Global API Test Dashboard Agent instance
api_dashboard_agent = ApiTestDashboardAgent()


def get_api_dashboard_agent() -> ApiTestDashboardAgent:
    """Get API Dashboard Agent instance"""
    return api_dashboard_agent
