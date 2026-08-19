# WickDB

> Open-source candlestick (k-line) pattern database and detection engine for quantitative analysis. Machine-readable pattern definitions, confidence-scored detection, and community-backtested reliability data.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen.svg)](#testing)

## Why?

Candlestick patterns are one of the oldest tools in technical analysis, yet there is no canonical, machine-readable database of pattern definitions. Every textbook, website, and trading platform defines patterns slightly differently — different names, different criteria, different visual representations. This makes it impossible for AI agents, quant models, and backtesting frameworks to reliably identify and compare patterns.

**WickDB solves this by providing:**

- 📐 **Measurable definitions** — every pattern has formal parameters (body ratios, shadow ratios, gap thresholds) instead of vague descriptions like "small body"
- 🤖 **Machine-readable** — patterns are stored as YAML files validated against a JSON Schema, with JSON output for API/agent consumption
- 🔍 **Detection engine** — a Python package that detects patterns in OHLCV data with confidence scoring
- 📊 **Community backtesting** — every pattern file includes a backtest section where the community contributes real win rates, sample sizes, and average returns
- 🆓 **Free and open source** — MIT licensed, no paywalls, no proprietary lock-in

## Installation

```bash
# Basic installation (pattern database + loader)
pip install wickdb

# With detection engine (adds yfinance for live data)
pip install wickdb[detect]

# With validation (adds jsonschema for schema validation)
pip install wickdb[validate]

# Full development setup
pip install wickdb[dev]
```

## Quick Start

### CLI

```bash
# List all patterns
wickdb list

# List bullish patterns only
wickdb list --category bullish

# Show a pattern's full definition
wickdb show morning_star

# Validate all pattern files against the schema
wickdb validate

# Detect patterns in live stock data
wickdb detect SPY --days 100

# Detect specific pattern
wickdb detect AAPL --pattern hammer

# Filter by category
wickdb detect TSLA --category bearish --days 50
```

### Python API

```python
from wickdb import PatternDB

# Initialize the pattern database (auto-loads all YAML patterns)
pdb = PatternDB()

# List available patterns
print(pdb.list_patterns())
# ['morning_star', 'hammer', 'bullish_engulfing', 'doji', ...]

# Load OHLCV data (any DataFrame with open/high/low/close/volume columns)
import yfinance as yf
df = yf.download("SPY", period="1y")

# Detect all patterns in the last 100 candles
results = pdb.detect(df, lookback=100)
# [
#   {
#     "pattern": "morning_star",
#     "name": "Morning Star",
#     "category": "bullish",
#     "index": "2026-07-15",
#     "confidence": 0.87,
#     "signal": {"direction": "bullish", "action": "buy"}
#   },
#   ...
# ]

# Detect a specific pattern
results = pdb.detect(df, pattern="hammer")

# Filter by category
bullish = pdb.detect(df, category="bullish")

# Export results as JSON (for AI agent consumption)
json_output = pdb.to_json(results)
```

### Pattern File Format

Patterns are defined as YAML files, validated against a [JSON Schema](schemas/pattern.schema.json):

```yaml
# patterns/bullish/reversal/morning_star.yaml
id: morning_star
name: Morning Star
category: bullish
subcategory: reversal
type: essential
probability: moderate

structure:
  candles: 3
  requirements:
    - candle:
        index: 0
        trend: downtrend_required
        body_size: large
        color: bearish
    - candle:
        index: 1
        body_size: small
        gap_down: true
        color: any
    - candle:
        index: 2
        body_size: large
        color: bullish
        close_into_candle_0: true

parameters:
  min_body_ratio: 0.05
  max_body_ratio: 0.30
  large_body_ratio: 0.60
  gap_threshold: 0.001

context:
  prior_trend:
    required: true
    direction: downtrend
    min_lookback: 5
  volume:
    recommended: true
    description: "Volume should increase on candle 3 for confirmation"

signal:
  direction: bullish
  action: buy
  stop_loss: below_candle_1_low
  target: recent_swing_high

backtest: []

tags:
  - reversal
  - three-candle
  - bullish
  - morning-star
```

## Pattern Catalog

### Tier 1: Essential Patterns (currently 9)

| Pattern | Category | Candles | Signal | Status |
|---------|----------|---------|--------|--------|
| Morning Star | Bullish / Reversal | 3 | Buy | ✅ |
| Hammer | Bullish / Reversal | 1 | Buy | ✅ |
| Bullish Engulfing | Bullish / Reversal | 2 | Buy | ✅ |
| Three White Soldiers | Bullish / Continuation | 3 | Buy | ✅ |
| Evening Star | Bearish / Reversal | 3 | Sell | ✅ |
| Shooting Star | Bearish / Reversal | 1 | Sell | ✅ |
| Bearish Engulfing | Bearish / Reversal | 2 | Sell | ✅ |
| Three Black Crows | Bearish / Continuation | 3 | Sell | ✅ |
| Doji | Neutral / Indecision | 1 | Hold | ✅ |

### Tier 2: Advanced Patterns (planned)

Abandoned Baby, Three Inside Up/Down, Three Outside Up/Down, Mat Hold, Rising/Falling Three Methods, Separating Lines, Stick Sandwich, Kicker, Belt Hold, and more.

### Tier 3: Modern/Quant Patterns (planned)

Fair Value Gap (FVG), Order Block, Wick Rejection, Volatility Squeeze, Gap Fill, Failed Breakout — patterns discovered through quantitative analysis, not traditional Japanese literature.

## Confidence Scoring

Every detection includes a confidence score (0.0–1.0) based on:

| Factor | Description |
|--------|-------------|
| `structure_match` | How closely the candles match the ideal pattern parameters |
| `volume_confirms` | Whether volume confirms the pattern (if recommended) |
| `trend_context` | Whether the required prior trend is present |
| `historical_win_rate` | Community backtest win rate for this instrument/timeframe |

```python
{
  "pattern": "morning_star",
  "confidence": 0.87,
  "factors": {
    "structure_match": 0.95,
    "volume_confirms": 0.80,
    "trend_context": 0.90,
    "historical_win_rate": 0.63
  }
}
```

## Project Structure

```
wickdb/
├── patterns/              # Pattern definitions (YAML)
│   ├── bullish/
│   │   ├── reversal/      # Morning Star, Hammer, Bullish Engulfing, ...
│   │   └── continuation/  # Three White Soldiers, ...
│   ├── bearish/
│   │   ├── reversal/      # Evening Star, Shooting Star, Bearish Engulfing, ...
│   │   └── continuation/  # Three Black Crows, ...
│   └── neutral/           # Doji, Spinning Top, ...
├── schemas/
│   └── pattern.schema.json  # JSON Schema for validation
├── src/wickdb/
│   ├── __init__.py        # Public API
│   ├── db.py              # PatternDB — detection engine
│   ├── loader.py          # YAML pattern loader
│   ├── validate.py        # Schema validation
│   └── cli.py             # CLI interface
├── tests/                 # 22 tests (all passing)
├── pyproject.toml
└── LICENSE
```

## Contributing

### Adding a New Pattern

1. Create a new YAML file in the appropriate `patterns/<category>/<subcategory>/` directory
2. Follow the [pattern file format](#pattern-file-format) and ensure all required fields are present
3. Validate your pattern: `wickdb validate`
4. Add tests if the pattern has unique detection logic
5. Submit a PR

### Contributing Backtest Data

Every pattern file has a `backtest` array. Add your backtest results:

```yaml
backtest:
  - instrument: SPY
    timeframe: daily
    win_rate: 0.63
    sample_size: 412
    avg_return_5d: 1.8%
    source: community
    contributor: "@yourhandle"
    date: "2026-08-15"
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=wickdb
```

## Roadmap

- [x] Phase 1: JSON Schema + 9 essential patterns + detection engine
- [ ] Phase 2: Tier 2 advanced patterns (20-30) + improved confidence scoring
- [ ] Phase 3: Backtesting framework + community contribution guidelines
- [ ] Phase 4: MCP server for AI agent integration + REST API + visualization

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

- Harold Edwin Hurst — for reminding us that pattern recognition transcends disciplines
- Steve Nison — for bringing Japanese candlestick analysis to Western markets
- The open-source quant community