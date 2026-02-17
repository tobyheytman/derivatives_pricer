from abc import ABC, abstractmethod
import numpy as np
from derivatives_pricer.domain.enums import ExerciseStyle  # Assuming enums still exist or we deprecate usage

class ExerciseStrategy(ABC):
    """
    Strategy for determining option value given continuation and intrinsic values.
    """
    @abstractmethod
    def apply(self, intrinsic_value: np.ndarray, continuation_value: np.ndarray) -> np.ndarray:
        pass
        
    @property
    @abstractmethod
    def style(self) -> str:
        pass

class EuropeanExercise(ExerciseStrategy):
    """No early exercise. Value is continuation value."""
    def apply(self, intrinsic_value: np.ndarray, continuation_value: np.ndarray) -> np.ndarray:
        return continuation_value
        
    @property
    def style(self) -> str:
        return "European"

class AmericanExercise(ExerciseStrategy):
    """Early exercise allowed. Max(Intrinsic, Continuation)."""
    def apply(self, intrinsic_value: np.ndarray, continuation_value: np.ndarray) -> np.ndarray:
        return np.maximum(intrinsic_value, continuation_value)

    @property
    def style(self) -> str:
        return "American"
