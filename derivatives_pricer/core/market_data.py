from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from datetime import date

@dataclass
class MarketData:
    """Container for market data required for pricing."""
    valuation_date: date
    spots: Dict[str, float] = field(default_factory=dict)
    rates: Dict[str, float] = field(default_factory=dict) # simplified: constant rates per currency/asset
    foreign_rates: Dict[str, float] = field(default_factory=dict) # For FX pricing
    volatilities: Dict[str, float] = field(default_factory=dict) # simplified: constant vols

    # TODO: Add curves and surfaces here
    curves: Dict[str, Any] = field(default_factory=dict)
    surfaces: Dict[str, Any] = field(default_factory=dict)

    def get_spot(self, ticker: str) -> float:
        return self.spots.get(ticker, 0.0)

    def get_rate(self, ticker: str) -> float:
        """
        Get the domestic risk-free rate relevant for the ticker.
        """
        return self.rates.get(ticker, 0.0)

    def get_foreign_rate(self, ticker: str) -> float:
        """
        Get the foreign risk-free rate relevant for the ticker usage in FX.
        """
        return self.foreign_rates.get(ticker, 0.0)


    def get_vol(self, ticker: str) -> float:
        """
        Get the implied volatility for the ticker.
        In a real system this would look up the volatility surface for the given strike/expiry.
        """
        return self.volatilities.get(ticker, 0.0)
