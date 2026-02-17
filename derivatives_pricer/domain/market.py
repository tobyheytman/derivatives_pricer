from dataclasses import dataclass

@dataclass(frozen=True)
class MarketState:
    """
    Encapsulates the financial environment at a single point in time.
    Immutable to ensure thread safety and reasoning.
    """
    spot_price: float
    risk_free_rate: float  # Annualized, continuously compounded
    volatility: float      # Annualized standard deviation
    dividend_yield: float = 0.0 # Continuous dividend yield
