from dataclasses import dataclass
import numpy as np

from derivatives_pricer.domain.interfaces import ValuationInstrument
from derivatives_pricer.domain.enums import ExerciseStyle, BarrierType
from derivatives_pricer.domain.payoff import BarrierPayoff, AsianPayoff, CallPayoff, PutPayoff
from derivatives_pricer.domain.exercise import EuropeanExercise

@dataclass(frozen=True)
class ExoticOption(ValuationInstrument):
    """
    Generic container for exotic options.
    Behavior is defined entirely by the Payoff Strategy.
    """
    payoff_strategy: any # Payoff Protocol
    expiry: float
    
    @property
    def expiration_time(self) -> float:
        return self.expiry

    @property
    def exercise_style(self) -> ExerciseStyle:
        return ExerciseStyle.EUROPEAN # Exotics usually European

    def calculate_payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        return self.payoff_strategy(spot_prices)

    # --- Factories ---

    @classmethod
    def barrier_up_out_call(cls, strike: float, barrier: float, expiry: float) -> 'ExoticOption':
        return cls(
            payoff_strategy=BarrierPayoff(
                strike=strike,
                barrier=barrier,
                barrier_type=BarrierType.UP_AND_OUT,
                underlying_payoff=CallPayoff(strike)
            ),
            expiry=expiry
        )

    @classmethod
    def asian_call(cls, strike: float, expiry: float) -> 'ExoticOption':
        return cls(
            payoff_strategy=AsianPayoff(strike=strike, underlying_payoff_type="Call"),
            expiry=expiry
        )
