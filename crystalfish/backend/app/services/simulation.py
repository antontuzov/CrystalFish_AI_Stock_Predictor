"""
Simulation service for CrystalFish
Orchestrates multi-agent swarm simulation
"""
import asyncio
import random
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from app.services.agent import Agent, generate_agents
from app.services.math_models import get_math_service
from app.services.openrouter import get_openrouter_client

logger = structlog.get_logger()


class SimulationService:
    """Service for running multi-agent simulations"""
    
    def __init__(self):
        self.math_service = get_math_service()
        self.logger = structlog.get_logger()
    
    async def run_simulation(
        self,
        simulation_id: int,
        params: Dict[str, Any],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Run a complete simulation
        
        Args:
            simulation_id: Simulation ID
            params: Simulation parameters
            progress_callback: Callback for progress updates
            
        Returns:
            Simulation results
        """
        self.logger.info(f"Starting simulation {simulation_id}", params=params)
        
        # Extract parameters
        asset_symbol = params["asset_symbol"]
        asset_type = params["asset_type"]
        time_horizon = params["time_horizon_days"]
        agents_count = params["agents_count"]
        personality_distribution = params["personality_distribution"]
        confidence_level = params["confidence_level"]
        
        # Fetch or load historical data
        price_data = await self._fetch_price_data(asset_symbol, asset_type, params)
        
        if price_data is None or len(price_data) < 30:
            raise ValueError("Insufficient price data for simulation")
        
        # Calculate technical indicators
        indicators = self.math_service.calculate_technical_indicators(price_data)
        
        # Run math models for baseline
        math_results = self._run_math_models(price_data, time_horizon, confidence_level)
        
        # Generate agents
        openrouter_client = get_openrouter_client()
        agents = generate_agents(agents_count, personality_distribution, openrouter_client)
        
        self.logger.info(f"Generated {len(agents)} agents for simulation {simulation_id}")
        
        # Initialize simulation state
        current_price = float(price_data.iloc[-1])
        simulation_steps = time_horizon
        
        # Track sentiment history
        sentiment_history = []
        
        # Run simulation steps
        for step in range(simulation_steps):
            # Update progress
            progress = (step / simulation_steps) * 100
            if progress_callback:
                await progress_callback({
                    "simulation_id": simulation_id,
                    "status": "running",
                    "progress_percent": progress,
                    "current_step": step,
                    "total_steps": simulation_steps,
                    "message": f"Running step {step + 1}/{simulation_steps}"
                })
            
            # Prepare market context
            market_context = self._prepare_market_context(
                price_data, indicators, current_price, step, asset_symbol
            )
            
            # Add math model signals to context
            if step < len(math_results["ensemble"]["predictions"]):
                math_pred = math_results["ensemble"][predictions][step]
                market_context["math_model_prediction"] = math_pred["predicted_price"]
                market_context["math_model_upper"] = math_pred["upper_bound"]
                market_context["math_model_lower"] = math_pred["lower_bound"]
            
            # Run all agents
            agent_decisions = await self._run_agent_step(agents, market_context, step)
            
            # Aggregate sentiment
            sentiment = self._aggregate_sentiment(agents)
            sentiment["step"] = step
            sentiment["date"] = (datetime.utcnow() + timedelta(days=step)).isoformat()
            sentiment_history.append(sentiment)
            
            # Update price based on agent actions (market impact)
            current_price = self._update_price(current_price, agents, sentiment)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        # Final calculations
        final_predictions = self._generate_predictions(
            price_data, agents, sentiment_history, math_results, time_horizon, confidence_level
        )
        
        # Get top performing agents
        top_agents = self._get_top_agents(agents, current_price)
        
        # Compile results
        results = {
            "simulation_id": simulation_id,
            "predictions": final_predictions,
            "sentiment_history": sentiment_history,
            "final_price_prediction": final_predictions[-1]["predicted_price"] if final_predictions else current_price,
            "price_change_percent": ((final_predictions[-1]["predicted_price"] - float(price_data.iloc[-1])) / float(price_data.iloc[-1]) * 100) if final_predictions else 0,
            "confidence_interval": {
                "lower": final_predictions[-1]["lower_bound"] if final_predictions else current_price * 0.9,
                "upper": final_predictions[-1]["upper_bound"] if final_predictions else current_price * 1.1
            },
            "key_factors": self._extract_key_factors(sentiment_history, indicators),
            "top_agents": [a.get_state() for a in top_agents],
            "math_model_comparison": math_results
        }
        
        self.logger.info(f"Simulation {simulation_id} completed")
        
        return results
    
    async def _fetch_price_data(
        self,
        asset_symbol: str,
        asset_type: str,
        params: Dict[str, Any]
    ) -> Optional[pd.Series]:
        """Fetch historical price data"""
        data_source = params.get("data_source", "yahoo")
        
        try:
            if data_source == "upload" and params.get("uploaded_data_path"):
                # Load from uploaded file
                df = pd.read_csv(params["uploaded_data_path"])
                if "close" in df.columns:
                    return pd.Series(df["close"].values, index=pd.to_datetime(df["date"]) if "date" in df.columns else None)
            
            # Fetch from Yahoo Finance
            import yfinance as yf
            
            ticker = asset_symbol
            if asset_type == "crypto":
                ticker = f"{asset_symbol}-USD"
            
            data = yf.download(ticker, period="1y", interval="1d", progress=False)
            
            if len(data) > 0:
                return data["Close"]
            
        except Exception as e:
            self.logger.error(f"Error fetching price data: {str(e)}")
        
        # Fallback: generate synthetic data
        return self._generate_synthetic_data(asset_symbol)
    
    def _generate_synthetic_data(self, asset_symbol: str) -> pd.Series:
        """Generate synthetic price data for testing"""
        np.random.seed(hash(asset_symbol) % 2**32)
        
        days = 365
        initial_price = random.uniform(50, 500)
        
        returns = np.random.normal(0.001, 0.02, days)
        prices = initial_price * np.exp(np.cumsum(returns))
        
        dates = pd.date_range(end=datetime.utcnow(), periods=days, freq='D')
        return pd.Series(prices, index=dates)
    
    def _run_math_models(
        self,
        price_data: pd.Series,
        steps: int,
        confidence: float
    ) -> Dict[str, Any]:
        """Run mathematical models for baseline"""
        try:
            ensemble = self.math_service.ensemble_forecast(price_data, steps, confidence)
            garch = self.math_service.garch_volatility(price_data, steps)
            
            return {
                "ensemble": ensemble,
                "garch": garch,
                "indicators": self.math_service.calculate_technical_indicators(price_data)
            }
        except Exception as e:
            self.logger.error(f"Error running math models: {str(e)}")
            return {
                "ensemble": {"predictions": []},
                "garch": {"predictions": []},
                "indicators": {}
            }
    
    def _prepare_market_context(
        self,
        price_data: pd.Series,
        indicators: Dict[str, Any],
        current_price: float,
        step: int,
        asset_symbol: str
    ) -> Dict[str, Any]:
        """Prepare market context for agents"""
        # Calculate recent price changes
        recent_returns = price_data.pct_change().tail(7)
        
        return {
            "asset_symbol": asset_symbol,
            "current_price": current_price,
            "price_change_24h": recent_returns.iloc[-1] * 100 if len(recent_returns) > 0 else 0,
            "price_change_7d": (price_data.iloc[-1] - price_data.iloc[-7]) / price_data.iloc[-7] * 100 if len(price_data) >= 7 else 0,
            "rsi": indicators.get("rsi", 50),
            "macd": indicators.get("macd", 0),
            "volume": indicators.get("current_volume", 0),
            "trend": indicators.get("trend", "neutral"),
            "volatility": indicators.get("volatility_20d", 0.3),
            "news_sentiment": random.choice(["positive", "neutral", "negative"]),  # Placeholder
            "step": step
        }
    
    async def _run_agent_step(
        self,
        agents: List[Agent],
        market_context: Dict[str, Any],
        step: int
    ) -> List[Dict[str, Any]]:
        """Run all agents for one step"""
        decisions = []
        
        # Run agents in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(agents), batch_size):
            batch = agents[i:i+batch_size]
            batch_tasks = [agent.think_and_act(market_context, step) for agent in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Agent error: {str(result)}")
                else:
                    decisions.append(result)
            
            # Rate limiting delay
            await asyncio.sleep(0.5)
        
        return decisions
    
    def _aggregate_sentiment(self, agents: List[Agent]) -> Dict[str, Any]:
        """Aggregate agent sentiment"""
        if not agents:
            return {
                "bullish_percent": 33.33,
                "bearish_percent": 33.33,
                "neutral_percent": 33.34,
                "average_confidence": 0.5
            }
        
        decisions = [a.current_decision for a in agents]
        confidences = [a.current_confidence for a in agents]
        
        buy_count = decisions.count("buy")
        sell_count = decisions.count("sell")
        hold_count = decisions.count("hold")
        total = len(decisions)
        
        return {
            "bullish_percent": (buy_count / total) * 100,
            "bearish_percent": (sell_count / total) * 100,
            "neutral_percent": (hold_count / total) * 100,
            "average_confidence": np.mean(confidences),
            "buy_count": buy_count,
            "sell_count": sell_count,
            "hold_count": hold_count
        }
    
    def _update_price(
        self,
        current_price: float,
        agents: List[Agent],
        sentiment: Dict[str, Any]
    ) -> float:
        """Update price based on agent actions"""
        # Calculate net buying pressure
        buy_pressure = sentiment["bullish_percent"] / 100
        sell_pressure = sentiment["bearish_percent"] / 100
        net_pressure = buy_pressure - sell_pressure
        
        # Random market noise
        noise = random.gauss(0, 0.01)
        
        # Price change
        price_change = net_pressure * 0.02 + noise  # Max 2% move per step
        new_price = current_price * (1 + price_change)
        
        return max(0.01, new_price)  # Ensure positive price
    
    def _generate_predictions(
        self,
        price_data: pd.Series,
        agents: List[Agent],
        sentiment_history: List[Dict[str, Any]],
        math_results: Dict[str, Any],
        steps: int,
        confidence: float
    ) -> List[Dict[str, Any]]:
        """Generate final price predictions"""
        predictions = []
        current_price = float(price_data.iloc[-1])
        
        # Get math model predictions
        math_predictions = math_results.get("ensemble", {}).get("predictions", [])
        
        # Get average agent sentiment trend
        if sentiment_history:
            recent_sentiment = sentiment_history[-1]
            sentiment_bias = (recent_sentiment["bullish_percent"] - recent_sentiment["bearish_percent"]) / 100
        else:
            sentiment_bias = 0
        
        for step in range(steps):
            # Combine math model with agent sentiment
            if step < len(math_predictions):
                math_pred = math_predictions[step]["predicted_price"]
                math_lower = math_predictions[step]["lower_bound"]
                math_upper = math_predictions[step]["upper_bound"]
            else:
                # Extrapolate
                last_math = math_predictions[-1] if math_predictions else {"predicted_price": current_price}
                math_pred = last_math["predicted_price"] * (1 + sentiment_bias * 0.01)
                math_lower = math_pred * 0.95
                math_upper = math_pred * 1.05
            
            # Weight: 60% math model, 40% agent sentiment
            agent_adjustment = sentiment_bias * 0.02 * current_price
            combined_price = math_pred * 0.6 + (math_pred + agent_adjustment) * 0.4
            
            # Widen confidence intervals over time
            z_score = 1.96 if confidence >= 0.95 else 1.645
            volatility = 0.02
            margin = z_score * volatility * np.sqrt(step + 1) * current_price
            
            predictions.append({
                "step": step + 1,
                "date": (datetime.utcnow() + timedelta(days=step + 1)).strftime("%Y-%m-%d"),
                "predicted_price": round(combined_price, 2),
                "lower_bound": round(max(0, combined_price - margin), 2),
                "upper_bound": round(combined_price + margin, 2),
                "confidence": confidence,
                "math_model_prediction": round(math_pred, 2),
                "agent_sentiment_bias": round(sentiment_bias, 4)
            })
        
        return predictions
    
    def _get_top_agents(self, agents: List[Agent], current_price: float, top_n: int = 5) -> List[Agent]:
        """Get top performing agents"""
        # Update all agent performance
        for agent in agents:
            agent.update_performance(current_price)
        
        # Sort by return
        sorted_agents = sorted(agents, key=lambda a: a.total_return, reverse=True)
        return sorted_agents[:top_n]
    
    def _extract_key_factors(
        self,
        sentiment_history: List[Dict[str, Any]],
        indicators: Dict[str, Any]
    ) -> List[str]:
        """Extract key influencing factors"""
        factors = []
        
        # Technical factors
        rsi = indicators.get("rsi", 50)
        if rsi > 70:
            factors.append("RSI indicates overbought conditions")
        elif rsi < 30:
            factors.append("RSI indicates oversold conditions")
        
        trend = indicators.get("trend", "neutral")
        if trend == "bullish":
            factors.append("Moving averages show bullish trend")
        elif trend == "bearish":
            factors.append("Moving averages show bearish trend")
        
        # Sentiment factors
        if sentiment_history:
            recent = sentiment_history[-1]
            if recent["bullish_percent"] > 60:
                factors.append("Strong bullish sentiment among agents")
            elif recent["bearish_percent"] > 60:
                factors.append("Strong bearish sentiment among agents")
            
            if recent["average_confidence"] > 0.7:
                factors.append("High confidence in agent predictions")
        
        return factors if factors else ["Mixed signals from technical and sentiment analysis"]


# Global service instance
_simulation_service: Optional[SimulationService] = None


def get_simulation_service() -> SimulationService:
    """Get or create simulation service"""
    global _simulation_service
    if _simulation_service is None:
        _simulation_service = SimulationService()
    return _simulation_service