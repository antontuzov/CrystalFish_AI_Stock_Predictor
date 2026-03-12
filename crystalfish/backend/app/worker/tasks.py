"""
Celery tasks for CrystalFish
"""
import asyncio
from typing import Dict, Any
from datetime import datetime
import structlog

from app.worker.celery_app import celery_app
from app.services.simulation import get_simulation_service
from app.core.database import SyncSessionLocal
from app.models.simulation import Simulation, SimulationStatus

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3)
def run_simulation_task(self, simulation_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run simulation as a Celery task
    
    Args:
        simulation_id: Simulation ID
        params: Simulation parameters
        
    Returns:
        Simulation results
    """
    logger.info(f"Starting simulation task {simulation_id}")
    
    # Update simulation status
    db = SyncSessionLocal()
    try:
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not simulation:
            raise ValueError(f"Simulation {simulation_id} not found")
        
        simulation.status = SimulationStatus.RUNNING
        simulation.started_at = datetime.utcnow()
        simulation.total_steps = params.get("time_horizon_days", 7)
        db.commit()
        
        # Progress callback
        async def progress_callback(update: Dict[str, Any]):
            simulation.progress_percent = update["progress_percent"]
            simulation.current_step = update["current_step"]
            db.commit()
            
            # Update task state for progress tracking
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": update["progress_percent"],
                    "current_step": update["current_step"],
                    "total_steps": update["total_steps"],
                    "message": update.get("message", "")
                }
            )
        
        # Run simulation
        service = get_simulation_service()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                service.run_simulation(simulation_id, params, progress_callback)
            )
        finally:
            loop.close()
        
        # Update simulation with results
        simulation.status = SimulationStatus.COMPLETED
        simulation.progress_percent = 100.0
        simulation.results = results
        simulation.prediction_chart_data = {
            "predictions": results["predictions"],
            "sentiment_history": results["sentiment_history"]
        }
        simulation.agent_sentiment_history = results["sentiment_history"]
        simulation.math_model_results = results["math_model_comparison"]
        simulation.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Simulation {simulation_id} completed successfully")
        
        return results
        
    except Exception as exc:
        logger.error(f"Simulation {simulation_id} failed: {str(exc)}")
        
        # Update simulation status
        simulation.status = SimulationStatus.FAILED
        simulation.error_message = str(exc)
        db.commit()
        
        # Retry on certain errors
        if self.request.retries < 3:
            raise self.retry(exc=exc, countdown=60)
        
        raise
        
    finally:
        db.close()


@celery_app.task
def cleanup_old_simulations(days: int = 30) -> int:
    """
    Clean up old simulation data
    
    Args:
        days: Delete simulations older than this many days
        
    Returns:
        Number of simulations deleted
    """
    from datetime import timedelta
    
    db = SyncSessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_simulations = db.query(Simulation).filter(
            Simulation.created_at < cutoff_date,
            Simulation.status.in_([SimulationStatus.COMPLETED, SimulationStatus.FAILED])
        ).all()
        
        count = len(old_simulations)
        for sim in old_simulations:
            db.delete(sim)
        
        db.commit()
        logger.info(f"Cleaned up {count} old simulations")
        
        return count
        
    finally:
        db.close()


@celery_app.task
def update_market_data() -> Dict[str, Any]:
    """Update cached market data"""
    # This could fetch and cache market data for active simulations
    logger.info("Updating market data cache")
    return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}