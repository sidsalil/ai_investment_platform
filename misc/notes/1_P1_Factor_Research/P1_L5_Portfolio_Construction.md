# P1-L5: Portfolio Construction from Signals

## Where we are in the pipeline

By the end of P1-L4, a stock doesn't have a raw factor value anymore — it has a **sector-neutral z-score**, a clean, comparable number telling you how strong its momentum signal is relative to its sector peers. Today's question: **how do you turn a list of 20 (or 100, or 500) z-scores into an actual portfolio** — a set of positions with real weights that add up to something you could hand to a trader?

This is the step between "I have a signal" and "I have something to backtest." Everything in P1-L6 (Information Coefficient) and P1-L7 (factor decay) evaluates the *portfolio* you build today, not the raw signal. Get this step wrong and every later number is measuring the wrong thing.

---

## Concept 1: Bucketing — deciles and quintiles

**Plain-language idea first.** Imagine you're a Portfolio Manager (PM) at Fidelity and an analyst hands you a ranked list of 100 stocks by conviction, most to least. You're not going to build 100 individual position sizes by hand justified stock by stock — you're going to group them into buckets of similar conviction and treat each bucket similarly. That's exactly what bucketing does, mechanically, at scale.

**Definitions:**
- A **decile** portfolio splits the ranked universe into **10 equal-sized groups** (10% of stocks each).
- A **quintile** portfolio splits it into **5 equal-sized groups** (20% of stocks each).
- The bucket with the *highest* z-scores (best signal) is the **top bucket**. The bucket with the *lowest* z-scores is the **bottom bucket**.

**Why bucket at all, instead of using the raw ranking directly?** Two reasons:
1. **Noise reduction.** Any individual stock's exact rank (#37 vs #38) is mostly noise — the difference between a 0.41 z-score and a 0.39 z-score isn't meaningfully different information. A bucket smooths this out; you're betting on "the top 20% as a group," not on razor-thin rank differences.
2. **Statistical practicality.** You need groups big enough to compute meaningful average returns per bucket (this becomes essential in P1-L6 for Information Coefficient work).

**Decile vs quintile — which one, and when?** More buckets = finer-grained bets, but each bucket has fewer stocks, so each bucket's average return is noisier (a bad quarter for one stock swings the whole bucket more when the bucket only has 10 stocks vs 50).

| Universe | Decile (10 buckets) | Quintile (5 buckets) |
|---|---|---|
| NASDAQ-100 (100 stocks) | 10 stocks/bucket — usable but thin | 20 stocks/bucket — more stable |
| S&P 500 (500 stocks) | 50 stocks/bucket — fine | 100 stocks/bucket — very stable |

**Decision for Project 1:** default to **quintiles** (5 buckets) across both the NASDAQ-100 development universe and the S&P 500 final universe, since 10 stocks per decile bucket on NASDAQ-100 is thin enough to make single-stock noise a real problem during the iteration phase where we're debugging pipeline mechanics, not yet doing final statistical work. Decile bucketing will be retained as a configurable option for the final S&P 500 run in Phase 4, where 50 stocks/bucket is statistically fine and finer granularity might be worth showing.

---

### Worked example: 20 stocks, sector-neutral z-scores → quintiles

Let's use a toy 20-stock universe (a stand-in for a slice of NASDAQ-100) with momentum z-scores already computed per the P1-L4 pipeline (winsorized, then sector-neutral z-scored). Sorted from highest to lowest signal:

| Rank | Ticker | Z-score | Quintile |
|---|---|---|---|
| 1 | AAA | 2.10 | **Q5 (top)** |
| 2 | BBB | 1.85 | **Q5 (top)** |
| 3 | CCC | 1.60 | **Q5 (top)** |
| 4 | DDD | 1.35 | **Q5 (top)** |
| 5 | EEE | 1.05 | Q4 |
| 6 | FFF | 0.80 | Q4 |
| 7 | GGG | 0.55 | Q4 |
| 8 | HHH | 0.30 | Q4 |
| 9 | III | 0.15 | Q3 |
| 10 | JJJ | 0.05 | Q3 |
| 11 | KKK | -0.05 | Q3 |
| 12 | LLL | -0.15 | Q3 |
| 13 | MMM | -0.30 | Q2 |
| 14 | NNN | -0.55 | Q2 |
| 15 | OOO | -0.80 | Q2 |
| 16 | PPP | -1.05 | Q2 |
| 17 | QQQ | -1.35 | **Q1 (bottom)** |
| 18 | RRR | -1.60 | **Q1 (bottom)** |
| 19 | SSS | -1.85 | **Q1 (bottom)** |
| 20 | TTT | -2.10 | **Q1 (bottom)** |

Mechanically: sort by z-score descending, then slice into 5 equal groups of 4. That's the entire bucketing algorithm — no more, no less. Ties (two stocks with identical z-scores landing on a bucket boundary) are a real edge case; standard practice is to break ties by a secondary sort key (e.g., ticker alphabetically, or market cap) for reproducibility. Note this for P1-Build-4.

---

## Concept 2: Long-only vs long-short

**Plain-language idea first.** Once you know which stocks are in your top and bottom buckets, you have to decide *what to actually do* with that information. There are two fundamentally different postures:

- **Long-only**: you buy the top bucket. You do nothing with the bottom bucket — you simply don't own those stocks. This is what almost every real long-only mutual fund or liquid-alts-adjacent-but-still-long-biased strategy at a firm like Fidelity actually does, because most mandates don't permit shorting.
- **Long-short**: you buy the top bucket **and simultaneously short-sell the bottom bucket**. "Shorting" means borrowing a stock you don't own and selling it, betting its price falls, so you profit if the bottom-bucket stocks underperform.

**Why would a researcher ever want long-short, if most real portfolios are long-only?** This is the single most important idea in today's lesson, so slow down here.

Any stock's return is (very roughly, per P1-L1's factor model): `return = market return + factor-specific return + idiosyncratic return`. If you just buy the top quintile, your portfolio's return is contaminated by the **market's overall direction** during your holding period — if the whole market rallies 5% that month, your top-quintile portfolio looks great even if your momentum *signal itself* did nothing useful, because you were just riding the market beta.

**Long-short cancels this out.** If your top and bottom buckets have roughly similar average market exposure (both are just "stocks in the universe," after all), then:

`Long-short return ≈ (market + top-bucket factor effect) − (market + bottom-bucket factor effect) = top-bucket factor effect − bottom-bucket factor effect`

The market terms subtract out. What's left is **specifically the return difference attributable to having a high vs. low signal** — which is the "pure" signal you're actually trying to test. This is why almost all factor *research* (as opposed to factor *product design*) is done long-short, even at firms that will eventually ship a long-only product: it's the cleanest way to ask "does this signal actually predict anything?" separate from "did the market go up this month?"

| | Long-only (top quintile) | Long-short (top minus bottom quintile) |
|---|---|---|
| **What you hold** | Buy top bucket only | Buy top bucket, short bottom bucket |
| **Net market exposure** | Full market exposure (you're 100% long stocks) | ≈ Zero (long and short roughly cancel) — this is called **dollar-neutral** |
| **What the return measures** | Absolute performance — includes market direction | The isolated factor effect — "does the signal spread returns apart?" |
| **Real-world analogy** | A typical actively-managed long-only mutual fund | A market-neutral hedge fund strategy |
| **Project 1 usage** | Practitioner-facing view for the memo | Research/evaluation default — feeds IC (P1-L6) |

**Important nuance to flag now, revisit later:** "dollar-neutral" (equal dollars long and short) is **not the same thing** as "market-neutral" or "beta-neutral" (equal *market risk* long and short). If your top-bucket stocks happen to have systematically higher market beta than your bottom-bucket stocks (common with momentum — high-momentum stocks are often higher-beta), a dollar-neutral long-short portfolio can still have leftover market exposure. True beta-neutrality requires explicitly matching betas, not just dollar amounts. This is a real methodology gotcha — flagging it now, full treatment deferred to P1-L8 (biases) and noted as a carried-forward item below.

---

### Worked example: long-only vs long-short weights (equal-weighted for now)

Using our 20-stock example, quintile size = 4 stocks. Equal-weighting means every stock in a bucket gets the same weight.

**Long-only, top quintile, equal-weighted:**

| Ticker | Z-score | Weight |
|---|---|---|
| AAA | 2.10 | 25.0% |
| BBB | 1.85 | 25.0% |
| CCC | 1.60 | 25.0% |
| DDD | 1.35 | 25.0% |
| **Total** | | **100%** |

Simple: 1 ÷ 4 stocks = 25% each. Fully invested, no shorts, net exposure = 100% long.

**Long-short, top minus bottom quintile, equal-weighted:**

| Ticker | Z-score | Position | Weight |
|---|---|---|---|
| AAA | 2.10 | Long | +25.0% |
| BBB | 1.85 | Long | +25.0% |
| CCC | 1.60 | Long | +25.0% |
| DDD | 1.35 | Long | +25.0% |
| QQQ | -1.35 | Short | -25.0% |
| RRR | -1.60 | Short | -25.0% |
| SSS | -1.85 | Short | -25.0% |
| TTT | -2.10 | Short | -25.0% |
| **Net exposure** | | | **0%** |
| **Gross exposure** | | | **200%** (100% long + 100% short) |

Two new terms here, defined plainly:
- **Net exposure** = longs minus shorts (as a % of capital). Zero net exposure means you're market-neutral on a dollar basis.
- **Gross exposure** = longs plus shorts (as a % of capital, ignoring sign). 200% gross means you're using leverage — you've taken $2 of position for every $1 of actual capital, since you're fully long AND fully short simultaneously.

---

## Concept 3: Equal weighting vs signal weighting

**Plain-language idea first.** Within a bucket, do all stocks get treated identically ("I have equal conviction in all 4 top stocks"), or should stocks with a *more extreme* signal get a bigger position ("AAA's z-score of 2.10 is much stronger than DDD's 1.35 — shouldn't I bet more on AAA")? That's the equal-weight vs signal-weight choice.

**Equal weighting**: every stock in a bucket gets `1 ÷ (number of stocks in the bucket)`. Simple, robust, doesn't require trusting the *precise magnitude* of the z-score — just its rank/bucket membership.

**Signal weighting**: weight is proportional to the z-score itself, normalized so the weights in each bucket sum to 100% (long side) or -100% (short side). Formula:

`weight_i = z_i / (sum of all z's on that side)`

**Why would you ever *not* signal-weight, if you have the more precise number available?** Because z-score magnitude carries estimation error too — the difference between a 2.10 and a 1.85 might just be measurement noise, not real extra conviction. Signal-weighting concentrates more capital into fewer names (whichever have the most extreme z-scores), which increases single-stock concentration risk. Equal-weighting is the more conservative, more diversified default; signal-weighting is a more aggressive bet that your z-score magnitudes are trustworthy, not just their ranks.

---

### Worked example: signal-weighted long-short

Same 8 stocks (top and bottom quintile) as above, now weighted proportional to |z-score| instead of equally.

**Long side (top quintile):**

| Ticker | Z-score | Calculation | Weight |
|---|---|---|---|
| AAA | 2.10 | 2.10 / 6.90 | 30.4% |
| BBB | 1.85 | 1.85 / 6.90 | 26.8% |
| CCC | 1.60 | 1.60 / 6.90 | 23.2% |
| DDD | 1.35 | 1.35 / 6.90 | 19.6% |
| **Sum of z's** | **6.90** | | **Total: 100%** |

**Short side (bottom quintile)** — note the short side's weights, by symmetry of this example, mirror the long side's exactly, but attached to the *opposite-ranked* stock (the most extreme short-side z gets the biggest short weight):

| Ticker | Z-score | \|Z-score\| | Calculation | Weight |
|---|---|---|---|---|
| QQQ | -1.35 | 1.35 | 1.35 / 6.90 | -19.6% |
| RRR | -1.60 | 1.60 | 1.60 / 6.90 | -23.2% |
| SSS | -1.85 | 1.85 | 1.85 / 6.90 | -26.8% |
| TTT | -2.10 | 2.10 | 2.10 / 6.90 | -30.4% |
| **Sum of \|z\|'s** | **6.90** | | | **Total: -100%** |

**Comparing the two weighting schemes side by side:**

| Ticker | Equal weight | Signal weight | Difference |
|---|---|---|---|
| AAA (z=2.10, strongest long) | 25.0% | 30.4% | Signal-weighting bets *more* on your highest-conviction name |
| DDD (z=1.35, weakest long) | 25.0% | 19.6% | Signal-weighting bets *less* on your weakest-conviction name in the bucket |
| TTT (z=-2.10, strongest short) | -25.0% | -30.4% | Same logic, short side |

Net and gross exposure are identical between the two schemes here (0% net, 200% gross) — weighting scheme changes *concentration within* the exposure, not the total amount of exposure.

---

## Putting it together: the full portfolio construction decision tree

| Step | Choice | Project 1 default |
|---|---|---|
| 1. Bucket count | Decile vs quintile | **Quintile** (5 buckets) |
| 2. Long-only vs long-short | Depends on purpose | **Long-short** for research/IC (P1-L6 onward); **long-only top-quintile** retained as a practitioner-facing alternative view in the memo |
| 3. Weighting scheme | Equal vs signal | **Equal-weighted** as the default; signal-weighted retained as a configurable diagnostic to show conviction-weighting |

**Why equal-weighted long-short as the *research* default, specifically:** it's the cleanest, least assumption-laden way to ask "does this signal separate winners from losers?" It doesn't require trusting z-score magnitudes (only rank/bucket membership), and it's the standard convention in academic factor research (this is literally how Fama-French portfolios are constructed) — so it's also the version most directly comparable to published factor research if you ever want to sanity-check your numbers against known results.

---

## Concepts flagged but not fully resolved (carried forward)

- **Dollar-neutral ≠ beta-neutral.** A long-short portfolio that's balanced in *dollars* can still carry leftover market exposure if the long and short buckets have different average market betas. Full treatment deferred to P1-L8 (biases).
- **Tie-breaking at bucket boundaries.** When two stocks have identical or near-identical z-scores straddling a bucket cutoff, a deterministic tie-breaking rule (e.g., secondary sort by ticker or market cap) is needed for reproducibility. Needed at implementation time in P1-Build-4.
- **Rebalancing frequency** (how often you redo this bucketing/weighting process — daily, weekly, monthly) is a related but separate question, deferred to P1-L7 (factor decay/turnover) since it depends on how fast the signal changes.

---

## One-paragraph summary (the "explain to a non-quant" version)

You take your ranked signal and slice it into buckets — quintiles, meaning 5 equal-sized groups from strongest to weakest signal. You buy the top bucket. For research purposes, you also short the bottom bucket, because that cancels out the market's overall direction and leaves you with a clean read on whether your signal actually separates winners from losers — this is long-short, dollar-neutral construction. Within each bucket, you can either treat every stock the same (equal-weighted, more conservative) or bet more on the stocks with the most extreme signal values (signal-weighted, more concentrated, more aggressive). Project 1 defaults to quintile buckets, long-short for research, equal-weighted as the baseline — the same convention used in classic academic factor research.
