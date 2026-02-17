from enum import Enum, auto

class OptionType(Enum):
    CALL = auto()
    PUT = auto()

class ExerciseStyle(Enum):
    AMERICAN = auto()
    EUROPEAN = auto()
    BERMUDAN = auto()

class BarrierType(Enum):
    UP_AND_OUT = auto()
    UP_AND_IN = auto()
    DOWN_AND_OUT = auto()
    DOWN_AND_IN = auto()
