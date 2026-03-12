"""
Agent routes for CrystalFish
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.agent import AgentResponse, AgentDetailResponse, AgentChatMessage, AgentChatResponse
from app.models.agent import Agent
from app.models.simulation import Simulation
from app.services.openrouter import get_openrouter_client

router = APIRouter(prefix="/simulations/{simulation_id}/agents", tags=["Agents"])


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    simulation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List all agents in a simulation"""
    # Verify simulation belongs to user
    sim_result = await db.execute(
        select(Simulation).where(
            Simulation.id == simulation_id,
            Simulation.user_id == user_id
        )
    )
    simulation = sim_result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Get agents
    result = await db.execute(
        select(Agent).where(Agent.simulation_id == simulation_id)
    )
    agents = result.scalars().all()
    
    return agents


@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    simulation_id: int,
    agent_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get agent details"""
    # Verify simulation belongs to user
    sim_result = await db.execute(
        select(Simulation).where(
            Simulation.id == simulation_id,
            Simulation.user_id == user_id
        )
    )
    simulation = sim_result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Get agent
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.simulation_id == simulation_id
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent


@router.post("/{agent_id}/chat", response_model=AgentChatResponse)
async def chat_with_agent(
    simulation_id: int,
    agent_id: int,
    message: AgentChatMessage,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Chat with an agent"""
    from datetime import datetime
    import asyncio
    
    # Verify simulation belongs to user
    sim_result = await db.execute(
        select(Simulation).where(
            Simulation.id == simulation_id,
            Simulation.user_id == user_id
        )
    )
    simulation = sim_result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Get agent
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.simulation_id == simulation_id
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Get OpenRouter client
    llm_client = get_openrouter_client()
    
    # Prepare market context
    market_context = {
        "asset_symbol": simulation.asset_symbol,
        "current_decision": agent.current_decision,
        "current_confidence": agent.current_confidence,
        "reasoning": agent.reasoning
    }
    
    # Get agent response
    try:
        response = asyncio.run(llm_client.chat_with_agent(
            agent_name=agent.name,
            agent_personality=agent.personality,
            persona_description=agent.persona_description,
            message=message.message,
            context=market_context
        ))
    except Exception as e:
        # Fallback response
        response = f"As {agent.name}, I appreciate your question about '{message.message}'. Based on my {agent.personality} perspective, I believe the market will move in a direction that aligns with my analysis. My current position reflects my confidence level of {agent.current_confidence:.0%}."
    
    return AgentChatResponse(
        agent_id=agent.id,
        agent_name=agent.name,
        response=response,
        timestamp=datetime.utcnow()
    )