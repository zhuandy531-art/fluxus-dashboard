"""
Shared helpers for data adapters: retry decorator, parsers, validators.
Per plan.md §2.2.
"""
import time
import functools
import logging

logger = logging.getLogger(__name__)


def retry(max_retries: int = 3, backoff_base: float = 2.0, exceptions: tuple = (Exception,)):
    """Exponential backoff retry decorator.

    Usage:
        @retry(max_retries=3, backoff_base=2.0)
        def fetch_data():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    wait = backoff_base ** attempt
                    logger.warning(
                        f"{func.__name__} attempt {attempt+1}/{max_retries} failed: {e}. "
                        f"Retrying in {wait:.1f}s..."
                    )
                    time.sleep(wait)
            raise last_exc
        return wrapper
    return decorator


def parse_pct_string(val) -> float | None:
    """Parse percentage strings like '3.50%' -> 0.035, '-1.20%' -> -0.012."""
    if val is None or val == '' or val == '-':
        return None
    try:
        s = str(val).strip().rstrip('%')
        return float(s) / 100.0
    except (ValueError, TypeError):
        return None


def parse_market_cap(val) -> float:
    """Parse market cap strings: '1.5B' -> 1_500_000_000, '250M' -> 250_000_000."""
    if val is None:
        return 0.0
    s = str(val).strip().upper()
    try:
        if 'T' in s:
            return float(s.replace('T', '')) * 1e12
        if 'B' in s:
            return float(s.replace('B', '')) * 1e9
        if 'M' in s:
            return float(s.replace('M', '')) * 1e6
        if 'K' in s:
            return float(s.replace('K', '')) * 1e3
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def parse_numeric(val) -> float | None:
    """Safely parse a numeric value, returning None on failure."""
    if val is None or val == '' or val == '-':
        return None
    try:
        return float(str(val).strip().replace(',', ''))
    except (ValueError, TypeError):
        return None
