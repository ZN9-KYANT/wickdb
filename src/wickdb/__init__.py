"""
WickDB — Open-source candlestick pattern database and detection engine.
"""

__version__ = "0.1.0"
__all__ = ["PatternDB", "load_patterns", "validate_pattern"]

from wickdb.db import PatternDB
from wickdb.loader import load_patterns
from wickdb.validate import validate_pattern