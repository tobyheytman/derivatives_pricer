import sys
import os
from datetime import date
import math

# Add project root to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from derivatives_pricer.core.types import OptionType
from derivatives_pricer.core.market_data import MarketData
from derivatives_pricer.instruments.fx import FXVanillaOption
from derivatives_pricer.engines.black_scholes import BlackScholesEngine

def test_fx_option_pricing():
    """Verify Garman-Kohlhagen pricing for FX options."""
    print("\nRunning FX Option Test...")
    valuation_date = date(2023, 1, 1)
    expiry_date = date(2024, 1, 1)
    
    # EURUSD
    
    market_data = MarketData(
        valuation_date=valuation_date,
        spots={"EURUSD": 1.10},
        rates={"EURUSD": 0.05}, # Domestic (USD)
        foreign_rates={"EURUSD": 0.03}, # Foreign (EUR)
        volatilities={"EURUSD": 0.10}
    )

    option = FXVanillaOption(
        currency_pair="EURUSD",
        strike=1.10,
        expiry_date=expiry_date,
        option_type=OptionType.CALL
    )

    engine = BlackScholesEngine(market_data)
    price = engine.price(option)

    
    # Manual Calc
    # d1 = (ln(1.1/1.1) + (0.05 - 0.03 + 0.5*0.01)*1) / 0.1
    # d1 = (0 + 0.025) / 0.1 = 0.25
    # d2 = 0.25 - 0.1 = 0.15
    # N(0.25) approx 0.5987
    # N(0.15) approx 0.5596
    # Price = S * e^-qT * N(d1) - K * e^-rT * N(d2)
    # Price = 1.1 * e^-0.03 * 0.5987 - 1.1 * e^-0.05 * 0.5596
    # Price = 1.1 * 0.9704 * 0.5987 - 1.1 * 0.9512 * 0.5596
    # Price = 0.6391 - 0.5855 = 0.0536
    
    print(f"Calculated FX Call Price: {price:.4f}")
    assert 0.0530 < price < 0.0540
    print("FX Option Test Passed")

if __name__ == "__main__":
    test_fx_option_pricing()
