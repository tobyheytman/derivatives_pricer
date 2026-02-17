from datetime import date
from typing import Any

from derivatives_pricer.engines.engine import PricingEngine
from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.instruments.rates import InterestRateSwap
from derivatives_pricer.data.curves import YieldCurve, ConstantYieldCurve
from derivatives_pricer.core.types import YearFraction

class DiscountingEngine(PricingEngine):
    """
    Pricing Engine using Discounted Cash Flow (DCF).
    Supports InterestRateSwap.
    """

    def price(self, instrument: Instrument) -> float:
        if isinstance(instrument, InterestRateSwap):
            return self._price_options_swap(instrument)
        else:
            raise NotImplementedError(f"DiscountingEngine does not support {type(instrument).__name__}")

    def _price_options_swap(self, swap: InterestRateSwap) -> float:
        # 1. Extract Data
        # Assuming curve is available in market_data.curves under "USD" or default
        curve = self.market_data.get_curve("USD")
        
        if not curve:
            # Fallback to constant rate from rates dict if curve not found
            rate = self.market_data.get_rate("USD")
            curve = ConstantYieldCurve(rate)
            
        valuation_date = self.market_data.valuation_date
        
        # 2. Logic (DCF)
        # Determine payment dates
        current_date = swap.start_date
        payment_dates = []
        while current_date < swap.maturity_date:
            month = current_date.month - 1 + swap.frequency_months
            year = current_date.year + month // 12
            month = month % 12 + 1
            next_date = date(year, month, current_date.day)
            if next_date > swap.maturity_date:
                next_date = swap.maturity_date
            payment_dates.append(next_date)
            current_date = next_date
            
        # PV(Fixed Leg)
        pv_fixed = 0.0
        prev_date = swap.start_date
        
        for p_date in payment_dates:
            days = (p_date - prev_date).days
            year_frac = YearFraction(days / 365.0)
            df = curve.discount_factor(YearFraction((p_date - valuation_date).days / 365.0))
            
            coupon = swap.notional * swap.fixed_rate * year_frac
            pv_fixed += coupon * df
            
            prev_date = p_date
            
        # PV(Floating Leg)
        df_start = curve.discount_factor(YearFraction((swap.start_date - valuation_date).days / 365.0))
        df_end = curve.discount_factor(YearFraction((swap.maturity_date - valuation_date).days / 365.0))
        
        pv_float = swap.notional * (df_start - df_end)
        
        if swap.payer:
            return pv_float - pv_fixed
        else:
            return pv_fixed - pv_float
