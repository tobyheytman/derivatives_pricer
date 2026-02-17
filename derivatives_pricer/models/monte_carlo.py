import numpy as np
from typing import Any, List
from datetime import date

from derivatives_pricer.core.model import PricingModel
from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.core.types import OptionType, YearFraction, BarrierType
from derivatives_pricer.instruments.equity import EquityVanillaOption, EquityBarrierOption, EquityAsianOption


class MonteCarloModel(PricingModel):
    """Monte Carlo pricing model."""
    
    def __init__(self, num_paths: int = 10000, num_steps: int = 100):
        self.num_paths = num_paths
        self.num_steps = num_steps

    def price(self, instrument: Instrument, market_data: Any) -> float:
        # Generate paths
        spot = market_data.get_spot(instrument.asset_name)
        r = market_data.get_rate(instrument.asset_name)
        sigma = market_data.get_vol(instrument.asset_name)
        valuation_date = market_data.valuation_date
        
        T_days = (instrument.expiry_date - valuation_date).days
        T = T_days / 365.0
        
        dt = T / self.num_steps
        
        # S_t = S_0 * exp((r - 0.5*sigma^2)t + sigma*W_t)
        # Vectorized simulation
        
        # Shape: (num_steps, num_paths)
        Z = np.random.standard_normal((self.num_steps, self.num_paths))
        
        # Precompute drift and diffusion
        drift = (r - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt)
        
        # log_returns = drift + diffusion * Z
        log_returns = drift + diffusion * Z
        
        # Accumulate returns
        log_paths = np.cumsum(log_returns, axis=0) # Shape: (steps, paths)
        
        # S_paths = S_0 * exp(log_paths)
        S_paths = spot * np.exp(log_paths)
        
        # Add S_0 at start of paths for completeness (steps+1, paths)
        S_paths = np.vstack([np.full(self.num_paths, spot), S_paths])
        
        # Calculate payoff for each path
        payoffs = np.zeros(self.num_paths)
        
        if isinstance(instrument, EquityVanillaOption):
            S_T = S_paths[-1]
            if instrument.option_type == OptionType.CALL:
                payoffs = np.maximum(S_T - instrument.strike, 0.0)
            else:
                payoffs = np.maximum(instrument.strike - S_T, 0.0)
                
        elif isinstance(instrument, EquityAsianOption):
            # Arithmetic average of path
            S_avg = np.mean(S_paths, axis=0)
            if instrument.option_type == OptionType.CALL:
                payoffs = np.maximum(S_avg - instrument.strike, 0.0)
            else:
                payoffs = np.maximum(instrument.strike - S_avg, 0.0)
                
        elif isinstance(instrument, EquityBarrierOption):
            # Check barrier conditions
            S_T = S_paths[-1]
            barrier = instrument.barrier
            
            max_S = np.max(S_paths, axis=0)
            min_S = np.min(S_paths, axis=0)
            
            if instrument.barrier_type == BarrierType.UP_AND_OUT:
                active = max_S < barrier
            elif instrument.barrier_type == BarrierType.DOWN_AND_OUT:
                active = min_S > barrier
            elif instrument.barrier_type == BarrierType.UP_AND_IN:
                active = max_S >= barrier
            elif instrument.barrier_type == BarrierType.DOWN_AND_IN:
                active = min_S <= barrier
            else:
                active = np.ones(self.num_paths, dtype=bool) # Default active
            
            # Helper payoff func
            raw_payoff = 0.0
            if instrument.option_type == OptionType.CALL:
                raw_payoff = np.maximum(S_T - instrument.strike, 0.0)
            else:
                raw_payoff = np.maximum(instrument.strike - S_T, 0.0)
                
            payoffs = np.where(active, raw_payoff, 0.0)
            
        else:
            raise NotImplementedError(f"Instrument {type(instrument)} not supported by MonteCarloModel yet")
            
        # Discount back
        price = np.mean(payoffs) * np.exp(-r * T)
        return float(price)
