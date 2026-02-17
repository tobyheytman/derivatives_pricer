from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np

class Payoff(ABC):
    """
    Strategy interface for Payoff calculation.
    """
    @abstractmethod
    def __call__(self, spot_prices: np.ndarray) -> np.ndarray:
        """Calculate payoff given spot prices."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Description of the payoff type."""
        pass

@dataclass(frozen=True)
class VanillaPayoff(Payoff):
    """
    Base class for Vanilla Payoffs (Strike-dependent).
    """
    strike: float

    def __call__(self, spot_prices: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Must implement in subclass")

    @property
    def name(self) -> str:
        return "Vanilla"

@dataclass(frozen=True)
class CallPayoff(VanillaPayoff):
    """Max(S - K, 0)"""
    def __call__(self, spot_prices: np.ndarray) -> np.ndarray:
        return np.maximum(spot_prices - self.strike, 0.0)
    
    @property
    def name(self) -> str:
        return "Call"

@dataclass(frozen=True)
class PutPayoff(VanillaPayoff):
    """Max(K - S, 0)"""
    def __call__(self, spot_prices: np.ndarray) -> np.ndarray:
        return np.maximum(self.strike - spot_prices, 0.0)
        
    @property
    def name(self) -> str:
        return "Put"
