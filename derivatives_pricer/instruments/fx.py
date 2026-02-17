from dataclasses import dataclass
from datetime import date
from typing import Any

from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.core.types import OptionType, ExerciseStyle

@dataclass
class FXVanillaOption(Instrument):
    """Standard European FX Option."""
    currency_pair: str # e.g. "EURUSD"
    strike: float
    expiry_date: date
    option_type: OptionType
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN

    def payoff(self, market_data: Any) -> float:
        """
        Calculate intrinsic value (payoff at expiry).
        """
        spot = market_data.get_spot(self.currency_pair)
        if self.option_type == OptionType.CALL:
            return max(spot - self.strike, 0.0)
        else:
            return max(self.strike - spot, 0.0)

    def is_expired(self, valuation_date: date) -> bool:
        return valuation_date > self.expiry_date
