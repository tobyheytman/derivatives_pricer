from abc import ABC, abstractmethod
from typing import Any

from derivatives_pricer.core.instrument import Instrument

class PricingModel(ABC):
    """Abstract base class for all pricing models."""

    @abstractmethod
    def price(self, instrument: Instrument, market_data: Any) -> float:
        """Calculate the price of the instrument given market data."""
        pass
