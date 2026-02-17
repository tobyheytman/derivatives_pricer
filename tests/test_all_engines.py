import sys
import os
import unittest
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from derivatives_pricer.domain.market import MarketState
from derivatives_pricer.instruments.options import VanillaOption
from derivatives_pricer.engines.binomial import BinomialPricingEngine
from derivatives_pricer.engines.analytic import BlackScholesEngine
from derivatives_pricer.engines.monte_carlo import MonteCarloEngine

class TestAllEngines(unittest.TestCase):
    
    def setUp(self):
        # Standard Test Case: ATM Call, 1 Year Expiry
        # Haug, Espen Gaarder. "The Complete Guide to Option Pricing Formulas".
        self.market = MarketState(
            spot_price=100.0,
            risk_free_rate=0.05,
            volatility=0.20,
            dividend_yield=0.0
        )
        self.option = VanillaOption.european_call(strike=100.0, expiry=1.0)
        
        # Approximate BS Price: 10.4506

    def test_analytic_benchmarks(self):
        """Verify Black-Scholes Engine is exact."""
        engine = BlackScholesEngine()
        price = engine.price(self.option, self.market)
        print(f"BS Analytic Price: {price:.4f}")
        self.assertAlmostEqual(price, 10.4506, delta=0.0001)

    def test_binomial_convergence(self):
        """Verify Binomial Tree converges to BS."""
        # CRR with N=1000 should be very close
        engine = BinomialPricingEngine(step_count=1000)
        price = engine.price(self.option, self.market)
        print(f"Binomial Price (N=1000): {price:.4f}")
        self.assertAlmostEqual(price, 10.4506, delta=0.01)

    def test_monte_carlo_convergence(self):
        """Verify Monte Carlo converges to BS."""
        # MC with N=50,000 paths
        # Set seed for reproducibility
        np.random.seed(42)
        engine = MonteCarloEngine(num_paths=50000, num_steps=100)
        price = engine.price(self.option, self.market)
        print(f"Monte Carlo Price (N=50k): {price:.4f}")
        self.assertAlmostEqual(price, 10.4506, delta=0.10) # 10 cents tolerance for MC

if __name__ == '__main__':
    unittest.main()
