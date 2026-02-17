import numpy as np
from abc import ABC, abstractmethod
from .enums import ExerciseStyle

class ValuationInstrument(ABC):
    """
    Abstract Base Class for any tradable asset.
    The instrument is responsible for defining its own payoff and exercise logic.
    """
    @property
    @abstractmethod
    def expiration_time(self) -> float:
        """Time to expiration in years."""
        pass

    @property
    @abstractmethod
    def exercise_style(self) -> ExerciseStyle:
        """The exercise style of the instrument."""
        pass

    @abstractmethod
    def calculate_payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        """
        Vectorized payoff calculation.
        
        Args:
            spot_prices: A numpy array of underlying asset prices.
            
        Returns:
            A numpy array of payoff values corresponding to the spot prices.
        """
        pass
