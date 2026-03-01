"""ATR Extension Enrichment Layer.

Not a standalone screener — this module adds ``atr_ext`` (ATR extension
from the 50-day SMA) and ``atr_color`` (green / amber / red) fields to
any list of ticker dicts.  It is designed to be called *after* each
screener produces its results so that every ticker badge on the
dashboard carries a visual heat indicator.

ATR Extension = abs(sma50_dist) / (atr / close)

    - **green**  (atr_ext <= 4):  Near the mean — entry zone.
    - **amber**  (atr_ext <= 6):  Stretched — caution.
    - **red**    (atr_ext >  6):  Over-extended — avoid new entries.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

# ── Color thresholds ─────────────────────────────────────────────────
_GREEN_MAX = 4.0
_AMBER_MAX = 6.0


def _classify_color(atr_ext: float | None) -> str:
    """Map an ATR extension value to a traffic-light color."""
    if atr_ext is None:
        return "amber"  # default when data is unavailable
    if atr_ext <= _GREEN_MAX:
        return "green"
    if atr_ext <= _AMBER_MAX:
        return "amber"
    return "red"


def enrich_with_atr(
    tickers: List[Dict[str, Any]],
    universe: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """Add ``atr_ext`` and ``atr_color`` to each ticker dict.

    Parameters
    ----------
    tickers : list[dict]
        List of ticker dicts (must contain at least a ``'ticker'`` key).
    universe : pd.DataFrame
        Finviz-sourced universe with at least ``ticker``, ``atr``,
        ``close``, and ``sma50_dist`` columns.

    Returns
    -------
    list[dict]
        The same list, with ``atr_ext`` (float | None) and
        ``atr_color`` (str) added to each entry.
    """
    if universe.empty or not tickers:
        logger.debug("enrich_with_atr: nothing to enrich")
        return tickers

    # Build a lookup keyed by ticker for fast access
    required_cols = {"ticker", "atr", "close", "sma50_dist"}
    if not required_cols.issubset(universe.columns):
        missing = required_cols - set(universe.columns)
        logger.warning(
            "enrich_with_atr: universe missing columns %s — skipping", missing
        )
        for entry in tickers:
            entry.setdefault("atr_ext", None)
            entry.setdefault("atr_color", "amber")
        return tickers

    lookup: Dict[str, Dict[str, Any]] = {}
    for _, row in universe.iterrows():
        lookup[row["ticker"]] = {
            "atr": row.get("atr"),
            "close": row.get("close"),
            "sma50_dist": row.get("sma50_dist"),
        }

    enriched_count = 0
    for entry in tickers:
        symbol = entry.get("ticker")
        info = lookup.get(symbol)

        if info is None:
            entry["atr_ext"] = None
            entry["atr_color"] = "amber"
            continue

        atr = info["atr"]
        close = info["close"]
        sma50_dist = info["sma50_dist"]

        # Calculate ATR extension: how many ATRs away from SMA50
        if (
            atr is not None
            and close is not None
            and sma50_dist is not None
            and not pd.isna(atr)
            and not pd.isna(close)
            and not pd.isna(sma50_dist)
            and atr > 0
            and close > 0
        ):
            atr_pct = atr / close  # ATR as fraction of price
            atr_ext = abs(sma50_dist) / atr_pct
            entry["atr_ext"] = round(atr_ext, 2)
            enriched_count += 1
        else:
            entry["atr_ext"] = None

        entry["atr_color"] = _classify_color(entry["atr_ext"])

    logger.info(
        "enrich_with_atr: enriched %d / %d tickers", enriched_count, len(tickers)
    )

    return tickers
