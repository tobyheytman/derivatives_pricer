import sys
import os
from datetime import date
import math

# Add project root to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from derivatives_pricer.core.types import OptionType, ExerciseStyle, BarrierType
from derivatives_pricer.core.market_data import MarketData
from derivatives_pricer.instruments.equity import EquityVanillaOption, EquityBarrierOption, EquityAsianOption
from derivatives_pricer.models.monte_carlo import MonteCarloModel
from derivatives_pricer.models.black_scholes import BlackScholesModel

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

    bs_model = BlackScholesModel()
    bs_price = bs_model.price(option, market_data)
    
    mc_model = MonteCarloModel(num_paths=50000, num_steps=100)
    mc_price = mc_model.price(option, market_data)
    
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

    # Barrier at 120. If price hits 120, option becomes worthless.
    # Strike 100. Spot 100.
    # This should be cheaper than vanilla call.
    option = EquityBarrierOption(
        asset_name="AAPL",
        strike=100.0,
        barrier=120.0,
        expiry_date=expiry_date,
        option_type=OptionType.CALL,
        barrier_type=BarrierType.UP_AND_OUT
    )

    mc_model = MonteCarloModel(num_paths=50000, num_steps=100)
    price = mc_model.price(option, market_data)
    
    bs_price = BlackScholesModel().price(
        EquityVanillaOption("AAPL", 100.0, expiry_date, OptionType.CALL),
        market_data
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

    # Asian option volatility is generally lower than vanilla, so price should be lower for ATM call.
    option = EquityAsianOption(
        asset_name="AAPL",
        strike=100.0,
        expiry_date=expiry_date,
        option_type=OptionType.CALL
    )

    mc_model = MonteCarloModel(num_paths=50000, num_steps=100)
    price = mc_model.price(option, market_data)
    
    bs_price = BlackScholesModel().price(
        EquityVanillaOption("AAPL", 100.0, expiry_date, OptionType.CALL),
        market_data
    )
    
    print(f"Vanilla Price: {bs_price:.4f}")
    print(f"Asian Price: {price:.4f}")
    
    assert price < bs_price
    print("Asian Test Passed")

if __name__ == "__main__":
    test_monte_carlo_vanilla_convergence()
    test_barrier_option_up_and_out()
    test_asian_option_average()
