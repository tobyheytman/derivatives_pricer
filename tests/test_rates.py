import sys
import os
from datetime import date
import math

# Add project root to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from derivatives_pricer.core.types import YearFraction
from derivatives_pricer.core.market_data import MarketData
from derivatives_pricer.instruments.rates import InterestRateSwap
from derivatives_pricer.engines.discounting import DiscountingEngine
from derivatives_pricer.data.curves import ConstantYieldCurve

def test_swap_pricing():
    """Verify Interest Rate Swap pricing."""
    print("\nRunning Swap Pricing Test...")
    valuation_date = date(2023, 1, 1)
    start_date = date(2023, 1, 3) # Spot start
    maturity_date = date(2024, 1, 3) # 1 year swap
    
    # Flat curve at 5%
    curve = ConstantYieldCurve(0.05)
    
    market_data = MarketData(
        valuation_date=valuation_date,
        curves={"USD": curve}
    )

    # 1. Par Swap Test
    
    swap_high_rate = InterestRateSwap(
        notional=1_000_000,
        fixed_rate=0.06, # Paying 6% fixed, market is 5%
        start_date=start_date,
        maturity_date=maturity_date,
        frequency_months=6,
        payer=True
    )
    
    engine = DiscountingEngine(market_data)
    pv_high = engine.price(swap_high_rate)
    
    print(f"PV (Pay 6%, Market 5%): {pv_high:.2f}")
    assert pv_high < 0.0 # We pay more than we receive
    
    # 2. Receiver Swap
    swap_receiver = InterestRateSwap(
        notional=1_000_000,
        fixed_rate=0.06,
        start_date=start_date,
        maturity_date=maturity_date,
        frequency_months=6,
        payer=False # Receive fixed
    )
    
    pv_receiver = engine.price(swap_receiver)
    print(f"PV (Receive 6%, Market 5%): {pv_receiver:.2f}")
    assert pv_receiver > 0.0

    
    # Check symmetry
    assert abs(pv_high + pv_receiver) < 1e-5
    print("Swap Test Passed")

if __name__ == "__main__":
    test_swap_pricing()
