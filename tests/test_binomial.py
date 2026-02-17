import sys
import os
import unittest
from datetime import date

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from derivatives_pricer.domain.enums import OptionType, ExerciseStyle
from derivatives_pricer.domain.market import MarketState
from derivatives_pricer.instruments.options import VanillaOption
from derivatives_pricer.engines.binomial import BinomialPricingEngine

class TestBinomialPricing(unittest.TestCase):
    
    def setUp(self):
        # Market State: S=100, r=5%, sigma=20%, q=0%
        self.market = MarketState(
            spot_price=100.0,
            risk_free_rate=0.05,
            volatility=0.20,
            dividend_yield=0.0
        )
        self.engine = BinomialPricingEngine(step_count=500)

    def test_european_call_convergence(self):
        """
        Verify European Call matches Black-Scholes approx.
        BS Value for S=100, K=100, T=1, r=0.05, sigma=0.2 is ~10.4506
        """
        option = VanillaOption.european_call(strike=100.0, expiry=1.0)
        price = self.engine.price(option, self.market)
        
        print(f"European Call Price (Binomial): {price:.4f}")
        self.assertAlmostEqual(price, 10.4506, delta=0.05)

    def test_american_put_early_exercise(self):
        """
        Verify American Put is worth more than European Put due to early exercise.
        Parameter set where early exercise is optimal:
        S=100, K=100, r=10% (high rates favor early exercise of puts), sigma=0.2, T=1
        """
        high_rate_market = MarketState(100.0, 0.10, 0.20, 0.0)
        
        euro_put = VanillaOption.european_put(100.0, 1.0)
        amer_put = VanillaOption.american_put(100.0, 1.0)
        
        euro_price = self.engine.price(euro_put, high_rate_market)
        amer_price = self.engine.price(amer_put, high_rate_market)
        
        print(f"European Put (r=10%): {euro_price:.4f}")
        print(f"American Put (r=10%): {amer_price:.4f}")
        
        self.assertGreater(amer_price, euro_price)

if __name__ == '__main__':
    unittest.main()
