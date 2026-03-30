import logging
from functools import wraps


def safe_slot(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error en {func.__name__}: {e}", exc_info=True)
            return None

    return wrapper
