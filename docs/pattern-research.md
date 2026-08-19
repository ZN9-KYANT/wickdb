# WickDB Pattern Research — Source Data

> Research compiled August 19, 2026. Sources below are from backtested studies, not opinion pieces.

---

## Source 1: Liberated Stock Trader — 56,680 trades on 30 Dow Jones stocks (20 years)

**Methodology:** 25 candle patterns tested on 30 DJIA stocks over 20 years. 56,680 total trades. All long trades, 10-day hold. TrendSpider backtesting.

### Top 10 by Win Rate

| Rank | Pattern | Win Rate | Avg Profit/Trade | Trades Tested |
|------|---------|----------|-----------------|---------------|
| 1 | Inverted Hammer | 60.0% | 1.12% | 1,702 |
| 2 | Gravestone Doji | 57.0% | 0.65% | 1,553 |
| 3 | Bearish Engulfing | 57.0% | 0.62% | 4,096 |
| 4 | Shooting Star | 57.1% | 0.56% | — |
| 5 | Bearish Marubozu | 56.1% | 0.80% | 2,360 |
| 6 | Bearish Harami Cross | 57.0% | 0.57% | — |
| 7 | Spinning Top | 55.9% | 0.49% | — |
| 8 | Doji | 55.6% | 0.51% | — |
| 9 | Bullish Harami Cross | 55.3% | 0.58% | 1,609 |
| 10 | Bullish Harami | 55.2% | 0.50% | — |

**Key insight:** The average win rate across all patterns is 55.8%. The best pattern (Inverted Hammer) is only 60% — candlestick patterns provide a marginal edge, not a strong one. Context and confirmation matter more than the pattern itself.

---

## Source 2: Thomas Bulkowski — Encyclopedia of Candlestick Charts

**Methodology:** 4.7 million price bars, 103 candle patterns, 500 stocks over 10 years. Ranked by reversal/continuation rate + 10-day performance + frequency.

### Best Performing Patterns by Category

**Bullish Reversals:**
| Pattern | Reversal Rate | 10-Day Move |
|---------|--------------|-------------|
| Above the Stomach | 66% | +2.74% |
| Three Inside Up | 65% | +2.61% |

**Bearish Reversals:**
| Pattern | Reversal Rate | 10-Day Move |
|---------|--------------|-------------|
| Bearish Engulfing | 79% | -3.56% (bull market), -5.92% (bear market) |
| Dragonfly Doji | ~55% | -3.89% |

**Bullish Continuations:**
| Pattern | Continuation Rate | 10-Day Move |
|---------|-------------------|-------------|
| Long Black Day | 53% | +5.11% |
| Black Marubozu | 53% | +4.39% |

**Bearish Continuations:**
| Pattern | Continuation Rate | 10-Day Move |
|---------|-------------------|-------------|
| Long White Day | 58% | -3.91% |
| White Marubozu | 56% | -3.55% |

**Key insight:** Single-candle patterns (Marubozu, Long Black/White Day) can outperform multi-candle patterns when used in the right context. Bulkowski found that "five of the eight best-performing candles" are single-line patterns.

---

## Source 3: Quantified Strategies — 75 patterns backtested on S&P 500

**Methodology:** 75 candlestick patterns coded as mechanical trading rules, backtested on S&P 500. Combined strategy approach.

**Key insight:** The best results came from combining the top 5 patterns into a single rule-based strategy, not from trading individual patterns. Exit rule: close above previous day's high.

---

## Patterns to Prioritize for WickDB Tier 2

Based on the research, these patterns have the strongest statistical backing and should be added next:

### High Priority (statistically proven edge)

1. **Inverted Hammer** — 60% win rate, best single pattern in 56K trade study
2. **Bearish Marubozu / Black Marubozu** — 56% win rate, best Bullowski continuation
3. **Gravestone Doji** — 57% win rate, distinct from standard Doji
4. **Bullish Harami / Bullish Harami Cross** — 55% win rate, classic reversal
5. **Bearish Harami / Bearish Harami Cross** — 57% win rate
6. **Dragonfly Doji** — Bulkowski's #2 bearish reversal, 3.89% move
7. **Three Inside Up** — 65% reversal rate, Bulkowski's #2 bullish reversal
8. **Above the Stomach** — 66% reversal rate, Bulkowski's #1 bullish reversal (not widely known!)
9. **Long Black Day** — 5.11% move, Bulkowski's #1 bullish continuation
10. **Long White Day** — 3.91% move, Bulkowski's #1 bearish continuation

### Medium Priority (classic but moderate edge)

11. **Piercing Line** — classic bullish reversal, moderate win rate
12. **Dark Cloud Cover** — classic bearish reversal, moderate win rate
13. **Spinning Top** — 55.9% win rate, indecision signal
14. **White Marubozu** — 56% continuation rate, Bulkowski
15. **Hanging Man** — classic bearish reversal at top of uptrend

### Modern/Quant Patterns (community-sourced, needs validation)

16. **Fair Value Gap (FVG)** — ICT/SMC pattern, popular but not formally backtested
17. **Order Block** — ICT/SMC pattern, needs formal definition
18. **Wick Rejection** — custom: % of range in wick, needs parameterization
19. **Failed Breakout** — pattern failure as a contrarian signal

---

## Key Takeaways for the Project

1. **No pattern has a win rate above 60%** — manage expectations. The edge is marginal.
2. **Context matters more than the pattern** — prior trend, volume, and market regime (Hurst exponent!) are bigger factors than the candle shape.
3. **Combining patterns works better than individual ones** — the Quantified Strategies study showed a combined strategy outperformed any single pattern.
4. **Single-candle patterns are underrated** — Bulkowski's research shows 5 of 8 best performers are single-candle. The Japanese tradition favors multi-candle patterns, but the data says otherwise.
5. **Bearish patterns tend to outperform bullish ones** — fear moves faster than greed. Bearish Engulfing at 79% reversal rate vs Bullish Engulfing at ~57%.

---

*Compiled: August 19, 2026*
*Sources: LiberatedStockTrader (56,680 trades), Thomas Bulkowski (Encyclopedia of Candlestick Charts, 4.7M bars), Quantified Strategies (75 patterns on S&P 500)*