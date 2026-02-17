from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from derivatives_pricer.domain.enums import BarrierType

class Payoff(ABC):
    """
    Strategy interface for Payoff calculation.
    Supports both path-dependent and path-independent logic.
    Input `prices` can be:
        - 1D Array: Terminal prices [paths]
        - 2D Array: Full paths [steps, paths]
    """
    @abstractmethod
    def __call__(self, prices: np.ndarray) -> np.ndarray:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

@dataclass(frozen=True)
class VanillaPayoff(Payoff):
    strike: float

    def __call__(self, prices: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def _get_terminal_prices(self, prices: np.ndarray) -> np.ndarray:
        """Helper to extract terminal prices from potential path matrix."""
        # If 2D (steps, paths), take last step.
        if prices.ndim == 2:
            return prices[-1]
        return prices

@dataclass(frozen=True)
class CallPayoff(VanillaPayoff):
    def __call__(self, prices: np.ndarray) -> np.ndarray:
        S = self._get_terminal_prices(prices)
        return np.maximum(S - self.strike, 0.0)
    
    @property
    def name(self) -> str:
        return "Call"

@dataclass(frozen=True)
class PutPayoff(VanillaPayoff):
    def __call__(self, prices: np.ndarray) -> np.ndarray:
        S = self._get_terminal_prices(prices)
        return np.maximum(self.strike - S, 0.0)
        
    @property
    def name(self) -> str:
        return "Put"

# --- Exotic Payoffs ---

@dataclass(frozen=True)
class BarrierPayoff(Payoff):
    strike: float
    barrier: float
    barrier_type: BarrierType
    underlying_payoff: Payoff # e.g. CallPayoff

    def __call__(self, prices: np.ndarray) -> np.ndarray:
        # Requires full paths
        if prices.ndim != 2:
            raise ValueError("BarrierPayoff requires Price Paths (2D array)")
            
        # prices: [steps, paths]
        max_prices = np.max(prices, axis=0)
        min_prices = np.min(prices, axis=0)
        
        active = np.ones(prices.shape[1], dtype=bool)
        
        if self.barrier_type == BarrierType.UP_AND_OUT:
            active = max_prices < self.barrier
        elif self.barrier_type == BarrierType.DOWN_AND_OUT:
            active = min_prices > self.barrier
        elif self.barrier_type == BarrierType.UP_AND_IN:
            active = max_prices >= self.barrier
        elif self.barrier_type == BarrierType.DOWN_AND_IN:
            active = min_prices <= self.barrier
            
        # Calculate raw payoff
        raw_payoff = self.underlying_payoff(prices)
        
        # Apply barrier condition
        return np.where(active, raw_payoff, 0.0)

    @property
    def name(self) -> str:
        return f"Barrier ({self.barrier_type.name})"

@dataclass(frozen=True)
class AsianPayoff(Payoff):
    strike: float
    underlying_payoff_type: str = "Call" # Simple flag for now, or compose? Composition is better.

    def __call__(self, prices: np.ndarray) -> np.ndarray:
        if prices.ndim != 2:
            raise ValueError("AsianPayoff requires Price Paths (2D array)")
            
        # Arithmetic Average
        average_prices = np.mean(prices, axis=0)
        
        if self.underlying_payoff_type == "Call":
            return np.maximum(average_prices - self.strike, 0.0)
        else:
            return np.maximum(self.strike - average_prices, 0.0)

    @property
    def name(self) -> str:
        return "Asian (Arithmetic)"
