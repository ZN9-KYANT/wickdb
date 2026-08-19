"""
Tests for pattern loading and validation.
"""

import pytest
from wickdb.loader import load_patterns, load_pattern
from wickdb.validate import validate_pattern


class TestPatternLoading:
    def test_load_all_patterns(self):
        patterns = load_patterns()
        assert len(patterns) >= 9, f"Expected at least 9 patterns, got {len(patterns)}"

    def test_load_specific_pattern(self):
        p = load_pattern("morning_star")
        assert p is not None
        assert p["id"] == "morning_star"
        assert p["name"] == "Morning Star"
        assert p["category"] == "bullish"

    def test_load_nonexistent_pattern(self):
        p = load_pattern("does_not_exist")
        assert p is None

    def test_all_patterns_have_required_fields(self):
        patterns = load_patterns()
        for p in patterns:
            assert "id" in p, f"Pattern missing 'id': {p}"
            assert "name" in p, f"Pattern missing 'name': {p.get('id')}"
            assert "category" in p, f"Pattern missing 'category': {p.get('id')}"
            assert "structure" in p, f"Pattern missing 'structure': {p.get('id')}"
            assert "signal" in p, f"Pattern missing 'signal': {p.get('id')}"


class TestPatternValidation:
    def test_valid_pattern_passes_validation(self):
        p = load_pattern("morning_star")
        clean = {k: v for k, v in p.items() if not k.startswith("_")}
        is_valid, errors = validate_pattern(clean)
        assert is_valid, f"morning_star should be valid but has errors: {errors}"

    def test_all_patterns_validate(self):
        patterns = load_patterns()
        for p in patterns:
            clean = {k: v for k, v in p.items() if not k.startswith("_")}
            is_valid, errors = validate_pattern(clean)
            assert is_valid, f"{p['id']} failed validation: {errors}"


class TestPatternStructure:
    def test_morning_star_structure(self):
        p = load_pattern("morning_star")
        struct = p["structure"]
        assert struct["candles"] == 3
        assert len(struct["requirements"]) == 3

    def test_hammer_structure(self):
        p = load_pattern("hammer")
        struct = p["structure"]
        assert struct["candles"] == 1
        assert len(struct["requirements"]) == 1

    def test_doji_is_neutral(self):
        p = load_pattern("doji")
        assert p["category"] == "neutral"

    def test_bullish_patterns_are_bullish(self):
        p = load_pattern("bullish_engulfing")
        assert p["category"] == "bullish"
        assert p["signal"]["direction"] == "bullish"

    def test_bearish_patterns_are_bearish(self):
        p = load_pattern("bearish_engulfing")
        assert p["category"] == "bearish"
        assert p["signal"]["direction"] == "bearish"