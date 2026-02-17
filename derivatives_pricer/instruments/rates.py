from dataclasses import dataclass
from typing import Any, List
from datetime import date

from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.core.types import YearFraction

@dataclass
class InterestRateSwap(Instrument):
    """Interest Rate Swap (Fixed vs Floating)."""
    notional: float
    fixed_rate: float
    start_date: date
    maturity_date: date
    frequency_months: int = 6 # Semiannual
    payer: bool = True # If true, pay fixed, receive float

    def payoff(self, market_data: Any) -> float:
        """
        Calculates swap PV.
        PV = PV(Float) - PV(Fixed) (if receiver)
        Since at par inception PV(Float) approx Notional (simplification),
        but generally calculated as sum of discounted cash flows.
        """
        # This is typically handled by a PricingModel (DCF), not intrinsic payoff logic.
        # But for completeness, let's just return 0 here as it's model dependent.
        return 0.0

    def is_expired(self, valuation_date: date) -> bool:
        return valuation_date > self.maturity_date
