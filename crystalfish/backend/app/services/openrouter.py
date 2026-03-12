"""
OpenRouter service for CrystalFish
Handles LLM interactions with fallback models
"""
import asyncio
import httpx
from typing import Optional, List, Dict, Any
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()


class OpenRouterError(Exception):
    """OpenRouter API error"""
    pass


class OpenRouterClient:
    """Client for OpenRouter API"""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.default_model = settings.OPENROUTER_DEFAULT_MODEL
        self.fallback_models = settings.OPENROUTER_FALLBACK_MODELS
        self.rate_limit_delay = settings.OPENROUTER_RATE_LIMIT_DELAY
        self._last_request_time = 0
    
    async def _rate_limit(self):
        """Apply rate limiting between requests"""
        import time
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self._last_request_time = time.time()
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        use_fallback: bool = True
    ) -> str:
        """
        Get chat completion from OpenRouter
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to settings)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_fallback: Whether to try fallback models on failure
            
        Returns:
            Generated text response
        """
        await self._rate_limit()
        
        if not self.api_key:
            logger.warning("No OpenRouter API key configured, using mock response")
            return self._mock_response(messages)
        
        models_to_try = [model or self.default_model]
        if use_fallback:
            models_to_try.extend(self.fallback_models)
        
        last_error = None
        
        for model_name in models_to_try:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://crystalfish.ai",
                            "X-Title": "CrystalFish"
                        },
                        json={
                            "model": model_name,
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            return data["choices"][0]["message"]["content"]
                        else:
                            logger.warning(f"Empty response from {model_name}")
                    elif response.status_code == 429:
                        logger.warning(f"Rate limited on {model_name}, waiting...")
                        await asyncio.sleep(5)
                    else:
                        logger.warning(f"Error from {model_name}: {response.status_code}")
                        
            except Exception as e:
                last_error = e
                logger.error(f"Error calling {model_name}: {str(e)}")
                continue
        
        # All models failed
        logger.error("All OpenRouter models failed, using mock response")
        return self._mock_response(messages)
    
    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate mock response when API is unavailable"""
        # Extract the last user message for context
        last_message = messages[-1]["content"] if messages else ""
        
        # Simple keyword-based responses
        last_message_lower = last_message.lower()
        
        if "buy" in last_message_lower or "bullish" in last_message_lower:
            return "Based on my analysis, I believe this is a good buying opportunity. The market indicators suggest upward momentum."
        elif "sell" in last_message_lower or "bearish" in last_message_lower:
            return "I'm cautious about the current market conditions. It might be wise to take profits or reduce exposure."
        elif "hold" in last_message_lower or "neutral" in last_message_lower:
            return "I'm taking a wait-and-see approach. The market is showing mixed signals right now."
        else:
            return "After analyzing the available data, I'm maintaining a neutral stance while monitoring for clearer signals."
    
    async def generate_agent_reasoning(
        self,
        agent_name: str,
        agent_personality: str,
        persona_description: str,
        market_context: Dict[str, Any],
        memory: List[Dict[str, Any]],
        current_position: float
    ) -> Dict[str, Any]:
        """
        Generate agent reasoning and decision
        
        Returns:
            Dict with 'decision', 'confidence', 'reasoning', 'target_position'
        """
        # Build prompt
        memory_str = ""
        if memory:
            recent_memories = memory[-5:]  # Last 5 memories
            memory_str = "\n".join([
                f"- Step {m.get('step', '?')}: {m.get('observation', '')} -> Decision: {m.get('decision', 'hold')}"
                for m in recent_memories
            ])
        
        prompt = f"""You are {agent_name}, {persona_description}

Current Market Context:
- Asset: {market_context.get('asset_symbol', 'UNKNOWN')}
- Current Price: ${market_context.get('current_price', 0):.2f}
- Price Change (24h): {market_context.get('price_change_24h', 0):.2f}%
- RSI: {market_context.get('rsi', 50):.2f}
- MACD: {market_context.get('macd', 0):.4f}
- Volume: {market_context.get('volume', 0)}
- News Sentiment: {market_context.get('news_sentiment', 'neutral')}

Your Current Position: {current_position:.4f} units

Your Recent Memory:
{memory_str}

Based on your personality ({agent_personality}) and the market context, decide your next action.

Respond in this exact format:
DECISION: [buy/sell/hold]
CONFIDENCE: [0.0-1.0]
TARGET_POSITION: [number of units to hold, can be fractional]
REASONING: [your brief reasoning in 2-3 sentences]
"""
        
        messages = [
            {"role": "system", "content": "You are a financial trading agent making decisions based on market data and your personality."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.8, max_tokens=300)
        
        # Parse response
        result = {
            "decision": "hold",
            "confidence": 0.5,
            "reasoning": "No clear reasoning provided.",
            "target_position": current_position
        }
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('DECISION:'):
                decision = line.split(':', 1)[1].strip().lower()
                if decision in ['buy', 'sell', 'hold']:
                    result["decision"] = decision
            elif line.startswith('CONFIDENCE:'):
                try:
                    conf = float(line.split(':', 1)[1].strip())
                    result["confidence"] = max(0.0, min(1.0, conf))
                except ValueError:
                    pass
            elif line.startswith('TARGET_POSITION:'):
                try:
                    result["target_position"] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('REASONING:'):
                result["reasoning"] = line.split(':', 1)[1].strip()
        
        return result
    
    async def chat_with_agent(
        self,
        agent_name: str,
        agent_personality: str,
        persona_description: str,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """Chat with an agent to understand its reasoning"""
        
        prompt = f"""You are {agent_name}, {persona_description}

Current Context:
- Asset: {context.get('asset_symbol', 'UNKNOWN')}
- Current Decision: {context.get('current_decision', 'hold')}
- Confidence: {context.get('current_confidence', 0.5)}
- Your Reasoning: {context.get('reasoning', 'N/A')}

The user asks: "{message}"

Respond as {agent_name} would, staying in character. Be concise but informative."""
        
        messages = [
            {"role": "system", "content": f"You are {agent_name}, a trading agent with {agent_personality} personality."},
            {"role": "user", "content": prompt}
        ]
        
        return await self.chat_completion(messages, temperature=0.9, max_tokens=400)


# Global client instance
_openrouter_client: Optional[OpenRouterClient] = None


def get_openrouter_client(api_key: Optional[str] = None) -> OpenRouterClient:
    """Get or create OpenRouter client"""
    global _openrouter_client
    if _openrouter_client is None or api_key:
        _openrouter_client = OpenRouterClient(api_key)
    return _openrouter_client