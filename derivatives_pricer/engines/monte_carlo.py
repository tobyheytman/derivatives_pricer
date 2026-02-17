import numpy as np
from typing import Final
from abc import ABC, abstractmethod

from derivatives_pricer.domain.interfaces import ValuationInstrument
from derivatives_pricer.domain.market import MarketState
from derivatives_pricer.engines.interface import PricingEngine
from derivatives_pricer.common.validation import validate_positive

class StochasticProcess(ABC):
    @abstractmethod
    def simulate_terminal_prices(self, T: float, steps: int, paths: int) -> np.ndarray:
        pass

class GeometricBrownianMotion(StochasticProcess):
    def __init__(self, market: MarketState):
        self._S0 = market.spot_price
        self._r = market.risk_free_rate
        self._q = market.dividend_yield
        self._sigma = market.volatility

    def simulate_terminal_prices(self, T: float, steps: int, paths: int) -> np.ndarray:
        dt = T / steps
        drift = (self._r - self._q - 0.5 * self._sigma**2) * dt
        diffusion = self._sigma * np.sqrt(dt)
        Z = np.random.standard_normal((steps, paths))
        total_log_return = np.sum(drift + diffusion * Z, axis=0)
        return self._S0 * np.exp(total_log_return)

class MonteCarloEngine(PricingEngine):
    
    @validate_positive("num_paths")
    @validate_positive("num_steps")
    def __init__(self, num_paths: int = 10000, num_steps: int = 100):
        self._num_paths: Final[int] = num_paths
        self._num_steps: Final[int] = num_steps

    def price(self, instrument: ValuationInstrument, market_state: MarketState) -> float:
        process = GeometricBrownianMotion(market_state)
        
        final_prices = process.simulate_terminal_prices(
            T=instrument.expiration_time,
            steps=self._num_steps,
            paths=self._num_paths
        )
        
        payoffs = instrument.calculate_payoff(final_prices)
        discount_factor = np.exp(-market_state.risk_free_rate * instrument.expiration_time)
        return float(np.mean(payoffs) * discount_factor)
