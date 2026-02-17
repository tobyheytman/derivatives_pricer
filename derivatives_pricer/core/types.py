from enum import Enum, auto
from typing import NewType

YearFraction = NewType("YearFraction", float)

class OptionType(Enum):
    CALL = auto()
    PUT = auto()

class ExerciseStyle(Enum):
    AMERICAN = auto()
    EUROPEAN = auto()
    BERMUDAN = auto()

class DayCountConvention(Enum):
    ACT_360 = auto()
    ACT_365 = auto()
    THIRTY_360 = auto()

class BarrierType(Enum):
    UP_AND_OUT = auto()
    UP_AND_IN = auto()
    DOWN_AND_OUT = auto()
    DOWN_AND_IN = auto()

