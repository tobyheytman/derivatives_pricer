from derivatives_pricer.engines.engine import PricingEngine
from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.instruments.equity import EquityVanillaOption
from derivatives_pricer.instruments.fx import FXVanillaOption
from derivatives_pricer.core.types import OptionType
from derivatives_pricer.math.analytics import black_scholes_price
from datetime import date

class BlackScholesEngine(PricingEngine):
    """
    Pricing Engine using the analytic Black-Scholes formula.
    Supports EquityVanillaOption and FXVanillaOption.
    """

    def price(self, instrument: Instrument) -> float:
        if not isinstance(instrument, (EquityVanillaOption, FXVanillaOption)):
            raise TypeError(f"BlackScholesEngine does not support {type(instrument).__name__}")
        
        # 1. Extract Data (Orchestration)
        if hasattr(instrument, 'asset_name'):
            ticker = instrument.asset_name
        elif hasattr(instrument, 'currency_pair'):
            ticker = instrument.currency_pair
        else:
            raise ValueError("Instrument must have asset_name or currency_pair")

        spot = self.market_data.get_spot(ticker)
        strike = instrument.strike
        
        # Calculate time to expiry
        valuation_date = self.market_data.valuation_date
        days_to_expiry = (instrument.expiry_date - valuation_date).days
        time_to_expiry = days_to_expiry / 365.0
        
        rate = self.market_data.get_rate(ticker)
        volatility = self.market_data.get_volatility(ticker)
        
        # Handle dividend/foreign rate
        dividend_yield = 0.0
        if isinstance(instrument, FXVanillaOption):
            dividend_yield = self.market_data.get_foreign_rate(ticker)
            
        is_call = (instrument.option_type == OptionType.CALL)

        # 2. Delegate Calculation (Logic)
        return black_scholes_price(
            spot=spot,
            strike=strike,
            time_to_expiry=time_to_expiry,
            risk_free_rate=rate,
            volatility=volatility,
            dividend_yield=dividend_yield,
            is_call=is_call
        )
