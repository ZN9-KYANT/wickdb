"""
CandleDB — Open-source candlestick pattern database and detection engine.
"""

__version__ = "0.1.0"
__all__ = ["PatternDB", "load_patterns", "validate_pattern"]

from candledb.db import PatternDB
from candledb.loader import load_patterns
from candledb.validate import validate_pattern