"""Power 3 Signal, Trend Status, and Power Trend calculators.

Standalone signal calculation functions that can be used independently of
the yfinance adapter.  These mirror the inline logic in
``YfinanceAdapter.fetch_ma_data`` (plan.md section 2.4) but are factored out so
that:

* Tests can exercise them without network calls.
* Other modules (e.g. a future breadth pipeline) can reuse them.
* The adapter can delegate here instead of duplicating logic.

Signal hierarchy (Power 3):
    POWER_3  (green)  -- EMA8 > EMA21 > SMA50 > SMA200
    CAUTION  (yellow) -- EMA8 > EMA21, close > SMA200
    WARNING  (orange) -- close > SMA200
    RISK_OFF (red)    -- close <= SMA200
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Power 3 Signal
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_power_3_signal(
    ema8: float,
    ema21: float,
    sma50: float,
    sma200: float,
    close: float,
) -> Dict[str, str]:
    """Determine the Power 3 Signal for a single ticker.

    The Power 3 Signal is a layered moving-average regime indicator:

    * **POWER_3** (green): EMA8 > EMA21 > SMA50 > SMA200 -- full uptrend.
    * **CAUTION** (yellow): EMA8 > EMA21 and close > SMA200 -- weakening but
      still above the long-term trend.
    * **WARNING** (orange): close > SMA200 -- intermediate trend broken, but
      long-term support holds.
    * **RISK_OFF** (red): close <= SMA200 -- below all key supports.

    Parameters
    ----------
    ema8 : float
        8-period Exponential Moving Average.
    ema21 : float
        21-period Exponential Moving Average.
    sma50 : float
        50-period Simple Moving Average.
    sma200 : float
        200-period Simple Moving Average.
    close : float
        Most recent closing price.

    Returns
    -------
    dict
        ``{'signal': str, 'color': str}`` where *signal* is one of
        ``POWER_3``, ``CAUTION``, ``WARNING``, ``RISK_OFF`` and *color*
        is the corresponding display colour.
    """
    if ema8 > ema21 > sma50 > sma200:
        return {"signal": "POWER_3", "color": "green"}
    if ema8 > ema21 and close > sma200:
        return {"signal": "CAUTION", "color": "yellow"}
    if close > sma200:
        return {"signal": "WARNING", "color": "orange"}
    return {"signal": "RISK_OFF", "color": "red"}


# ═══════════════════════════════════════════════════════════════════════════════
# Power Trend (Oratnek-style)
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_power_trend(
    hist: pd.DataFrame,
    sma20: float,
    sma50: float,
    sma200: float,
) -> Dict[str, bool]:
    """Evaluate the five Oratnek Power Trend conditions.

    A "Power Trend" exists when *all five* checks are True, indicating a
    broad, orderly, multi-timeframe uptrend.

    The five checks are:

    1. **3d_gt_20sma** -- the last 3 daily closes all stayed above SMA20.
    2. **3d_gt_50sma** -- the last 3 daily closes all stayed above SMA50.
    3. **3d_gt_200sma** -- the last 3 daily closes all stayed above SMA200.
    4. **20sma_gt_50sma** -- SMA20 > SMA50 (short-term trend rising).
    5. **50sma_gt_200sma** -- SMA50 > SMA200 (golden cross in effect).

    Parameters
    ----------
    hist : pd.DataFrame
        OHLC DataFrame with at least a ``Close`` column and >= 3 rows.
    sma20 : float
        Current 20-period Simple Moving Average.
    sma50 : float
        Current 50-period Simple Moving Average.
    sma200 : float
        Current 200-period Simple Moving Average.

    Returns
    -------
    dict
        Five boolean keys matching the checks above, plus an aggregate
        ``'is_power_trend'`` that is True only when all five pass.
    """
    if hist.empty or len(hist) < 3:
        logger.warning("calculate_power_trend: insufficient history (%d rows)", len(hist))
        return {
            "3d_gt_20sma": False,
            "3d_gt_50sma": False,
            "3d_gt_200sma": False,
            "20sma_gt_50sma": False,
            "50sma_gt_200sma": False,
            "is_power_trend": False,
        }

    last_3_close_min = float(hist["Close"].iloc[-3:].min())

    checks = {
        "3d_gt_20sma": last_3_close_min > sma20,
        "3d_gt_50sma": last_3_close_min > sma50,
        "3d_gt_200sma": last_3_close_min > sma200,
        "20sma_gt_50sma": sma20 > sma50,
        "50sma_gt_200sma": sma50 > sma200,
    }
    checks["is_power_trend"] = all(checks.values())
    return checks


# ═══════════════════════════════════════════════════════════════════════════════
# Trend Status (Oratnek-style distance percentages)
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_trend_status(
    close: float,
    hist: pd.DataFrame,
    ema21: float,
    sma50: float,
    sma200: float,
) -> Dict[str, float]:
    """Compute percentage distances from key moving averages and the 52-week high.

    Positive values mean the close is *above* the reference; negative means
    *below*.  This is the Oratnek "Trend Status" panel that lets traders
    quickly see how extended (or compressed) a ticker is relative to its
    structural supports.

    Parameters
    ----------
    close : float
        Most recent closing price.
    hist : pd.DataFrame
        OHLC DataFrame with a ``Close`` column spanning at least 252 rows
        for a meaningful 52-week high.
    ema21 : float
        21-period Exponential Moving Average.
    sma50 : float
        50-period Simple Moving Average.
    sma200 : float
        200-period Simple Moving Average.

    Returns
    -------
    dict
        Keys: ``9ema_dist``, ``21ema_dist``, ``50sma_dist``,
        ``200sma_dist``, ``52w_high_dist`` -- each a rounded float
        representing percent distance.
    """
    if hist.empty or close == 0:
        return {
            "9ema_dist": 0.0,
            "21ema_dist": 0.0,
            "50sma_dist": 0.0,
            "200sma_dist": 0.0,
            "52w_high_dist": 0.0,
        }

    ema9 = float(hist["Close"].ewm(span=9, adjust=False).mean().iloc[-1])
    high_52w = float(hist["Close"].max())

    return {
        "9ema_dist": round((close - ema9) / close * 100, 2),
        "21ema_dist": round((close - ema21) / close * 100, 2),
        "50sma_dist": round((close - sma50) / close * 100, 2),
        "200sma_dist": round((close - sma200) / close * 100, 2),
        "52w_high_dist": round((close - high_52w) / high_52w * 100, 2),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Aggregate market signal from multiple tickers
# ═══════════════════════════════════════════════════════════════════════════════

# Signal priority for aggregation (lower index = more bullish).
_SIGNAL_PRIORITY: List[str] = ["POWER_3", "CAUTION", "WARNING", "RISK_OFF"]

# Display colours keyed by signal name.
_SIGNAL_COLORS: Dict[str, str] = {
    "POWER_3": "green",
    "CAUTION": "yellow",
    "WARNING": "orange",
    "RISK_OFF": "red",
}


def generate_all_signals(ticker_signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate Power 3 signals from multiple tickers into a market-wide view.

    The aggregate signal is the **weakest** (most bearish) signal across all
    tickers supplied.  This implements the conservative "weakest-link" approach
    -- if any major index is in RISK_OFF, the aggregate is RISK_OFF.

    Additionally the function counts how many tickers fall into each regime
    bucket to give a quick "breadth of strength" reading.

    Parameters
    ----------
    ticker_signals : dict
        Mapping of ticker symbol to its signal dict.  Each value must
        contain at least ``{'signal': str, 'color': str}`` as returned by
        :func:`calculate_power_3_signal`.

        Example::

            {
                'SPY': {'signal': 'POWER_3', 'color': 'green', ...},
                'QQQ': {'signal': 'CAUTION', 'color': 'yellow', ...},
                'IWM': {'signal': 'WARNING', 'color': 'orange', ...},
                'RSP': {'signal': 'POWER_3', 'color': 'green', ...},
            }

    Returns
    -------
    dict
        ``{
            'aggregate_signal': str,
            'aggregate_color': str,
            'signal_counts': {'POWER_3': N, 'CAUTION': N, ...},
            'total_tickers': int,
            'all_power_3': bool,
            'tickers': {<original ticker_signals dict>},
        }``
    """
    if not ticker_signals:
        logger.warning("generate_all_signals called with empty ticker_signals")
        return {
            "aggregate_signal": "RISK_OFF",
            "aggregate_color": "red",
            "signal_counts": {s: 0 for s in _SIGNAL_PRIORITY},
            "total_tickers": 0,
            "all_power_3": False,
            "tickers": {},
        }

    # Count occurrences of each signal level.
    signal_counts: Dict[str, int] = {s: 0 for s in _SIGNAL_PRIORITY}
    worst_priority = 0  # index into _SIGNAL_PRIORITY; higher = more bearish

    for ticker, sig_data in ticker_signals.items():
        sig_name = sig_data.get("signal", "RISK_OFF")
        if sig_name in signal_counts:
            signal_counts[sig_name] += 1
        else:
            logger.warning("Unknown signal '%s' for ticker %s, treating as RISK_OFF", sig_name, ticker)
            signal_counts["RISK_OFF"] += 1
            sig_name = "RISK_OFF"

        idx = _SIGNAL_PRIORITY.index(sig_name) if sig_name in _SIGNAL_PRIORITY else len(_SIGNAL_PRIORITY) - 1
        worst_priority = max(worst_priority, idx)

    aggregate_signal = _SIGNAL_PRIORITY[worst_priority]
    all_power_3 = signal_counts.get("POWER_3", 0) == len(ticker_signals)

    return {
        "aggregate_signal": aggregate_signal,
        "aggregate_color": _SIGNAL_COLORS[aggregate_signal],
        "signal_counts": signal_counts,
        "total_tickers": len(ticker_signals),
        "all_power_3": all_power_3,
        "tickers": ticker_signals,
    }
