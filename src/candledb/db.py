"""
PatternDB — the main pattern database and detection engine.

Usage:
    from candledb import PatternDB
    import pandas as pd

    pdb = PatternDB()
    df = pd.DataFrame(...)  # OHLCV data with columns: open, high, low, close, volume

    results = pdb.detect(df, lookback=100)
"""

from typing import Optional

import pandas as pd
import numpy as np

from candledb.loader import load_patterns


class PatternDB:
    """Main pattern database — loads patterns and detects them in OHLCV data."""

    def __init__(self, patterns_dir: Optional[str] = None):
        self.patterns = load_patterns(patterns_dir)
        self._index = {p["id"]: p for p in self.patterns}

    def list_patterns(self, category: Optional[str] = None) -> list[str]:
        """List all pattern IDs, optionally filtered by category."""
        if category:
            return [p["id"] for p in self.patterns if p.get("category") == category]
        return [p["id"] for p in self.patterns]

    def get_pattern(self, pattern_id: str) -> Optional[dict]:
        """Get a single pattern definition by ID."""
        return self._index.get(pattern_id)

    def detect(
        self,
        df: pd.DataFrame,
        pattern: Optional[str] = None,
        category: Optional[str] = None,
        lookback: int = 100,
    ) -> list[dict]:
        """
        Detect candlestick patterns in OHLCV data.

        Args:
            df: DataFrame with columns: open, high, low, close, volume
            pattern: Specific pattern ID to detect. If None, detect all.
            category: Filter by category (bullish, bearish, neutral).
            lookback: Number of recent candles to scan.

        Returns:
            List of detections: [{"pattern": id, "index": i, "confidence": float}, ...]
        """
        # Slice to lookback window
        if lookback and len(df) > lookback:
            df = df.iloc[-lookback:]

        # Select patterns to run
        if pattern:
            patterns_to_check = [self._index[pattern]] if pattern in self._index else []
        elif category:
            patterns_to_check = [p for p in self.patterns if p.get("category") == category]
        else:
            patterns_to_check = self.patterns

        results = []
        for p in patterns_to_check:
            detections = self._detect_pattern(df, p)
            results.extend(detections)

        # Sort by index
        results.sort(key=lambda x: x["index"])
        return results

    def _detect_pattern(self, df: pd.DataFrame, pattern: dict) -> list[dict]:
        """Detect a single pattern in the dataframe."""
        pid = pattern["id"]
        structure = pattern.get("structure", {})
        num_candles = structure.get("candles", 1)
        requirements = structure.get("requirements", [])

        if len(df) < num_candles:
            return []

        detections = []
        params = pattern.get("parameters", {})

        for i in range(len(df) - num_candles + 1):
            window = df.iloc[i : i + num_candles]

            # Check each candle requirement
            match = True
            confidence_factors = []

            for req in requirements:
                candle_req = req.get("candle", {})
                idx = candle_req.get("index", 0)

                if idx >= len(window):
                    match = False
                    break

                row = window.iloc[idx]
                candle_ok, factor = self._check_candle(row, candle_req, window, params, df)
                confidence_factors.append(factor)
                if not candle_ok:
                    match = False
                    break

            # Check prior trend context
            context = pattern.get("context", {})
            prior_trend = context.get("prior_trend", {})
            if prior_trend.get("required", False) and match:
                trend_ok = self._check_prior_trend(
                    df, i, prior_trend, num_candles
                )
                if not trend_ok:
                    match = False
                confidence_factors.append(1.0 if trend_ok else 0.0)

            if match:
                confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
                detections.append(
                    {
                        "pattern": pid,
                        "name": pattern.get("name", pid),
                        "category": pattern.get("category", ""),
                        "index": df.index[i] if hasattr(df.index, "__getitem__") else i,
                        "row": i,
                        "confidence": round(confidence, 3),
                        "signal": pattern.get("signal", {}),
                    }
                )

        return detections

    def _check_candle(
        self,
        row: pd.Series,
        req: dict,
        window: pd.DataFrame,
        params: dict,
        full_df: pd.DataFrame,
    ) -> tuple[bool, float]:
        """Check if a single candle matches its requirements. Returns (match, confidence_factor)."""
        o = float(row.get("open", 0))
        h = float(row.get("high", 0))
        l = float(row.get("low", 0))
        c = float(row.get("close", 0))

        body = abs(c - o)
        rng = h - l if h - l > 0 else 1e-10
        body_ratio = body / rng

        # Upper and lower shadow
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l

        factors = []
        match = True

        # Color check
        color = req.get("color", "any")
        if color == "bullish" and c <= o:
            match = False
        elif color == "bearish" and c >= o:
            match = False
        if color != "any":
            factors.append(1.0 if match else 0.0)

        # Body size check
        body_size = req.get("body_size", "any")
        max_ratio = params.get("max_body_ratio", 0.30)
        large_ratio = params.get("large_body_ratio", 0.60)

        if body_size == "small" and body_ratio > max_ratio:
            match = False
        elif body_size == "large" and body_ratio < large_ratio:
            match = False
        elif body_size == "medium" and (body_ratio < max_ratio or body_ratio > large_ratio):
            match = False
        if body_size != "any":
            factors.append(1.0 if match else 0.0)

        # Doji check
        if req.get("doji", False):
            min_body = params.get("min_body_ratio", 0.0)
            if body_ratio > max(params.get("max_body_ratio", 0.05), min_body):
                match = False
            factors.append(1.0 if match else 0.0)

        # Shadow checks
        shadow_ratio = params.get("shadow_ratio", 2.0)

        upper_shadow_req = req.get("upper_shadow", "any")
        if upper_shadow_req == "long":
            if upper_shadow < body * shadow_ratio or body == 0:
                match = False
                factors.append(0.0)
            else:
                factors.append(1.0)
        elif upper_shadow_req == "short":
            if upper_shadow > body * 0.5:
                match = False
                factors.append(0.0)
            else:
                factors.append(1.0)

        lower_shadow_req = req.get("lower_shadow", "any")
        if lower_shadow_req == "long":
            if lower_shadow < body * shadow_ratio or body == 0:
                match = False
                factors.append(0.0)
            else:
                factors.append(1.0)
        elif lower_shadow_req == "short":
            if lower_shadow > body * 0.5:
                match = False
                factors.append(0.0)
            else:
                factors.append(1.0)

        # Gap checks (compared to previous candle in the window)
        idx = req.get("index", 0)
        if idx > 0:
            prev_row = window.iloc[idx - 1]
            prev_close = float(prev_row.get("close", 0))

            if req.get("gap_up", False) and o <= prev_close:
                match = False
                factors.append(0.0)
            elif req.get("gap_down", False) and o >= prev_close:
                match = False
                factors.append(0.0)
            else:
                if req.get("gap_up") or req.get("gap_down"):
                    factors.append(1.0)

        # Close into candle 0 check (candle closes into the body of the first candle)
        if req.get("close_into_candle_0", False) and idx > 0:
            candle0 = window.iloc[0]
            c0_open = float(candle0.get("open", 0))
            c0_close = float(candle0.get("close", 0))
            c0_high = max(c0_open, c0_close)
            c0_low = min(c0_open, c0_close)

            if not (c0_low <= c <= c0_high):
                match = False
                factors.append(0.0)
            else:
                # How far into the body = higher confidence
                penetration = (c - c0_low) / (c0_high - c0_low) if c0_high != c0_low else 0.5
                factors.append(max(0.5, penetration))

        confidence = sum(factors) / len(factors) if factors else 0.8
        return match, confidence

    def _check_prior_trend(
        self, df: pd.DataFrame, pattern_start: int, trend_req: dict, num_candles: int
    ) -> bool:
        """Check if there's a prior trend before the pattern."""
        direction = trend_req.get("direction", "any")
        min_lookback = trend_req.get("min_lookback", 3)

        if pattern_start < min_lookback:
            return False

        # Look at candles before the pattern
        lookback_start = max(0, pattern_start - min_lookback)
        prior = df.iloc[lookback_start:pattern_start]

        if len(prior) < min_lookback:
            return False

        # Simple trend detection: check if closes are trending
        closes = prior["close"].values
        if len(closes) < 2:
            return False

        # Linear regression slope
        x = np.arange(len(closes))
        slope = np.polyfit(x, closes, 1)[0]

        # Normalize slope relative to price
        avg_price = np.mean(closes)
        norm_slope = slope / avg_price if avg_price > 0 else 0

        if direction == "uptrend":
            return norm_slope > 0.001
        elif direction == "downtrend":
            return norm_slope < -0.001
        else:
            return True

    def to_json(self, results: list[dict]) -> str:
        """Export detection results as JSON string."""
        import json
        return json.dumps(results, indent=2, default=str)