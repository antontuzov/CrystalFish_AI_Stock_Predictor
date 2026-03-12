"""
Mathematical models for CrystalFish
Implements statistical forecasting models as baselines
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

# Optional imports - handle gracefully if not available
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logger.warning("statsmodels not available, ARIMA will use fallback")

try:
    from arch import arch_model
    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False
    logger.warning("arch not available, GARCH will use fallback")

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("prophet not available, will use fallback")

try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    logger.warning("ta not available, technical indicators will use fallback")


class MathModelsError(Exception):
    """Math models error"""
    pass


class MathModelsService:
    """Service for mathematical forecasting models"""
    
    def __init__(self):
        self.logger = structlog.get_logger()
    
    def calculate_technical_indicators(
        self, 
        prices: pd.Series, 
        volumes: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Calculate technical indicators
        
        Args:
            prices: Price series
            volumes: Volume series (optional)
            
        Returns:
            Dict with indicator values
        """
        if len(prices) < 30:
            return self._fallback_indicators(prices, volumes)
        
        try:
            indicators = {}
            
            # RSI
            if TA_AVAILABLE:
                indicators['rsi'] = ta.momentum.rsi(prices, window=14).iloc[-1]
            else:
                indicators['rsi'] = self._calculate_rsi(prices)
            
            # MACD
            if TA_AVAILABLE:
                macd = ta.trend.MACD(prices)
                indicators['macd'] = macd.macd().iloc[-1]
                indicators['macd_signal'] = macd.macd_signal().iloc[-1]
                indicators['macd_histogram'] = macd.macd_diff().iloc[-1]
            else:
                macd_vals = self._calculate_macd(prices)
                indicators.update(macd_vals)
            
            # Bollinger Bands
            if TA_AVAILABLE:
                bb = ta.volatility.BollingerBands(prices)
                indicators['bb_upper'] = bb.bollinger_hband().iloc[-1]
                indicators['bb_lower'] = bb.bollinger_lband().iloc[-1]
                indicators['bb_middle'] = bb.bollinger_mavg().iloc[-1]
                indicators['bb_width'] = bb.bollinger_wband().iloc[-1]
            else:
                bb_vals = self._calculate_bollinger_bands(prices)
                indicators.update(bb_vals)
            
            # Moving Averages
            indicators['sma_20'] = prices.rolling(window=20).mean().iloc[-1]
            indicators['sma_50'] = prices.rolling(window=50).mean().iloc[-1]
            indicators['ema_12'] = prices.ewm(span=12).mean().iloc[-1]
            
            # Volume indicators
            if volumes is not None and len(volumes) > 0:
                indicators['volume_sma'] = volumes.rolling(window=20).mean().iloc[-1]
                indicators['current_volume'] = volumes.iloc[-1]
            
            # Trend detection
            sma20 = indicators['sma_20']
            sma50 = indicators['sma_50']
            current_price = prices.iloc[-1]
            
            if current_price > sma20 > sma50:
                indicators['trend'] = 'bullish'
            elif current_price < sma20 < sma50:
                indicators['trend'] = 'bearish'
            else:
                indicators['trend'] = 'neutral'
            
            # Volatility (standard deviation of returns)
            returns = prices.pct_change().dropna()
            indicators['volatility_20d'] = returns.rolling(window=20).std().iloc[-1] * np.sqrt(365)
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}")
            return self._fallback_indicators(prices, volumes)
    
    def _fallback_indicators(self, prices: pd.Series, volumes: Optional[pd.Series]) -> Dict[str, Any]:
        """Fallback indicator calculation"""
        return {
            'rsi': 50.0,
            'macd': 0.0,
            'macd_signal': 0.0,
            'macd_histogram': 0.0,
            'bb_upper': prices.iloc[-1] * 1.05,
            'bb_lower': prices.iloc[-1] * 0.95,
            'bb_middle': prices.iloc[-1],
            'sma_20': prices.tail(20).mean(),
            'sma_50': prices.tail(50).mean() if len(prices) >= 50 else prices.mean(),
            'trend': 'neutral',
            'volatility_20d': 0.3
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI manually"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = prices.diff().dropna()
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)
        
        avg_gains = gains.rolling(window=period).mean().iloc[-1]
        avg_losses = losses.rolling(window=period).mean().iloc[-1]
        
        if avg_losses == 0:
            return 100.0
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate MACD manually"""
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        return {
            'macd': macd.iloc[-1],
            'macd_signal': signal.iloc[-1],
            'macd_histogram': histogram.iloc[-1]
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Dict[str, float]:
        """Calculate Bollinger Bands manually"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        return {
            'bb_upper': (sma + 2 * std).iloc[-1],
            'bb_lower': (sma - 2 * std).iloc[-1],
            'bb_middle': sma.iloc[-1],
            'bb_width': (4 * std / sma).iloc[-1]
        }
    
    def arima_forecast(
        self, 
        prices: pd.Series, 
        steps: int = 7,
        confidence: float = 0.95
    ) -> Dict[str, Any]:
        """
        ARIMA forecasting
        
        Args:
            prices: Historical price series
            steps: Number of steps to forecast
            confidence: Confidence level for intervals
            
        Returns:
            Dict with forecasts and confidence intervals
        """
        if not STATSMODELS_AVAILABLE or len(prices) < 30:
            return self._fallback_forecast(prices, steps, confidence)
        
        try:
            # Make series stationary if needed
            prices_clean = prices.dropna()
            
            # Fit ARIMA model (1,1,1) - simple but effective
            model = ARIMA(prices_clean, order=(1, 1, 1))
            fitted = model.fit()
            
            # Forecast
            forecast_result = fitted.get_forecast(steps=steps)
            forecast_mean = forecast_result.predicted_mean
            forecast_ci = forecast_result.conf_int(alpha=1-confidence)
            
            # Generate dates
            last_date = prices_clean.index[-1]
            if isinstance(last_date, pd.Timestamp):
                future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=steps, freq='D')
            else:
                future_dates = range(1, steps + 1)
            
            predictions = []
            for i in range(steps):
                predictions.append({
                    'step': i + 1,
                    'date': str(future_dates[i]) if isinstance(future_dates, pd.DatetimeIndex) else f"day_{i+1}",
                    'predicted_price': float(forecast_mean.iloc[i]),
                    'lower_bound': float(forecast_ci.iloc[i, 0]),
                    'upper_bound': float(forecast_ci.iloc[i, 1]),
                    'confidence': confidence
                })
            
            return {
                'model': 'ARIMA(1,1,1)',
                'predictions': predictions,
                'aic': float(fitted.aic),
                'bic': float(fitted.bic)
            }
            
        except Exception as e:
            self.logger.error(f"ARIMA error: {str(e)}")
            return self._fallback_forecast(prices, steps, confidence)
    
    def garch_volatility(
        self, 
        prices: pd.Series, 
        steps: int = 7
    ) -> Dict[str, Any]:
        """
        GARCH volatility forecasting
        
        Args:
            prices: Historical price series
            steps: Number of steps to forecast
            
        Returns:
            Dict with volatility forecasts
        """
        if not ARCH_AVAILABLE or len(prices) < 60:
            return self._fallback_volatility(prices, steps)
        
        try:
            # Calculate returns
            returns = prices.pct_change().dropna() * 100  # Convert to percentage
            
            # Fit GARCH(1,1)
            model = arch_model(returns, vol='Garch', p=1, q=1)
            fitted = model.fit(disp='off')
            
            # Forecast volatility
            forecast = fitted.forecast(horizon=steps)
            variance_forecast = forecast.variance.values[-1]
            
            volatility_forecast = np.sqrt(variance_forecast)
            
            predictions = []
            for i in range(steps):
                predictions.append({
                    'step': i + 1,
                    'predicted_volatility': float(volatility_forecast[i]) / 100,  # Convert back
                    'predicted_variance': float(variance_forecast[i]) / 10000
                })
            
            return {
                'model': 'GARCH(1,1)',
                'predictions': predictions,
                'current_volatility': float(np.std(returns)) / 100,
                'persistence': float(fitted.params.get('beta[1]', 0))
            }
            
        except Exception as e:
            self.logger.error(f"GARCH error: {str(e)}")
            return self._fallback_volatility(prices, steps)
    
    def prophet_forecast(
        self, 
        prices: pd.Series, 
        steps: int = 7,
        confidence: float = 0.95
    ) -> Dict[str, Any]:
        """
        Prophet forecasting
        
        Args:
            prices: Historical price series with datetime index
            steps: Number of steps to forecast
            confidence: Confidence level
            
        Returns:
            Dict with forecasts
        """
        if not PROPHET_AVAILABLE or len(prices) < 30:
            return self._fallback_forecast(prices, steps, confidence)
        
        try:
            # Prepare data for Prophet
            df = pd.DataFrame({
                'ds': prices.index,
                'y': prices.values
            })
            
            # Fit Prophet
            model = Prophet(
                interval_width=confidence,
                daily_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05
            )
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=steps)
            forecast = model.predict(future)
            
            # Extract predictions
            future_forecast = forecast.tail(steps)
            
            predictions = []
            for _, row in future_forecast.iterrows():
                predictions.append({
                    'step': len(predictions) + 1,
                    'date': str(row['ds']),
                    'predicted_price': float(row['yhat']),
                    'lower_bound': float(row['yhat_lower']),
                    'upper_bound': float(row['yhat_upper']),
                    'confidence': confidence
                })
            
            return {
                'model': 'Prophet',
                'predictions': predictions,
                'trend': 'upward' if predictions[-1]['predicted_price'] > prices.iloc[-1] else 'downward'
            }
            
        except Exception as e:
            self.logger.error(f"Prophet error: {str(e)}")
            return self._fallback_forecast(prices, steps, confidence)
    
    def _fallback_forecast(
        self, 
        prices: pd.Series, 
        steps: int, 
        confidence: float
    ) -> Dict[str, Any]:
        """Fallback forecast using simple methods"""
        last_price = prices.iloc[-1]
        
        # Calculate recent trend
        if len(prices) >= 7:
            weekly_return = (prices.iloc[-1] - prices.iloc[-7]) / prices.iloc[-7]
            daily_drift = weekly_return / 7
        else:
            daily_drift = 0
        
        # Calculate volatility
        returns = prices.pct_change().dropna()
        volatility = returns.std() if len(returns) > 0 else 0.02
        
        # Simple trend extrapolation with random walk
        predictions = []
        for i in range(steps):
            predicted = last_price * (1 + daily_drift * (i + 1))
            # Widen confidence intervals over time
            z_score = 1.96 if confidence >= 0.95 else 1.645
            margin = z_score * volatility * np.sqrt(i + 1) * last_price
            
            predictions.append({
                'step': i + 1,
                'date': f'day_{i+1}',
                'predicted_price': float(predicted),
                'lower_bound': float(max(0, predicted - margin)),
                'upper_bound': float(predicted + margin),
                'confidence': confidence
            })
        
        return {
            'model': 'Simple Trend Extrapolation',
            'predictions': predictions,
            'note': 'Fallback model used due to insufficient data or missing dependencies'
        }
    
    def _fallback_volatility(self, prices: pd.Series, steps: int) -> Dict[str, Any]:
        """Fallback volatility forecast"""
        returns = prices.pct_change().dropna()
        current_vol = returns.std() if len(returns) > 0 else 0.02
        
        predictions = []
        for i in range(steps):
            # Volatility tends to revert to mean
            predictions.append({
                'step': i + 1,
                'predicted_volatility': float(current_vol),
                'predicted_variance': float(current_vol ** 2)
            })
        
        return {
            'model': 'Historical Volatility',
            'predictions': predictions,
            'current_volatility': float(current_vol),
            'note': 'Fallback model used'
        }
    
    def ensemble_forecast(
        self, 
        prices: pd.Series, 
        steps: int = 7,
        confidence: float = 0.95
    ) -> Dict[str, Any]:
        """
        Ensemble forecast combining multiple models
        
        Args:
            prices: Historical price series
            steps: Number of steps to forecast
            confidence: Confidence level
            
        Returns:
            Dict with ensemble predictions
        """
        # Get individual forecasts
        arima_result = self.arima_forecast(prices, steps, confidence)
        prophet_result = self.prophet_forecast(prices, steps, confidence)
        
        # Simple average ensemble
        ensemble_predictions = []
        for i in range(steps):
            arima_pred = arima_result['predictions'][i]
            prophet_pred = prophet_result['predictions'][i]
            
            # Weighted average (can be tuned)
            arima_weight = 0.5
            prophet_weight = 0.5
            
            ensemble_price = (
                arima_pred['predicted_price'] * arima_weight + 
                prophet_pred['predicted_price'] * prophet_weight
            )
            
            # Conservative confidence intervals
            lower_bound = min(arima_pred['lower_bound'], prophet_pred['lower_bound'])
            upper_bound = max(arima_pred['upper_bound'], prophet_pred['upper_bound'])
            
            ensemble_predictions.append({
                'step': i + 1,
                'date': arima_pred.get('date', prophet_pred.get('date', f'day_{i+1}')),
                'predicted_price': float(ensemble_price),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'confidence': confidence,
                'arima_prediction': arima_pred['predicted_price'],
                'prophet_prediction': prophet_pred['predicted_price']
            })
        
        return {
            'model': 'Ensemble (ARIMA + Prophet)',
            'predictions': ensemble_predictions,
            'components': {
                'arima': arima_result,
                'prophet': prophet_result
            }
        }


# Global service instance
_math_service: Optional[MathModelsService] = None


def get_math_service() -> MathModelsService:
    """Get or create math models service"""
    global _math_service
    if _math_service is None:
        _math_service = MathModelsService()
    return _math_service