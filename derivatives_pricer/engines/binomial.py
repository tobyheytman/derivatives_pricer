import numpy as np
from typing import Final, Tuple
from dataclasses import dataclass

from derivatives_pricer.domain.enums import ExerciseStyle
from derivatives_pricer.domain.interfaces import ValuationInstrument
from derivatives_pricer.domain.market import MarketState
from derivatives_pricer.engines.interface import PricingEngine
from derivatives_pricer.common.validation import validate_positive
from derivatives_pricer.instruments.options import VanillaOption

# --- 1. Parameterization Strategy ---

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

# --- 2. The Lattice State ---

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
        """
        Perform one backward step.
        Relies on the Instrument's Exercise Strategy to determine node value.
        """
        # 1. Calculate Continuation Value (Expectation under Q)
        continuation = self._params.df * (
            self._params.p * current_values[:-1] + 
            (1 - self._params.p) * current_values[1:]
        )
        
        # 2. Update Spot Prices for current step (for intrinsic calculation)
        # S_{i} at time k = S_{i} at time k+1 / u
        self._spot_prices = self._spot_prices[:-1] / self._params.u
        
        # 3. Calculate Intrinsic Value
        intrinsic = instrument.calculate_payoff(self._spot_prices)
        
        # 4. Delegate to Exercise Strategy (Polymorphism)
        # "Should I exercise or hold?" -> Strategy decides.
        return instrument.apply_exercise_condition(intrinsic, continuation)

# --- 3. The Orchestrator Engine ---

class BinomialPricingEngine(PricingEngine):
    
    @validate_positive("step_count")
    def __init__(self, step_count: int = 1000):
        self._steps: Final[int] = step_count

    def price(self, instrument: ValuationInstrument, market_state: MarketState) -> float:
        # TODO: Engine interface uses base ValuationInstrument, 
        # but Binomial specifically needs `apply_exercise_condition`.
        # Ideally, `ValuationInstrument` has `apply_exercise_condition`.
        # For now, explicit check or cast for VanillaOption since typically Lattice implies Vanilla/American.
        if not isinstance(instrument, VanillaOption):
             raise TypeError("BinomialEngine currently requires VanillaOption (composed)")

        # 1. Params
        params = BinomialParameterizer.calculate(
            market_state, 
            instrument.expiration_time, 
            self._steps
        )
        
        # 2. Lattice
        lattice = BinomialLattice(
            market_state, 
            params, 
            self._steps
        )
        
        # 3. Terminal Condition
        # We need the spots at maturity first.
        values = instrument.calculate_payoff(lattice._spot_prices)
        
        # 4. Rollback
        for _ in range(self._steps):
            values = lattice.backward_induction_step(values, instrument)
            
        return float(values[0])
