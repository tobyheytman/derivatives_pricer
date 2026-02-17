import numpy as np

def vanilla_option_payoff(
    prices: np.ndarray,
    strike: float,
    is_call: bool
) -> np.ndarray:
    """
    Calculate payoff for vanilla options.
    prices: shape (num_paths,) or broadcastable.
    """
    if is_call:
        return np.maximum(prices - strike, 0.0)
    else:
        return np.maximum(strike - prices, 0.0)

def loop_barrier_payoff(
    paths: np.ndarray,
    strike: float,
    barrier: float,
    is_call: bool,
    barrier_type_name: str # string representation of BarrierType enum
) -> np.ndarray:
    """
    Calculate payoff for barrier options.
    paths: shape (num_steps, num_paths)
    """
    # final_prices = paths[-1]
    # max_prices = np.max(paths, axis=0)
    # min_prices = np.min(paths, axis=0)
    
    # Logic is clearer if we just pass the arrays needed, but paths needed for min/max
    final_prices = paths[-1]
    max_prices = np.max(paths, axis=0)
    min_prices = np.min(paths, axis=0)
    
    active = np.ones(paths.shape[1], dtype=bool)
    
    if barrier_type_name == "UP_AND_OUT":
        active = max_prices < barrier
    elif barrier_type_name == "DOWN_AND_OUT":
        active = min_prices > barrier
    elif barrier_type_name == "UP_AND_IN":
        active = max_prices >= barrier
    elif barrier_type_name == "DOWN_AND_IN":
        active = min_prices <= barrier
        
    raw_payoffs = vanilla_option_payoff(final_prices, strike, is_call)
    return np.where(active, raw_payoffs, 0.0)

def asian_option_payoff(
    paths: np.ndarray,
    strike: float,
    is_call: bool
) -> np.ndarray:
    """
    Calculate payoff for Asian options (Arithmetic average).
    paths: shape (num_steps, num_paths)
    """
    average_prices = np.mean(paths, axis=0)
    return vanilla_option_payoff(average_prices, strike, is_call)
