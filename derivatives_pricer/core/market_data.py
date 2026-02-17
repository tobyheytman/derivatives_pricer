from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from datetime import date
from derivatives_pricer.core.types import YearFraction

@dataclass
class MarketData:
    """
    Container for market data required for pricing.
    Serves as the context for PricingEngines.
    """
    valuation_date: date
    spots: Dict[str, float] = field(default_factory=dict)
    rates: Dict[str, float] = field(default_factory=dict) # Domestic risk-free rates
    foreign_rates: Dict[str, float] = field(default_factory=dict) # Foreign risk-free rates (for FX)
    volatilities: Dict[str, float] = field(default_factory=dict) # Implied volatilities
    curves: Dict[str, Any] = field(default_factory=dict) # YieldCurve objects

    def get_spot(self, ticker: str) -> float:
        """Returns the spot price for a given ticker."""
        if ticker not in self.spots:
            raise KeyError(f"Spot price for {ticker} not found in market data.")
        return self.spots[ticker]

    def get_rate(self, ticker: str) -> float:
        """Returns the domestic risk-free rate for a given ticker/currency."""
        return self.rates.get(ticker, 0.0)

    def get_foreign_rate(self, ticker: str) -> float:
        """Returns the foreign risk-free rate for a given ticker/currency pair."""
        return self.foreign_rates.get(ticker, 0.0)

    def get_volatility(self, ticker: str) -> float:
        """Returns the implied volatility for a given ticker."""
        return self.volatilities.get(ticker, 0.0)
    
    def get_curve(self, currency: str) -> Any:
        """Returns the yield curve for a given currency."""
        return self.curves.get(currency)
