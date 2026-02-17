from dataclasses import dataclass
from datetime import date
from typing import Any

from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.core.types import OptionType

@dataclass
class CommodityFuture(Instrument):
    """Commodity Future Contract."""
    commodity_name: str
    delivery_date: date
    strike_price: float # For a future, this is the entered price usually, or 0 for spot?
    # standard future: payoff is S_T - K

    def payoff(self, market_data: Any) -> float:
        spot = market_data.get_spot(self.commodity_name)
        return spot - self.strike_price

    def is_expired(self, valuation_date: date) -> bool:
        return valuation_date > self.delivery_date

@dataclass
class CommodityOption(Instrument):
    """Option on a Commodity Future."""
    commodity_name: str
    strike: float
    expiry_date: date
    option_type: OptionType

    def payoff(self, market_data: Any) -> float:
        # Assuming payoff based on spot for simplicity in MVP
        spot = market_data.get_spot(self.commodity_name)
        if self.option_type == OptionType.CALL:
            return max(spot - self.strike, 0.0)
        else:
            return max(self.strike - spot, 0.0)

    def is_expired(self, valuation_date: date) -> bool:
        return valuation_date > self.expiry_date
