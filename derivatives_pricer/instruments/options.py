from dataclasses import dataclass
import numpy as np
from typing import Optional

from derivatives_pricer.domain.interfaces import ValuationInstrument
from derivatives_pricer.domain.enums import OptionType, ExerciseStyle
from derivatives_pricer.domain.payoff import Payoff, CallPayoff, PutPayoff
from derivatives_pricer.domain.exercise import ExerciseStrategy, EuropeanExercise, AmericanExercise

@dataclass(frozen=True)
class VanillaOption(ValuationInstrument):
    """
    A specific financial contract composed of distinct behaviors.
    It no longer contains logic for "how" to calculate payoff or exercise.
    It simply delegates to its strategies.
    
    Attributes:
        payoff (Payoff): The payoff strategy (e.g. Call, Put).
        exercise (ExerciseStrategy): The exercise strategy (e.g. American, European).
        expiry (float): Time to expiration.
    """
    payoff_strategy: Payoff
    exercise_strategy: ExerciseStrategy
    expiry: float
    strike: float # Kept for reference/analytic engines, though payoff owns it too.

    @property
    def expiration_time(self) -> float:
        return self.expiry

    @property
    def option_type(self) -> OptionType:
        if isinstance(self.payoff_strategy, CallPayoff):
            return OptionType.CALL
        return OptionType.PUT

    @property
    def exercise_style(self) -> ExerciseStyle:
        # Backward compatibility / Enum mapping
        if isinstance(self.exercise_strategy, AmericanExercise):
            return ExerciseStyle.AMERICAN
        return ExerciseStyle.EUROPEAN

    def calculate_payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        return self.payoff_strategy(spot_prices)
        
    def apply_exercise_condition(self, intrinsic: np.ndarray, continuation: np.ndarray) -> np.ndarray:
        return self.exercise_strategy.apply(intrinsic, continuation)

    # --- Factory Methods ---
    
    @classmethod
    def american_put(cls, strike: float, expiry: float) -> 'VanillaOption':
        """Creates an American Put Option."""
        return cls(
            payoff_strategy=PutPayoff(strike),
            exercise_strategy=AmericanExercise(),
            expiry=expiry,
            strike=strike
        )

    @classmethod
    def european_call(cls, strike: float, expiry: float) -> 'VanillaOption':
        """Creates a European Call Option."""
        return cls(
            payoff_strategy=CallPayoff(strike),
            exercise_strategy=EuropeanExercise(),
            expiry=expiry,
            strike=strike
        )

    @classmethod
    def european_put(cls, strike: float, expiry: float) -> 'VanillaOption':
        """Creates a European Put Option."""
        return cls(
            payoff_strategy=PutPayoff(strike),
            exercise_strategy=EuropeanExercise(),
            expiry=expiry,
            strike=strike
        )
