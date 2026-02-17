import numpy as np
from enum import Enum, auto
from typing import NewType, Protocol, runtime_checkable, Final

YearFraction = NewType("YearFraction", float)

class OptionType(Enum):
    CALL = auto()
    PUT = auto()


class ExerciseStyle(Enum):
    AMERICAN = auto()
    EUROPEAN = auto()
    BERMUDAN = auto()
