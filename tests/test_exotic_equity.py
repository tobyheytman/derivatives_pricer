import sys
import os
from datetime import date
import math

# Add project root to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from derivatives_pricer.core.types import OptionType, ExerciseStyle, BarrierType
from derivatives_pricer.core.market_data import MarketData
from derivatives_pricer.instruments.equity import EquityVanillaOption, EquityBarrierOption, EquityAsianOption
from derivatives_pricer.engines.monte_carlo import MonteCarloEngine
from derivatives_pricer.engines.black_scholes import BlackScholesEngine

def test_monte_carlo_vanilla_convergence():
    """Verify MC converges to BS for vanilla options."""
    print("\nRunning Vanilla Convergence Test...")
    valuation_date = date(2023, 1, 1)
    expiry_date = date(2024, 1, 1)
    
    market_data = MarketData(
        valuation_date=valuation_date,
        spots={"AAPL": 100.0},
        rates={"AAPL": 0.05},
        volatilities={"AAPL": 0.2}
    )

    option = EquityVanillaOption(
        asset_name="AAPL",
        strike=100.0,
        expiry_date=expiry_date,
        option_type=OptionType.CALL
    )

    bs_engine = BlackScholesEngine(market_data)
    bs_price = bs_engine.price(option)
    
    mc_engine = MonteCarloEngine(market_data, num_paths=50000, num_steps=100)
    mc_price = mc_engine.price(option)
    
    print(f"BS Price: {bs_price:.4f}")
    print(f"MC Price: {mc_price:.4f}")
    
    # 1% tolerance
    assert abs(bs_price - mc_price) / bs_price < 0.02
    print("Vanilla Convergence Passed")

def test_barrier_option_up_and_out():
    """Test Up-and-Out Call."""
    print("\nRunning Barrier Up-and-Out Test...")
    valuation_date = date(2023, 1, 1)
    expiry_date = date(2024, 1, 1)
    
    market_data = MarketData(
        valuation_date=valuation_date,
        spots={"AAPL": 100.0},
        rates={"AAPL": 0.05},
        volatilities={"AAPL": 0.2}
    )

    option = EquityBarrierOption(
        asset_name="AAPL",
        strike=100.0,
        barrier=120.0,
        expiry_date=expiry_date,
        option_type=OptionType.CALL,
        barrier_type=BarrierType.UP_AND_OUT
    )

    mc_engine = MonteCarloEngine(market_data, num_paths=50000, num_steps=100)
    price = mc_engine.price(option)
    
    bs_engine = BlackScholesEngine(market_data)
    bs_price = bs_engine.price(
        EquityVanillaOption("AAPL", 100.0, expiry_date, OptionType.CALL)
    )
    
    print(f"Vanilla Price: {bs_price:.4f}")
    print(f"Barrier Price: {price:.4f}")
    
    assert price < bs_price
    assert price > 0.0
    print("Barrier Test Passed")

def test_asian_option_average():
    """Test Asian Option (Arithmetic Average)."""
    print("\nRunning Asian Option Test...")
    valuation_date = date(2023, 1, 1)
    expiry_date = date(2024, 1, 1)
    
    market_data = MarketData(
        valuation_date=valuation_date,
        spots={"AAPL": 100.0},
        rates={"AAPL": 0.05},
        volatilities={"AAPL": 0.2}
    )

    option = EquityAsianOption(
        asset_name="AAPL",
        strike=100.0,
        expiry_date=expiry_date,
        option_type=OptionType.CALL
    )

    mc_engine = MonteCarloEngine(market_data, num_paths=50000, num_steps=100)
    price = mc_engine.price(option)
    
    bs_engine = BlackScholesEngine(market_data)
    bs_price = bs_engine.price(
        EquityVanillaOption("AAPL", 100.0, expiry_date, OptionType.CALL)
    )
    
    print(f"Vanilla Price: {bs_price:.4f}")
    print(f"Asian Price: {price:.4f}")
    
    assert price < bs_price
    print("Asian Test Passed")


if __name__ == "__main__":
    test_monte_carlo_vanilla_convergence()
    test_barrier_option_up_and_out()
    test_asian_option_average()
