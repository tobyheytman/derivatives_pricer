from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict

from derivatives_pricer.core.types import YearFraction

class Instrument(ABC):
    """Abstract base class for all financial instruments."""
    
    @abstractmethod
    def payoff(self, market_data: Any) -> float:
        """Calculate the payoff of the instrument given market data."""
        pass

    @abstractmethod
    def is_expired(self, valuation_date: date) -> bool:
        """Check if the instrument is expired on the given date."""
        pass
