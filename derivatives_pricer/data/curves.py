import numpy as np
from abc import ABC, abstractmethod
from derivatives_pricer.core.types import YearFraction, DayCountConvention

class YieldCurve(ABC):
    """Abstract base class for yield curves."""
    
    @abstractmethod
    def discount_factor(self, t: YearFraction) -> float:
        """Calculate the discount factor for a given time t."""
        pass
        
    @abstractmethod
    def zero_rate(self, t: YearFraction, compounding: str = "continuous") -> float:
        """Calculate the zero rate for a given time t."""
        pass

class ConstantYieldCurve(YieldCurve):
    """Yield curve with a constant continuous rate."""
    
    def __init__(self, rate: float):
        self.rate = rate

    def discount_factor(self, t: YearFraction) -> float:
        return np.exp(-self.rate * t)

    def zero_rate(self, t: YearFraction, compounding: str = "continuous") -> float:
        return self.rate

