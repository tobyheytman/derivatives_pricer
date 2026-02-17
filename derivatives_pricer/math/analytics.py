import numpy as np
from scipy.stats import norm

def black_scholes_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
    is_call: bool = True
) -> float:
    """
    Calculate Black-Scholes price for a European option.
    
    Args:
        spot: Current underlying price (S)
        strike: Option strike price (K)
        time_to_expiry: Time to expiry in years (T)
        risk_free_rate: Risk-free interest rate (r)
        volatility: Annualized volatility (sigma)
        dividend_yield: Continuous dividend yield or foreign rate (q)
        is_call: True for Call, False for Put
        
    Returns:
        Option price
    """
    if time_to_expiry <= 0:
        return max(spot - strike, 0.0) if is_call else max(strike - spot, 0.0)

    d1 = (np.log(spot / strike) + (risk_free_rate - dividend_yield + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)

    if is_call:
        price = spot * np.exp(-dividend_yield * time_to_expiry) * norm.cdf(d1) - strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
    else:
        price = strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - spot * np.exp(-dividend_yield * time_to_expiry) * norm.cdf(-d1)
        
    return float(price)
