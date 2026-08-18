"""
CLI interface for CandleDB.

Usage:
    candledb list                          # List all patterns
    candledb list --category bullish       # List bullish patterns
    candledb detect SPY --days 100         # Detect patterns in SPY
    candledb detect SPY --pattern hammer   # Detect specific pattern
    candledb validate                       # Validate all pattern files
    candledb show morning_star              # Show pattern details
"""

import argparse
import json
import sys

from candledb import PatternDB
from candledb.validate import validate_all


def cmd_list(args):
    pdb = PatternDB()
    ids = pdb.list_patterns(category=args.category)
    if ids:
        print(f"Patterns ({len(ids)}):")
        for pid in ids:
            p = pdb.get_pattern(pid)
            cat = p.get("category", "")
            sub = p.get("subcategory", "")
            name = p.get("name", pid)
            print(f"  {pid:30s} {cat:10s} {sub:15s} {name}")
    else:
        print("No patterns found.")


def cmd_show(args):
    pdb = PatternDB()
    p = pdb.get_pattern(args.pattern_id)
    if not p:
        print(f"Pattern '{args.pattern_id}' not found.")
        sys.exit(1)
    # Strip internal fields
    p = {k: v for k, v in p.items() if not k.startswith("_")}
    print(json.dumps(p, indent=2, default=str))


def cmd_validate(args):
    results = validate_all()
    print(f"Valid: {len(results['valid'])} patterns")
    if results["valid"]:
        for pid in results["valid"]:
            print(f"  ✅ {pid}")
    if results["invalid"]:
        print(f"\nInvalid: {len(results['invalid'])} patterns")
        for item in results["invalid"]:
            print(f"  ❌ {item['id']}")
            for err in item["errors"]:
                print(f"     {err}")
        sys.exit(1)


def cmd_detect(args):
    pdb = PatternDB()

    # Load OHLCV data
    try:
        import yfinance as yf
    except ImportError:
        print("yfinance is required for detection. Install with: pip install yfinance")
        sys.exit(1)

    ticker = args.ticker.upper()
    period = "1y" if args.days > 60 else "6mo"
    df = yf.download(ticker, period=period, progress=False)

    if df.empty:
        print(f"No data for {ticker}")
        sys.exit(1)

    # Flatten multi-level columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Normalize column names
    df = df.rename(columns=str.lower)

    results = pdb.detect(
        df,
        pattern=args.pattern,
        category=args.category,
        lookback=args.days,
    )

    if results:
        print(f"Detected {len(results)} pattern(s) in {ticker} (last {args.days} days):")
        for r in results:
            conf_bar = "█" * int(r["confidence"] * 10)
            print(
                f"  {r['pattern']:30s} {r.get('name', ''):25s} "
                f"conf={r['confidence']:.2f} {conf_bar:10s} "
                f"@ {r.get('index', r.get('row', ''))}"
            )
    else:
        print(f"No patterns detected in {ticker} (last {args.days} days).")


def main():
    parser = argparse.ArgumentParser(
        prog="candledb",
        description="CandleDB — Open-source candlestick pattern database and detection engine",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list
    p_list = subparsers.add_parser("list", help="List all patterns")
    p_list.add_argument("--category", choices=["bullish", "bearish", "neutral"], help="Filter by category")
    p_list.set_defaults(func=cmd_list)

    # show
    p_show = subparsers.add_parser("show", help="Show a single pattern definition")
    p_show.add_argument("pattern_id", help="Pattern ID (e.g. morning_star)")
    p_show.set_defaults(func=cmd_show)

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate all pattern files against schema")
    p_validate.set_defaults(func=cmd_validate)

    # detect
    p_detect = subparsers.add_parser("detect", help="Detect patterns in a stock's OHLCV data")
    p_detect.add_argument("ticker", help="Stock ticker (e.g. SPY, AAPL)")
    p_detect.add_argument("--days", type=int, default=100, help="Lookback days (default: 100)")
    p_detect.add_argument("--pattern", help="Detect specific pattern ID")
    p_detect.add_argument("--category", choices=["bullish", "bearish", "neutral"], help="Filter by category")
    p_detect.set_defaults(func=cmd_detect)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()