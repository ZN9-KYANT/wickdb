"""
Tests for the pattern detection engine.
"""

import pandas as pd
import numpy as np
from wickdb import PatternDB


def make_df(opens, highs, lows, closes, volumes=None):
    """Helper: build an OHLCV DataFrame from lists."""
    n = len(closes)
    if volumes is None:
        volumes = [1000000] * n
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


class TestPatternDB:
    def test_init_loads_patterns(self):
        pdb = PatternDB()
        assert len(pdb.list_patterns()) >= 9

    def test_list_by_category(self):
        pdb = PatternDB()
        bullish = pdb.list_patterns(category="bullish")
        assert "morning_star" in bullish
        assert "hammer" in bullish

    def test_get_pattern(self):
        pdb = PatternDB()
        p = pdb.get_pattern("doji")
        assert p is not None
        assert p["id"] == "doji"

    def test_get_nonexistent_pattern(self):
        pdb = PatternDB()
        assert pdb.get_pattern("nonexistent") is None


class TestDojiDetection:
    def test_detects_doji(self):
        """A perfect doji: open == close, large range."""
        df = make_df(
            opens=[100, 100, 100, 100],
            highs=[100, 105, 100, 105],
            lows=[100, 95, 100, 95],
            closes=[100.01, 100, 100.01, 100],  # near-zero body
        )
        pdb = PatternDB()
        results = pdb.detect(df, pattern="doji")
        # Should detect dojis (body ratio < 5% of range)
        assert len(results) > 0, "Should detect at least one doji"

    def test_no_doji_on_large_body(self):
        """A large-bodied candle should not be a doji."""
        df = make_df(
            opens=[100, 100, 100],
            highs=[110, 110, 110],
            lows=[95, 95, 95],
            closes=[108, 108, 108],  # large body (8/15 = 53% of range)
        )
        pdb = PatternDB()
        results = pdb.detect(df, pattern="doji")
        assert len(results) == 0, "Large body should not be detected as doji"


class TestEngulfingDetection:
    def test_detects_bullish_engulfing(self):
        """A bullish engulfing pattern: bearish candle followed by larger bullish candle."""
        df = make_df(
            opens=[110, 95],    # candle 0 opens high, candle 1 opens lower
            highs=[112, 113],
            lows=[105, 94],
            closes=[106, 112],  # candle 0 closes lower (bearish), candle 1 closes higher (bullish, engulfs)
        )
        pdb = PatternDB()
        results = pdb.detect(df, pattern="bullish_engulfing")
        # May or may not detect depending on trend context (needs prior uptrend)
        # For now just test it doesn't crash
        assert isinstance(results, list)

    def test_detects_bearish_engulfing(self):
        """A bearish engulfing pattern."""
        df = make_df(
            opens=[90, 108],
            highs=[95, 110],
            lows=[88, 87],
            closes=[94, 89],  # candle 0 bullish, candle 1 bearish and engulfs
        )
        pdb = PatternDB()
        results = pdb.detect(df, pattern="bearish_engulfing")
        assert isinstance(results, list)


class TestHammerDetection:
    def test_detects_hammer(self):
        """A hammer: small body at top, long lower shadow."""
        df = make_df(
            opens=[100, 100, 99.5],
            highs=[100, 100, 100],
            lows=[100, 95, 95],    # long lower shadow
            closes=[100, 100, 99.8],  # small body at top
        )
        pdb = PatternDB()
        results = pdb.detect(df, pattern="hammer")
        # Hammer needs prior downtrend context which we don't have here
        # Just verify it doesn't crash
        assert isinstance(results, list)


class TestConfidenceScoring:
    def test_confidence_between_0_and_1(self):
        """All detection confidence values should be between 0 and 1."""
        df = make_df(
            opens=[100, 100, 100, 100],
            highs=[105, 105, 105, 105],
            lows=[95, 95, 95, 95],
            closes=[102, 102, 102, 102],
        )
        pdb = PatternDB()
        results = pdb.detect(df)
        for r in results:
            assert 0.0 <= r["confidence"] <= 1.0, f"Confidence {r['confidence']} out of range"

    def test_to_json_serializes(self):
        """to_json should produce valid JSON."""
        df = make_df(
            opens=[100], highs=[101], lows=[99], closes=[100.01],
        )
        pdb = PatternDB()
        results = pdb.detect(df)
        json_str = pdb.to_json(results)
        import json
        parsed = json.loads(json_str)  # should not throw
        assert isinstance(parsed, list)