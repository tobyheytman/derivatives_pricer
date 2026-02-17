import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum

print("This is an initial test")


@dataclass
class MarketData(Enum):
    price: float
    volume: float
    timestamp: pd.Timestamp
