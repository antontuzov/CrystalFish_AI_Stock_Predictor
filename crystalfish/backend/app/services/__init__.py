"""
Services module for CrystalFish
"""
from app.services.openrouter import OpenRouterClient, get_openrouter_client
from app.services.math_models import MathModelsService, get_math_service
from app.services.agent import Agent, generate_agents
from app.services.simulation import SimulationService, get_simulation_service

__all__ = [
    "OpenRouterClient", "get_openrouter_client",
    "MathModelsService", "get_math_service",
    "Agent", "generate_agents",
    "SimulationService", "get_simulation_service"
]