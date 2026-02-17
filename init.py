from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Dict, Final
import numpy as np
from scipy.interpolate import interp1d
from .instruments import ExerciseStyle, OptionType, YearFraction


class DayCountConvertion(Enum):
    ACT_360 = auto()
    ACT_365 = auto()
    THIRTY_360 = auto()


class YieldCurve(ABC):
    @abstractmethod
    def discount_factor(self, t: YearFraction) -> float:
        pass
