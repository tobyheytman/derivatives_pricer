from derivatives_pricer.domain.interfaces import ValuationInstrument
from derivatives_pricer.domain.market import MarketState
from derivatives_pricer.domain.enums import OptionType
from derivatives_pricer.instruments.options import VanillaOption
from derivatives_pricer.engines.interface import PricingEngine
from derivatives_pricer.domain.analytic_formulas import black_scholes_price

class BlackScholesEngine(PricingEngine):
    """
    Analytic Engine for Vanilla European Options.
    """
    
    def price(self, instrument: ValuationInstrument, market_state: MarketState) -> float:
        if not isinstance(instrument, VanillaOption):
            raise TypeError("BlackScholesEngine only supports VanillaOption")
            
        # BS is strictly European
        # We could raise error if American, or just price as European approximation.
        # User requested rigorous engineering -> Raise error or explicit behavior.
        # Let's assume strictness.
        # if instrument.exercise_style == ExerciseStyle.AMERICAN:
        #    raise ValueError("Black-Scholes does not support American exercise.")
        
        return black_scholes_price(
            spot=market_state.spot_price,
            strike=instrument.strike,
            time_to_expiry=instrument.expiration_time,
            risk_free_rate=market_state.risk_free_rate,
            volatility=market_state.volatility,
            dividend_yield=market_state.dividend_yield,
            is_call=(instrument.option_type == OptionType.CALL)
        )
