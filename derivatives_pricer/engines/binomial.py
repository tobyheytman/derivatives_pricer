import numpy as np
from typing import Final
from dataclasses import dataclass

from derivatives_pricer.domain.interfaces import ValuationInstrument
from derivatives_pricer.domain.market import MarketState
from derivatives_pricer.engines.interface import PricingEngine
from derivatives_pricer.common.validation import validate_positive
from derivatives_pricer.instruments.options import VanillaOption

@dataclass(frozen=True)
class BinomialParams:
    u: float
    d: float
    p: float
    df: float

class BinomialParameterizer:
    @staticmethod
    def calculate(market: MarketState, T: float, steps: int) -> BinomialParams:
        dt = T / steps
        r = market.risk_free_rate
        q = market.dividend_yield
        sigma = market.volatility
        
        u = np.exp(sigma * np.sqrt(dt))
        d = 1.0 / u
        p = (np.exp((r - q) * dt) - d) / (u - d)
        df = np.exp(-r * dt)
        
        return BinomialParams(u, d, p, df)

class BinomialLattice:
    def __init__(self, market: MarketState, params: BinomialParams, steps: int):
        self._market = market
        self._params = params
        self._steps = steps
        self._spot_prices: np.ndarray = self._initialize_spot_prices()

    def _initialize_spot_prices(self) -> np.ndarray:
        indices = np.arange(self._steps + 1)
        u_pow = self._steps - indices
        d_pow = indices
        return self._market.spot_price * (self._params.u ** u_pow) * (self._params.d ** d_pow)

    def backward_induction_step(self, 
                                current_values: np.ndarray, 
                                instrument: VanillaOption) -> np.ndarray:
        # Continuation
        continuation = self._params.df * (
            self._params.p * current_values[:-1] + 
            (1 - self._params.p) * current_values[1:]
        )
        
        # Spot update
        self._spot_prices = self._spot_prices[:-1] / self._params.u
        
        # Intrinsic
        # NOTE: Payoff strategy expects paths. `spot_prices` is 1D array of terminal prices (nodes).
        # We can pass it directly as 1D array. The Payoff strategy (Vanilla) handles this.
        intrinsic = instrument.calculate_payoff(self._spot_prices)
        
        return instrument.apply_exercise_condition(intrinsic, continuation)

class BinomialPricingEngine(PricingEngine):
    
    @validate_positive("step_count")
    def __init__(self, step_count: int = 1000):
        self._steps: Final[int] = step_count

    def price(self, instrument: ValuationInstrument, market_state: MarketState) -> float:
        if not isinstance(instrument, VanillaOption):
             raise TypeError("BinomialEngine currently requires VanillaOption (composed)")

        params = BinomialParameterizer.calculate(
            market_state, 
            instrument.expiration_time, 
            self._steps
        )
        
        lattice = BinomialLattice(
            market_state, 
            params, 
            self._steps
        )
        
        # Terminal Values
        # Pass 1D array of spots.
        values = instrument.calculate_payoff(lattice._spot_prices)
        
        # Rollback
        for _ in range(self._steps):
            values = lattice.backward_induction_step(values, instrument)
            
        return float(values[0])
