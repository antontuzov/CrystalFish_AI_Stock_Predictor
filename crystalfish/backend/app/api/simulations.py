"""
Simulation routes for CrystalFish
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import json
import os
import shutil

from app.core.database import get_db
from app.core.security import get_current_user_id, get_optional_user_id
from app.core.config import get_settings
from app.schemas.simulation import (
    SimulationCreate, SimulationUpdate, SimulationResponse,
    SimulationListResponse, SimulationProgressUpdate, SimulationResults
)
from app.models.simulation import Simulation, SimulationStatus
from app.worker.tasks import run_simulation_task

router = APIRouter(prefix="/simulations", tags=["Simulations"])


@router.post("", response_model=SimulationResponse)
async def create_simulation(
    simulation_data: SimulationCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new simulation"""
    settings = get_settings()
    
    # Validate agent count
    if simulation_data.agents_count > settings.MAX_AGENTS_PER_SIMULATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent count exceeds maximum of {settings.MAX_AGENTS_PER_SIMULATION}"
        )
    
    # Create simulation
    new_simulation = Simulation(
        user_id=user_id,
        name=simulation_data.name,
        description=simulation_data.description,
        asset_symbol=simulation_data.asset_symbol.upper(),
        asset_type=simulation_data.asset_type,
        time_horizon_days=simulation_data.time_horizon_days,
        confidence_level=simulation_data.confidence_level,
        agents_count=simulation_data.agents_count,
        personality_distribution=simulation_data.personality_distribution.model_dump(),
        data_source=simulation_data.data_source,
        status=SimulationStatus.PENDING,
        progress_percent=0.0
    )
    
    db.add(new_simulation)
    await db.commit()
    await db.refresh(new_simulation)
    
    # Start simulation task
    params = {
        "asset_symbol": new_simulation.asset_symbol,
        "asset_type": new_simulation.asset_type,
        "time_horizon_days": new_simulation.time_horizon_days,
        "confidence_level": new_simulation.confidence_level,
        "agents_count": new_simulation.agents_count,
        "personality_distribution": new_simulation.personality_distribution,
        "data_source": new_simulation.data_source,
        "uploaded_data_path": new_simulation.uploaded_data_path
    }
    
    # Queue the task
    run_simulation_task.delay(new_simulation.id, params)
    
    return new_simulation


@router.post("/upload", response_model=SimulationResponse)
async def create_simulation_with_upload(
    name: str,
    asset_symbol: str,
    asset_type: str = "stock",
    time_horizon_days: int = 7,
    confidence_level: float = 0.95,
    agents_count: int = 100,
    personality_distribution: Optional[str] = None,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create simulation with uploaded data file"""
    settings = get_settings()
    
    # Save uploaded file
    upload_dir = "/app/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{user_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Parse personality distribution
    if personality_distribution:
        try:
            pers_dist = json.loads(personality_distribution)
        except json.JSONDecodeError:
            pers_dist = {
                "bullish": 0.25,
                "bearish": 0.25,
                "neutral": 0.25,
                "trend_follower": 0.15,
                "contrarian": 0.10
            }
    else:
        pers_dist = {
            "bullish": 0.25,
            "bearish": 0.25,
            "neutral": 0.25,
            "trend_follower": 0.15,
            "contrarian": 0.10
        }
    
    # Create simulation
    new_simulation = Simulation(
        user_id=user_id,
        name=name,
        asset_symbol=asset_symbol.upper(),
        asset_type=asset_type,
        time_horizon_days=time_horizon_days,
        confidence_level=confidence_level,
        agents_count=min(agents_count, settings.MAX_AGENTS_PER_SIMULATION),
        personality_distribution=pers_dist,
        data_source="upload",
        uploaded_data_path=file_path,
        status=SimulationStatus.PENDING,
        progress_percent=0.0
    )
    
    db.add(new_simulation)
    await db.commit()
    await db.refresh(new_simulation)
    
    # Start simulation task
    params = {
        "asset_symbol": new_simulation.asset_symbol,
        "asset_type": new_simulation.asset_type,
        "time_horizon_days": new_simulation.time_horizon_days,
        "confidence_level": new_simulation.confidence_level,
        "agents_count": new_simulation.agents_count,
        "personality_distribution": new_simulation.personality_distribution,
        "data_source": "upload",
        "uploaded_data_path": file_path
    }
    
    run_simulation_task.delay(new_simulation.id, params)
    
    return new_simulation


@router.get("", response_model=List[SimulationListResponse])
async def list_simulations(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List user's simulations"""
    query = select(Simulation).where(Simulation.user_id == user_id)
    
    if status:
        query = query.where(Simulation.status == status)
    
    query = query.order_by(desc(Simulation.created_at)).offset(offset).limit(limit)
    
    result = await db.execute(query)
    simulations = result.scalars().all()
    
    return simulations


@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get simulation details"""
    result = await db.execute(
        select(Simulation).where(
            Simulation.id == simulation_id,
            Simulation.user_id == user_id
        )
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    return simulation


@router.get("/{simulation_id}/results", response_model=SimulationResults)
async def get_simulation_results(
    simulation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get simulation results"""
    result = await db.execute(
        select(Simulation).where(
            Simulation.id == simulation_id,
            Simulation.user_id == user_id
        )
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    if simulation.status != SimulationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Simulation is {simulation.status.value}, not completed"
        )
    
    if not simulation.results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not available"
        )
    
    return SimulationResults(**simulation.results)


@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    simulation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a simulation"""
    result = await db.execute(
        select(Simulation).where(
            Simulation.id == simulation_id,
            Simulation.user_id == user_id
        )
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    await db.delete(simulation)
    await db.commit()
    
    return None


@router.websocket("/{simulation_id}/ws")
async def simulation_websocket(websocket: WebSocket, simulation_id: int):
    """WebSocket for real-time simulation updates"""
    await websocket.accept()
    
    try:
        while True:
            # Get simulation status from task
            task = run_simulation_task.AsyncResult(f"simulation_{simulation_id}")
            
            if task.state == "PENDING":
                await websocket.send_json({
                    "status": "pending",
                    "progress": 0,
                    "message": "Waiting to start..."
                })
            elif task.state == "PROGRESS":
                await websocket.send_json({
                    "status": "running",
                    "progress": task.info.get("progress", 0),
                    "current_step": task.info.get("current_step", 0),
                    "total_steps": task.info.get("total_steps", 0),
                    "message": task.info.get("message", "")
                })
            elif task.state == "SUCCESS":
                await websocket.send_json({
                    "status": "completed",
                    "progress": 100,
                    "message": "Simulation completed!"
                })
                break
            elif task.state == "FAILURE":
                await websocket.send_json({
                    "status": "failed",
                    "progress": 0,
                    "message": str(task.info)
                })
                break
            
            await asyncio.sleep(1)
            
    except Exception as e:
        await websocket.close()
    finally:
        await websocket.close()