import numpy as np
from typing import Any
from datetime import date

from derivatives_pricer.core.model import PricingModel
from derivatives_pricer.core.instrument import Instrument
from derivatives_pricer.core.types import YearFraction
from derivatives_pricer.instruments.rates import InterestRateSwap
from derivatives_pricer.data.curves import YieldCurve, ConstantYieldCurve

class DCFPricer(PricingModel):
    """Discounted Cash Flow pricer for linear rate instruments."""

    def price(self, instrument: Instrument, market_data: Any) -> float:
        if isinstance(instrument, InterestRateSwap):
            return self._price_swap(instrument, market_data)
        else:
            raise NotImplementedError(f"DCFPricer does not support {type(instrument)}")

    def _price_swap(self, swap: InterestRateSwap, market_data: Any) -> float:
        # Get curve
        # Assuming curve is available in market_data.curves under some key, e.g. "USD"
        # Or just use the first curve found for simplicity in this demo
        curve = None
        if hasattr(market_data, 'curves') and market_data.curves:
            curve = list(market_data.curves.values())[0] # Very naive!
        
        if not curve or not isinstance(curve, YieldCurve):
            # Fallback to constant rate from rates dict
            rate = market_data.get_rate("USD") # Default USD
            curve = ConstantYieldCurve(rate)

        valuation_date = getattr(market_data, 'valuation_date', date.today())
        
        # Determine payment dates
        # Simplified: generate dates every 'frequency' months
        current_date = swap.start_date
        payment_dates = []
        while current_date < swap.maturity_date:
            # Add frequency months
            month = current_date.month - 1 + swap.frequency_months
            year = current_date.year + month // 12
            month = month % 12 + 1
            next_date = date(year, month, current_date.day) # Simplified day rolling
            if next_date > swap.maturity_date:
                next_date = swap.maturity_date
            payment_dates.append(next_date)
            current_date = next_date
            
        # Calculate PV(Fixed Leg)
        pv_fixed = 0.0
        prev_date = swap.start_date
        years = []
        
        for p_date in payment_dates:
            days = (p_date - prev_date).days
            year_frac = YearFraction(days / 365.0)
            df = curve.discount_factor(YearFraction((p_date - valuation_date).days / 365.0))
            
            # Coupon payment
            coupon = swap.notional * swap.fixed_rate * year_frac
            pv_fixed += coupon * df
            
            prev_date = p_date
            
        # PV(Floating Leg)
        # For a standard swap at inception, PV(Float) = Notional (if curve used for forecasting and discounting is same)
        # But generally: PV_float = Sum(L_i * dt * df_i) + Notional * df_T (if exchange of principal)
        # Swaps usually don't exchange principal.
        # However, a floating leg can be decomposed into: Notional * (df_start - df_end)
        # Or more simply: Value = Notional (at start) - Notional * df_end (at end) ??
        # Wait, standard result: PV_float = Notional * (df(start) - df(end)) is wrong.
        # PV_float (paying Libor) = Notional * (1 - df(T)) ?? No.
        
        # Let's use the property: PV_float_leg (with notional at end) = Notional * df(start)
        # Since swap has no principal exchange, we must subtract Notional * df(end).
        # So PV_float_leg_only_coupons = Notional * (df(start) - df(end))
        
        df_start = curve.discount_factor(YearFraction((swap.start_date - valuation_date).days / 365.0))
        df_end = curve.discount_factor(YearFraction((swap.maturity_date - valuation_date).days / 365.0))
        
        pv_float = swap.notional * (df_start - df_end)
        
        if swap.payer: # Paying fixed, receiving float
            return pv_float - pv_fixed
        else: # Receiving fixed, paying float
            return pv_fixed - pv_float
