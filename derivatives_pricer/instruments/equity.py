from dataclasses import dataclass
from datetime import date
from typing import Any, List

from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.core.types import OptionType, ExerciseStyle, BarrierType

@dataclass
class EquityVanillaOption(Instrument):
    """Standard European Equity Option."""
    asset_name: str
    strike: float
    expiry_date: date
    option_type: OptionType
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN

    def payoff(self, market_data: Any) -> float:
        """
        Calculate intrinsic value (payoff at expiry).
        max(S - K, 0) for Call
        max(K - S, 0) for Put
        """
        spot = market_data.get_spot(self.asset_name)
        if self.option_type == OptionType.CALL:
            return max(spot - self.strike, 0.0)
        else:
            return max(self.strike - spot, 0.0)

    def is_expired(self, valuation_date: date) -> bool:
        return valuation_date > self.expiry_date

@dataclass
class EquityBarrierOption(Instrument):
    """Barrier Option (Single Barrier)."""
    asset_name: str
    strike: float
    barrier: float
    expiry_date: date
    option_type: OptionType
    barrier_type: BarrierType
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN

    def payoff(self, market_data: Any) -> float:
        # Path dependent, cannot be determined by single spot at expiry nicely
        # But this method is required by ABC. 
        # For path-dependent instruments, payoff might need path data or be unused by analytical models.
        # For now, return intrinsic if barrier condition is not checked here (assuming it was active)
        # Realistically, payoff needs more context or is only called by MC engine which handles barrier.
        # Let's return intrinsic value as a placeholder
        spot = market_data.get_spot(self.asset_name)
        if self.option_type == OptionType.CALL:
            return max(spot - self.strike, 0.0)
        else:
            return max(self.strike - spot, 0.0)

    def is_expired(self, valuation_date: date) -> bool:
        return valuation_date > self.expiry_date

@dataclass
class EquityAsianOption(Instrument):
    """Asian Option (Arithmetic Average)."""
    asset_name: str
    strike: float
    expiry_date: date
    option_type: OptionType
    fixing_dates: List[date] = None # For discrete fixing. If None, assume continuous/daily.
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN

    def payoff(self, market_data: Any) -> float:
        # Also path dependent.
        spot = market_data.get_spot(self.asset_name)
        # Placeholder
        if self.option_type == OptionType.CALL:
            return max(spot - self.strike, 0.0)
        else:
            return max(self.strike - spot, 0.0)

    def is_expired(self, valuation_date: date) -> bool:
        return valuation_date > self.expiry_date
