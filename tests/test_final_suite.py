import sys
import os
import unittest
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from derivatives_pricer.domain.market import MarketState
from derivatives_pricer.domain.enums import BarrierType
from derivatives_pricer.instruments.options import VanillaOption
from derivatives_pricer.instruments.exotics import ExoticOption
from derivatives_pricer.engines.binomial import BinomialPricingEngine
from derivatives_pricer.engines.analytic import BlackScholesEngine
from derivatives_pricer.engines.monte_carlo import MonteCarloEngine

class TestDerivativesPricer(unittest.TestCase):
    
    def setUp(self):
        # Standard Market
        self.market = MarketState(
            spot_price=100.0,
            risk_free_rate=0.05,
            volatility=0.20,
            dividend_yield=0.0
        )
        # Engines
        self.bs_engine = BlackScholesEngine()
        self.bin_engine = BinomialPricingEngine(step_count=500)
        self.mc_engine = MonteCarloEngine(num_paths=10000, num_steps=100)

    def test_vanilla_option_consistency(self):
        """Verify all engines agree on Vanilla European Call."""
        option = VanillaOption.european_call(strike=100.0, expiry=1.0)
        
        price_bs = self.bs_engine.price(option, self.market)
        price_bin = self.bin_engine.price(option, self.market)
        price_mc = self.mc_engine.price(option, self.market)
        
        print(f"\n[Vanilla Call] BS: {price_bs:.4f}, Bin: {price_bin:.4f}, MC: {price_mc:.4f}")
        
        self.assertAlmostEqual(price_bs, 10.4506, delta=0.001)
        self.assertAlmostEqual(price_bin, 10.4506, delta=0.1)
        self.assertAlmostEqual(price_mc, 10.4506, delta=0.2)

    def test_barrier_option(self):
        """Verify Barrier Option Pricing (Monte Carlo Only)."""
        # Up-and-out Call
        # Strike 100, Barrier 150.
        # If price hits 150, option dies.
        # Should be cheaper than vanilla.
        
        barrier_option = ExoticOption.barrier_up_out_call(strike=100.0, barrier=150.0, expiry=1.0)
        
        # BS Engine should fail or not be supported (Engine logic currently handles only Vanilla)
        # Actually BS engine checks isinstance(VanillaOption). ExoticOption is not VanillaOption.
        with self.assertRaises(TypeError):
            self.bs_engine.price(barrier_option, self.market)

        price_barrier = self.mc_engine.price(barrier_option, self.market)
        price_vanilla = self.mc_engine.price(
            VanillaOption.european_call(100.0, 1.0), 
            self.market
        )
        
        print(f"\n[Barrier Up-Out 150] Price: {price_barrier:.4f} vs Vanilla: {price_vanilla:.4f}")
        self.assertLess(price_barrier, price_vanilla)

    def test_asian_option(self):
        """Verify Asian Option Pricing (Monte Carlo Only)."""
        # Arithmetic Average Call
        # Volatility of average < Volatility of spot.
        # Price should be lower than Vanilla ATM.
        
        asian_option = ExoticOption.asian_call(strike=100.0, expiry=1.0)
        
        price_asian = self.mc_engine.price(asian_option, self.market)
        price_vanilla = self.mc_engine.price(
            VanillaOption.european_call(100.0, 1.0), 
            self.market
        )
        
        print(f"\n[Asian Call] Price: {price_asian:.4f} vs Vanilla: {price_vanilla:.4f}")
        self.assertLess(price_asian, price_vanilla)

    def test_fx_option(self):
        """Verify FX Option using Vanilla framework."""
        # EURUSD: S=1.10, K=1.10, r_dom=5%, r_for=3%, vol=10%
        # Foreign rate is handled via dividend_yield in MarketState.
        
        fx_market = MarketState(
            spot_price=1.10,
            risk_free_rate=0.05,
            volatility=0.10,
            dividend_yield=0.03 # Foreign Rate
        )
        
        # It's just a Vanilla Option on the currency pair
        fx_option = VanillaOption.european_call(strike=1.10, expiry=1.0)
        
        price = self.bs_engine.price(fx_option, fx_market)
        
        # Garman-Kohlhagen / BS result
        # d1 = (ln(1) + (0.05 - 0.03 + 0.005)) / 0.1 = 0.25
        # d2 = 0.15
        # N(d1) = 0.5987, N(d2) = 0.5596
        # Call = 1.1 * e^-0.03 * 0.5987 - 1.1 * e^-0.05 * 0.5596
        # Call = 1.1 * 0.9704 * 0.5987 - 1.1 * 0.9512 * 0.5596
        # Call = 0.639 - 0.585 = 0.054
        
        print(f"\n[FX Call] Price: {price:.4f}")
        self.assertAlmostEqual(price, 0.0536, delta=0.001)

if __name__ == '__main__':
    unittest.main()
