import numpy as np
from typing import Final
from abc import ABC, abstractmethod

from derivatives_pricer.domain.interfaces import ValuationInstrument
from derivatives_pricer.domain.market import MarketState
from derivatives_pricer.engines.interface import PricingEngine
from derivatives_pricer.common.validation import validate_positive

class StochasticProcess(ABC):
    @abstractmethod
    def simulate_paths(self, T: float, steps: int, paths: int) -> np.ndarray:
        pass

class GeometricBrownianMotion(StochasticProcess):
    def __init__(self, market: MarketState):
        self._S0 = market.spot_price
        self._r = market.risk_free_rate
        self._q = market.dividend_yield
        self._sigma = market.volatility

    def simulate_paths(self, T: float, steps: int, paths: int) -> np.ndarray:
        """Returns full path matrix [steps, paths]"""
        dt = T / steps
        drift = (self._r - self._q - 0.5 * self._sigma**2) * dt
        diffusion = self._sigma * np.sqrt(dt)
        
        # Paths including S0?
        # Standard MC often just needs steps.
        # [0] = S0
        # [1] = S0 * exp(...)
        
        Z = np.random.standard_normal((steps, paths))
        log_returns = drift + diffusion * Z
        
        # Cumulative Sum for paths
        cumulative_log_returns = np.cumsum(log_returns, axis=0)
        
        # Broadcast S0
        # prices[i] = S0 * exp(cum_ret[i])
        prices = self._S0 * np.exp(cumulative_log_returns)
        
        return prices

class MonteCarloEngine(PricingEngine):
    
    @validate_positive("num_paths")
    @validate_positive("num_steps")
    def __init__(self, num_paths: int = 10000, num_steps: int = 100):
        self._num_paths: Final[int] = num_paths
        self._num_steps: Final[int] = num_steps

    def price(self, instrument: ValuationInstrument, market_state: MarketState) -> float:
        process = GeometricBrownianMotion(market_state)
        
        # Get full paths [steps x paths]
        paths = process.simulate_paths(
            T=instrument.expiration_time,
            steps=self._num_steps,
            paths=self._num_paths
        )
        
        # Pass paths to instrument.
        # Instrument strategy handles 1D vs 2D.
        payoffs = instrument.calculate_payoff(paths)
        
        discount_factor = np.exp(-market_state.risk_free_rate * instrument.expiration_time)
        return float(np.mean(payoffs) * discount_factor)
