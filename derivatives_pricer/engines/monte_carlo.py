import numpy as np
from derivatives_pricer.engines.engine import PricingEngine
from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.instruments.equity import EquityVanillaOption, EquityBarrierOption, EquityAsianOption
from derivatives_pricer.core.types import OptionType, BarrierType
from derivatives_pricer.math.simulation import generate_geometric_brownian_motion_paths

class MonteCarloEngine(PricingEngine):
    """
    Pricing Engine using Monte Carlo simulation.
    """
    
    def __init__(self, market_data, num_paths: int = 10000, num_steps: int = 100):
        super().__init__(market_data)
        self.num_paths = num_paths
        self.num_steps = num_steps

    def price(self, instrument: Instrument) -> float:
        # 1. Extract Data
        ticker = instrument.asset_name # Assuming equity/asset based for now
        spot = self.market_data.get_spot(ticker)
        rate = self.market_data.get_rate(ticker)
        volatility = self.market_data.get_volatility(ticker)
        
        valuation_date = self.market_data.valuation_date
        days_to_expiry = (instrument.expiry_date - valuation_date).days
        time_to_expiry = days_to_expiry / 365.0
        
        if time_to_expiry <= 0:
            return instrument.payoff(self.market_data)
            
        # 2. Generate Paths (delegated to math)
        paths = generate_geometric_brownian_motion_paths(
            spot=spot,
            risk_free_rate=rate,
            volatility=volatility,
            time_to_expiry=time_to_expiry,
            num_steps=self.num_steps,
            num_paths=self.num_paths
        )
        
        # 3. Calculate Payoff (Delegated to math)
        from derivatives_pricer.math.payoffs import vanilla_option_payoff, loop_barrier_payoff, asian_option_payoff
        
        final_prices = paths[-1]
        is_call = (instrument.option_type == OptionType.CALL)
        
        if isinstance(instrument, EquityVanillaOption):
            payoffs = vanilla_option_payoff(final_prices, instrument.strike, is_call)
                
        elif isinstance(instrument, EquityAsianOption):
            payoffs = asian_option_payoff(paths, instrument.strike, is_call)

        elif isinstance(instrument, EquityBarrierOption):
            payoffs = loop_barrier_payoff(
                paths, 
                instrument.strike, 
                instrument.barrier, 
                is_call,
                instrument.barrier_type.name 
            )
            
        else:
             raise NotImplementedError(f"MonteCarloEngine does not support {type(instrument).__name__}")

             
        # 4. Discount
        discount_factor = np.exp(-rate * time_to_expiry)
        price = np.mean(payoffs) * discount_factor
        
        return float(price)
