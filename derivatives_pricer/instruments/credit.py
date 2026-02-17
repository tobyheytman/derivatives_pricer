from dataclasses import dataclass
from datetime import date
from typing import Any

from derivatives_pricer.core.instrument import Instrument

@dataclass
class CreditDefaultSwap(Instrument):
    """Credit Default Swap (CDS)."""
    reference_entity: str
    notional: float
    spread_bps: float
    maturity_date: date
    protection_buyer: bool = True # Buyer pays premium, receives protection

    def payoff(self, market_data: Any) -> float:
        # Contingent on default event.
        # In a real model, this would check if default occurred.
        return 0.0

    def is_expired(self, valuation_date: date) -> bool:
        return valuation_date > self.maturity_date
