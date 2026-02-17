from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.core.market_data import MarketData

class PricingEngine(ABC):
    """
    Abstract base class for Valid Pricing Engines.
    
    A Pricing Engine is initialized with a specific MarketData context.
    It exposes a `price` method that accepts an Instrument.
    """
    
    def __init__(self, market_data: MarketData):
        self.market_data = market_data

    @abstractmethod
    def price(self, instrument: Instrument) -> float:
        """
        Calculates the fair value of the given instrument.
        
        Args:
            instrument: The financial instrument to price.
            
        Returns:
            The calculated price (float).
        """
        pass
