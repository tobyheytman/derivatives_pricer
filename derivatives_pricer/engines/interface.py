from abc import ABC, abstractmethod
from typing import Final

from derivatives_pricer.domain.interfaces import ValuationInstrument
from derivatives_pricer.domain.market import MarketState

class PricingEngine(ABC):
    """
    Abstract base class for all pricing methods.
    Engines are stateless regarding the instrument but may hold configuration.
    """
    
    @abstractmethod
    def price(self, instrument: ValuationInstrument, market_state: MarketState) -> float:
        """
        Calculates the fair value of the instrument given the market state.
        """
        pass
