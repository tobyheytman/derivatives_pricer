from functools import wraps
from typing import Callable, Any, TypeVar

F = TypeVar('F', bound=Callable[..., Any])

def validate_positive(param_name: str) -> Callable[[F], F]:
    """
    Decorator to ensure a specific parameter is positive > 0.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Map args to names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            val = bound_args.arguments.get(param_name)
            if val is not None and isinstance(val, (int, float)) and val <= 0:
                raise ValueError(f"Parameter '{param_name}' must be positive, got {val}")
            
            return func(*args, **kwargs)
        return wrapper # type: ignore
    return decorator

def validate_probability(param_name: str) -> Callable[[F], F]:
    """
    Ensure parameter is between 0 and 1.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            val = bound_args.arguments.get(param_name)
            if val is not None and isinstance(val, (int, float)) and not (0 <= val <= 1):
                raise ValueError(f"Parameter '{param_name}' must be a probability [0,1], got {val}")
            
            return func(*args, **kwargs)
        return wrapper # type: ignore
    return decorator
