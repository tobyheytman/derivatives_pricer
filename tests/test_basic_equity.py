import sys
import os
from datetime import date


# Add project root to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from derivatives_pricer.core.types import OptionType, ExerciseStyle
from derivatives_pricer.core.market_data import MarketData
from derivatives_pricer.instruments.equity import EquityVanillaOption
from derivatives_pricer.engines.black_scholes import BlackScholesEngine

def test_black_scholes_call():
    # Setup market data
    valuation_date = date(2023, 1, 1)
    expiry_date = date(2024, 1, 1) # 1 year
    
    market_data = MarketData(
        valuation_date=valuation_date,
        spots={"AAPL": 100.0},
        rates={"AAPL": 0.05},
        volatilities={"AAPL": 0.2}
    )

    # Setup instrument
    call_option = EquityVanillaOption(
        asset_name="AAPL",
        strike=100.0,
        expiry_date=expiry_date,
        option_type=OptionType.CALL
    )

    # Setup engine
    engine = BlackScholesEngine(market_data)

    # Calculate price
    price = engine.price(call_option)
    
    # Expected price (approximate BS value)
    # S=100, K=100, T=1, r=0.05, sigma=0.2
    # Call = 10.45
    
    print(f"Calculated Call Price: {price}")
    assert 10.40 < price < 10.50

def test_black_scholes_put():
    # Setup market data
    valuation_date = date(2023, 1, 1)
    expiry_date = date(2024, 1, 1) # 1 year
    
    market_data = MarketData(
        valuation_date=valuation_date,
        spots={"AAPL": 100.0},
        rates={"AAPL": 0.05},
        volatilities={"AAPL": 0.2}
    )

    # Setup instrument
    put_option = EquityVanillaOption(
        asset_name="AAPL",
        strike=100.0,
        expiry_date=expiry_date,
        option_type=OptionType.PUT
    )

    # Setup engine
    engine = BlackScholesEngine(market_data)

    # Calculate price
    price = engine.price(put_option)
    
    print(f"Calculated Put Price: {price}")
    assert 5.50 < price < 5.60


if __name__ == "__main__":
    test_black_scholes_call()
    test_black_scholes_put()
