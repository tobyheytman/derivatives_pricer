import numpy as np
from scipy.stats import norm
from typing import Any
from datetime import date

from derivatives_pricer.core.model import PricingModel
from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.core.types import OptionType, YearFraction
from derivatives_pricer.instruments.equity import EquityVanillaOption
from derivatives_pricer.instruments.fx import FXVanillaOption

class BlackScholesModel(PricingModel):
    """Analytical Black-Scholes pricing model for European options."""

    def price(self, instrument: Instrument, market_data: Any) -> float:
        if not isinstance(instrument, (EquityVanillaOption, FXVanillaOption)):
            raise ValueError("BlackScholesModel only supports EquityVanillaOption and FXVanillaOption")
        
        # Extract market data
        if hasattr(instrument, 'asset_name'):
            ticker = instrument.asset_name
        elif hasattr(instrument, 'currency_pair'):
            ticker = instrument.currency_pair
        else:
            raise ValueError("Instrument must have asset_name or currency_pair")

        S = market_data.get_spot(ticker)
        K = instrument.strike
        
        valuation_date = getattr(market_data, 'valuation_date', date.today())
        
        T_days = (instrument.expiry_date - valuation_date).days
        T = YearFraction(T_days / 365.0) # Simple ACT/365 for now
        
        if T <= 0:
            return instrument.payoff(market_data)

        # Get rate and vol. 
        r = market_data.get_rate(ticker) if hasattr(market_data, 'get_rate') else 0.0
        sigma = market_data.get_vol(ticker) if hasattr(market_data, 'get_vol') else 0.2
        
        # Dividend yield or foreign rate
        q = 0.0
        if isinstance(instrument, FXVanillaOption):
            q = market_data.get_foreign_rate(ticker) if hasattr(market_data, 'get_foreign_rate') else 0.0
        
        # Generalized BS:
        # d1 = (ln(S/K) + (r - q + 0.5*sigma^2)T) / (sigma*sqrt(T))
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if instrument.option_type == OptionType.CALL:
            price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

        return price

