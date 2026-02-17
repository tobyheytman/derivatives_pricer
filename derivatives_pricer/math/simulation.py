import numpy as np

def generate_geometric_brownian_motion_paths(
    spot: float,
    risk_free_rate: float,
    volatility: float,
    time_to_expiry: float,
    num_steps: int,
    num_paths: int,
    dividend_yield: float = 0.0
) -> np.ndarray:
    """
    Generate paths using Geometric Brownian Motion.
    
    Returns:
        np.ndarray: Array of shape (num_steps + 1, num_paths) containing asset prices.
    """
    dt = time_to_expiry / num_steps
    
    # Drift and diffusion terms
    drift = (risk_free_rate - dividend_yield - 0.5 * volatility**2) * dt
    diffusion = volatility * np.sqrt(dt)
    
    # Generate random shocks
    Z = np.random.standard_normal((num_steps, num_paths))
    
    # Calculate log returns
    log_returns = drift + diffusion * Z
    
    # Accumulate log returns to get log prices
    log_paths = np.vstack([np.zeros(num_paths), np.cumsum(log_returns, axis=0)])
    
    # Convert back to prices
    paths = spot * np.exp(log_paths)
    
    return paths
