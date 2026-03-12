"""
Agent service for CrystalFish
Defines agent behavior and decision making
"""
import random
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.services.openrouter import get_openrouter_client, OpenRouterClient

logger = structlog.get_logger()


# Agent persona templates
AGENT_PERSONAS = {
    "bullish": {
        "names": ["Optimist Olivia", "Bullish Bob", "Growth Gary", "Moon Mike", "Rocket Rachel"],
        "descriptions": [
            "You are an optimistic investor who always sees the upside. You believe in long-term growth and tend to buy dips.",
            "You're a growth-focused trader who believes the market always goes up in the long run. You love momentum.",
            "You're a crypto enthusiast who believes in the technology and expects prices to reach new highs."
        ],
        "avatars": ["dolphin", "whale"]
    },
    "bearish": {
        "names": ["Pessimistic Pete", "Bearish Betty", "Doomer Dan", "Crash Cathy", "Short Seller Sam"],
        "descriptions": [
            "You are a cautious investor who sees risks everywhere. You believe in taking profits early and protecting capital.",
            "You're a risk-averse trader who believes what goes up must come down. You're quick to sell.",
            "You're a skeptical analyst who thinks most assets are overvalued. You look for short opportunities."
        ],
        "avatars": ["octopus", "turtle"]
    },
    "neutral": {
        "names": ["Balanced Ben", "Neutral Nancy", "Steady Steve", "Centered Cathy", "Moderate Mike"],
        "descriptions": [
            "You are a balanced investor who weighs both sides equally. You make decisions based on solid data.",
            "You're a methodical trader who doesn't get emotional. You follow a systematic approach.",
            "You're a conservative analyst who waits for clear signals before acting."
        ],
        "avatars": ["fish", "seahorse"]
    },
    "trend_follower": {
        "names": ["Trendy Tom", "Momentum Mary", "Follower Fred", "Chart Charlie", "Technical Tina"],
        "descriptions": [
            "You are a technical trader who follows trends. You buy when price is rising, sell when falling.",
            "You're a momentum trader who rides the wave. You use moving averages and technical indicators.",
            "You're a chart pattern expert who trades based on price action and volume."
        ],
        "avatars": ["dolphin", "fish"]
    },
    "contrarian": {
        "names": ["Contrarian Carl", "Reverser Rita", "Opposite Oscar", "Against Andy", "Counter Cathy"],
        "descriptions": [
            "You are a contrarian investor who goes against the crowd. You buy when others are fearful.",
            "You're a value hunter who looks for oversold assets. You sell when euphoria peaks.",
            "You're a mean-reversion trader who believes extremes always correct."
        ],
        "avatars": ["octopus", "seahorse"]
    }
}


class Agent:
    """
    CrystalFish Agent - Individual AI trader in the swarm
    """
    
    def __init__(
        self,
        agent_id: int,
        name: str,
        avatar_type: str,
        personality: str,
        persona_description: str,
        initial_capital: float = 10000.0,
        openrouter_client: Optional[OpenRouterClient] = None
    ):
        self.id = agent_id
        self.name = name
        self.avatar_type = avatar_type
        self.personality = personality
        self.persona_description = persona_description
        
        # Financial state
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position = 0.0  # Units of asset held
        
        # Memory
        self.memory: List[Dict[str, Any]] = []
        self.trade_history: List[Dict[str, Any]] = []
        
        # Current decision
        self.current_decision = "hold"
        self.current_confidence = 0.5
        self.reasoning = ""
        self.target_position = 0.0
        
        # Performance
        self.total_return = 0.0
        self.sharpe_ratio = 0.0
        
        # LLM client
        self.llm_client = openrouter_client or get_openrouter_client()
        
        # Logger
        self.logger = structlog.get_logger().bind(agent_id=agent_id, agent_name=name)
    
    @classmethod
    def create_random_agent(
        cls,
        agent_id: int,
        personality: str,
        openrouter_client: Optional[OpenRouterClient] = None
    ) -> "Agent":
        """Create a random agent with given personality"""
        persona = AGENT_PERSONAS.get(personality, AGENT_PERSONAS["neutral"])
        
        name = random.choice(persona["names"])
        avatar_type = random.choice(persona["avatars"])
        description = random.choice(persona["descriptions"])
        
        return cls(
            agent_id=agent_id,
            name=name,
            avatar_type=avatar_type,
            personality=personality,
            persona_description=description,
            openrouter_client=openrouter_client
        )
    
    async def think_and_act(
        self,
        market_context: Dict[str, Any],
        step: int
    ) -> Dict[str, Any]:
        """
        Agent thinks about the market and makes a decision
        
        Args:
            market_context: Current market data
            step: Current simulation step
            
        Returns:
            Decision dict with action details
        """
        self.logger.debug(f"Step {step}: Agent thinking", market_context=market_context)
        
        try:
            # Get LLM reasoning
            result = await self.llm_client.generate_agent_reasoning(
                agent_name=self.name,
                agent_personality=self.personality,
                persona_description=self.persona_description,
                market_context=market_context,
                memory=self.memory,
                current_position=self.position
            )
            
            self.current_decision = result.get("decision", "hold")
            self.current_confidence = result.get("confidence", 0.5)
            self.reasoning = result.get("reasoning", "")
            self.target_position = result.get("target_position", self.position)
            
        except Exception as e:
            self.logger.error(f"Error in LLM call: {str(e)}")
            # Fallback to rule-based decision
            self._rule_based_decision(market_context)
        
        # Record in memory
        memory_entry = {
            "step": step,
            "timestamp": datetime.utcnow().isoformat(),
            "observation": {
                "price": market_context.get("current_price"),
                "rsi": market_context.get("rsi"),
                "trend": market_context.get("trend")
            },
            "decision": self.current_decision,
            "confidence": self.current_confidence,
            "reasoning": self.reasoning
        }
        self.memory.append(memory_entry)
        
        # Execute trade
        trade_result = self._execute_trade(market_context.get("current_price", 0))
        
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "decision": self.current_decision,
            "confidence": self.current_confidence,
            "reasoning": self.reasoning,
            "trade": trade_result
        }
    
    def _rule_based_decision(self, market_context: Dict[str, Any]):
        """Fallback rule-based decision making"""
        price = market_context.get("current_price", 0)
        rsi = market_context.get("rsi", 50)
        trend = market_context.get("trend", "neutral")
        
        # Personality-based rules
        if self.personality == "bullish":
            if rsi < 40 or trend == "bullish":
                self.current_decision = "buy"
                self.current_confidence = 0.6 + random.random() * 0.3
            else:
                self.current_decision = "hold"
                self.current_confidence = 0.5
                
        elif self.personality == "bearish":
            if rsi > 60 or trend == "bearish":
                self.current_decision = "sell"
                self.current_confidence = 0.6 + random.random() * 0.3
            else:
                self.current_decision = "hold"
                self.current_confidence = 0.5
                
        elif self.personality == "trend_follower":
            if trend == "bullish":
                self.current_decision = "buy"
                self.current_confidence = 0.7
            elif trend == "bearish":
                self.current_decision = "sell"
                self.current_confidence = 0.7
            else:
                self.current_decision = "hold"
                self.current_confidence = 0.5
                
        elif self.personality == "contrarian":
            if rsi > 70:
                self.current_decision = "sell"
                self.current_confidence = 0.65
            elif rsi < 30:
                self.current_decision = "buy"
                self.current_confidence = 0.65
            else:
                self.current_decision = "hold"
                self.current_confidence = 0.4
                
        else:  # neutral
            if rsi < 35:
                self.current_decision = "buy"
                self.current_confidence = 0.55
            elif rsi > 65:
                self.current_decision = "sell"
                self.current_confidence = 0.55
            else:
                self.current_decision = "hold"
                self.current_confidence = 0.5
        
        self.reasoning = f"Rule-based decision: {self.personality} agent responding to RSI={rsi:.1f}, trend={trend}"
        
        # Set target position based on decision
        if self.current_decision == "buy":
            self.target_position = self.current_capital / price * self.current_confidence if price > 0 else 0
        elif self.current_decision == "sell":
            self.target_position = 0
        else:
            self.target_position = self.position
    
    def _execute_trade(self, current_price: float) -> Dict[str, Any]:
        """Execute trade based on current decision"""
        if current_price <= 0:
            return {"action": "none", "amount": 0, "value": 0}
        
        trade_amount = 0
        trade_value = 0
        
        if self.current_decision == "buy":
            # Buy to reach target position
            amount_to_buy = self.target_position - self.position
            if amount_to_buy > 0:
                cost = amount_to_buy * current_price
                if cost <= self.current_capital:
                    self.position += amount_to_buy
                    self.current_capital -= cost
                    trade_amount = amount_to_buy
                    trade_value = cost
        
        elif self.current_decision == "sell":
            # Sell to reach target position
            amount_to_sell = self.position - self.target_position
            if amount_to_sell > 0:
                proceeds = amount_to_sell * current_price
                self.position -= amount_to_sell
                self.current_capital += proceeds
                trade_amount = -amount_to_sell
                trade_value = proceeds
        
        # Record trade
        trade_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": self.current_decision,
            "amount": trade_amount,
            "price": current_price,
            "value": trade_value,
            "confidence": self.current_confidence
        }
        self.trade_history.append(trade_record)
        
        return trade_record
    
    def update_performance(self, current_price: float):
        """Update agent performance metrics"""
        total_value = self.current_capital + self.position * current_price
        self.total_return = (total_value - self.initial_capital) / self.initial_capital
        
        # Calculate Sharpe ratio if enough trade history
        if len(self.trade_history) >= 5:
            returns = [t.get("value", 0) for t in self.trade_history if t.get("value", 0) != 0]
            if len(returns) > 1:
                mean_return = np.mean(returns)
                std_return = np.std(returns) + 1e-8  # Avoid div by zero
                self.sharpe_ratio = mean_return / std_return
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return {
            "id": self.id,
            "name": self.name,
            "avatar_type": self.avatar_type,
            "personality": self.personality,
            "current_capital": self.current_capital,
            "position": self.position,
            "current_decision": self.current_decision,
            "current_confidence": self.current_confidence,
            "reasoning": self.reasoning,
            "total_return": self.total_return,
            "sharpe_ratio": self.sharpe_ratio,
            "memory_count": len(self.memory),
            "trade_count": len(self.trade_history)
        }
    
    async def chat(self, message: str, market_context: Dict[str, Any]) -> str:
        """Chat with the agent"""
        return await self.llm_client.chat_with_agent(
            agent_name=self.name,
            agent_personality=self.personality,
            persona_description=self.persona_description,
            message=message,
            context={
                "asset_symbol": market_context.get("asset_symbol", "UNKNOWN"),
                "current_decision": self.current_decision,
                "current_confidence": self.current_confidence,
                "reasoning": self.reasoning
            }
        )


def generate_agents(
    count: int,
    personality_distribution: Dict[str, float],
    openrouter_client: Optional[OpenRouterClient] = None
) -> List[Agent]:
    """
    Generate a list of agents based on personality distribution
    
    Args:
        count: Total number of agents
        personality_distribution: Dict with personality -> proportion
        openrouter_client: Optional LLM client
        
    Returns:
        List of Agent instances
    """
    agents = []
    agent_id = 1
    
    for personality, proportion in personality_distribution.items():
        num_agents = int(count * proportion)
        for _ in range(num_agents):
            agent = Agent.create_random_agent(
                agent_id=agent_id,
                personality=personality,
                openrouter_client=openrouter_client
            )
            agents.append(agent)
            agent_id += 1
    
    # Fill remaining agents with neutral
    while len(agents) < count:
        agent = Agent.create_random_agent(
            agent_id=agent_id,
            personality="neutral",
            openrouter_client=openrouter_client
        )
        agents.append(agent)
        agent_id += 1
    
    return agents