# P1-L4: Signal Construction — Turning Data into Predictions

**Completed:** 2026-07-12

Before we start: this lesson builds directly on P1-L3. You now know how to compute a **return** correctly (log vs simple, adjusted vs raw). A "factor" like momentum is just a number computed from those returns for each stock — but a raw factor number, by itself, is not usable for building a portfolio. This lesson is about the transformation step between "I have a raw number for each stock" and "I have a comparable, tradeable signal."

---

## 1. Signal vs. Factor — a distinction worth being precise about

You've been using the word "factor" loosely since P1-L1. Time to sharpen it.

| Term | What it means | Example |
|---|---|---|
| **Raw factor value** | The literal computed number for a stock, in its natural units | NVDA's 12-month-minus-1-month momentum = 95% |
| **Signal** | The raw factor value *after* it has been transformed onto a scale that is comparable across every stock in the universe, on that date | NVDA's momentum **z-score** = 1.53 |

Think of it like a performance review at Fidelity. "Managed a $2B book" and "closed 40 tickets" are both raw facts — but they're not comparable to each other, or across employees with different roles, until you convert them into something like a percentile ranking within a peer group. That converted, comparable version is the "signal." The raw fact is real but not directly rankable against other raw facts.

**Why this matters for Project 1:** every downstream step — portfolio construction (P1-L5), Information Coefficient (P1-L6) — operates on the *signal*, not the raw factor. If the signal construction step is done sloppily, everything downstream inherits the flaw, even if the raw factor calculation was perfect.

---

## 2. Why raw factors can't be used directly — the apples-to-oranges problem

Three separate problems, each independently disqualifying a raw factor from direct use:

**Problem 1: Different factors live on different scales.**
A momentum factor might range from -30% to +90%. A price-to-earnings (P/E) ratio might range from 8 to 45. A dollar-volume liquidity factor might range from $10,000 to $50,000,000. You cannot average, combine, or compare these numbers directly — it's like comparing a temperature in Celsius to a distance in miles.

**Problem 2: Outliers dominate.**
A single extreme value (a stock up 95% in 11 months during an AI boom) can swamp everything else if you're not careful. You'll see this happen numerically in Section 3.

**Problem 3: A "signal" can secretly be a hidden sector bet.**
If you rank stocks by raw momentum and every tech stock happens to be up and every utility happens to be flat, your "momentum signal" isn't measuring momentum — it's really just measuring "is this a tech stock." You'll see this happen numerically in Section 5, and it's the most important trap in this lesson.

The fix for all three problems is **cross-sectional normalization** — comparing each stock only to its peers *on that specific date*, not comparing across time and not comparing raw units directly. "Cross-sectional" means: across all stocks, at one point in time — as opposed to "time-series," which would mean looking at one stock across many dates. Signal construction is a cross-sectional exercise.

---

## 3. Z-scoring — the core normalization tool

### 3.1 Intuition first

Before the formula: a **z-score** answers one question — *"how unusual is this value, measured in units of typical spread, relative to its peer group?"*

Analogy from your world: if a portfolio manager tells you "the fund returned 8%," that number means nothing until you know the context. Was the peer group average 2%, or was it 15%? A z-score bakes that context in automatically. A z-score of +2.0 means "two typical-sized moves better than average." A z-score of 0 means "exactly average." A z-score of -1.5 means "one and a half typical-sized moves worse than average."

The "typical size of a move" in a group of numbers has a name: **standard deviation**. Standard deviation measures how spread out a group of numbers is around their average. If all 8 stocks in a universe had nearly identical momentum, the standard deviation would be small, and even a modest difference would produce a large z-score (because "unusual" is relative to how much variation normally exists). If the stocks varied wildly, the standard deviation would be large, and only a truly extreme value would produce a large z-score.

### 3.2 The formula

z_i = (x_i − mean) / standard_deviation

Where:
- x_i = the raw factor value for stock i
- mean = the average raw factor value across all stocks in the universe, on that date
- standard_deviation (commonly written using the Greek letter sigma, σ) = the standard deviation of the raw factor values across all stocks in the universe, on that date

### 3.3 Worked example — raw momentum, no cleanup yet

Eight stocks, two sectors, raw 12-month-minus-1-month momentum (from P1-L3's return conventions):

| Stock | Sector | Raw momentum (%) |
|---|---|---|
| AAPL | Tech | 18 |
| MSFT | Tech | 22 |
| NVDA | Tech | 95 |
| INTC | Tech | -5 |
| DUK | Utilities | 3 |
| SO | Utilities | 5 |
| AEP | Utilities | 2 |
| NEE | Utilities | 8 |

**Step 1 — mean:** (18+22+95-5+3+5+2+8)/8 = 148/8 = 18.5

**Step 2 — standard deviation.** (Skip the derivation mechanics for now — just know it's computed from how far each value sits from the mean, squared to remove negative signs, averaged, then square-rooted.) Result: standard deviation ≈ 30.05

**Step 3 — z-scores:**

| Stock | Sector | Raw (%) | Deviation from mean | z-score |
|---|---|---|---|---|
| AAPL | Tech | 18 | -0.5 | -0.017 |
| MSFT | Tech | 22 | +3.5 | 0.116 |
| NVDA | Tech | 95 | +76.5 | **2.546** |
| INTC | Tech | -5 | -23.5 | -0.782 |
| DUK | Utilities | 3 | -15.5 | -0.516 |
| SO | Utilities | 5 | -13.5 | -0.449 |
| AEP | Utilities | 2 | -16.5 | -0.549 |
| NEE | Utilities | 8 | -10.5 | -0.349 |

**What went wrong here:** NVDA's single outlier value pulled the mean up and inflated the standard deviation so much that it dwarfs every other stock. NVDA's z-score of 2.546 is enormous compared to everything else — but look closely: MSFT (raw 22%) and AAPL (raw 18%) barely differ from each other in z-score terms (0.116 vs -0.017), even though a 22% vs 18% momentum difference is real and probably meaningful. The outlier has compressed all the *real* differentiation among the other seven stocks into a narrow band near zero. This is Problem 2 from Section 2, now visible in numbers.

---

## 4. Winsorization — controlling the outlier problem

### 4.1 Intuition first

**Winsorization** is capping extreme values at a threshold, rather than deleting them. The name comes from Charles Winsor, a statistician who advocated this approach over simply discarding outliers.

Analogy: imagine you're calculating average deal size on your sales team, and one rep closed a once-in-a-career $500M enterprise deal. If you leave it in raw, it distorts every comparison. If you delete it, you lose the (real, legitimate) information that this rep did close an unusually large deal. Winsorization does neither — it says "treat this value as if it were only as extreme as the edge of what's normal," capping it at, say, the 99th percentile value instead of deleting it or leaving it untouched. NVDA's momentum being unusually high is real and worth keeping — but treating it as "95% better than average" versus "meaningfully above average, but not so extreme it breaks the whole scale" is the judgment call winsorization makes.

This is different from **trimming**, which deletes outlier observations entirely. Winsorization keeps every stock in the universe — it just caps the *value*, not the *stock*.

### 4.2 The method

Pick a percentile threshold — common industry choices are the 1st/99th percentile or the 5th/95th percentile. Any value below the low percentile is set equal to the low percentile's value; any value above the high percentile is set equal to the high percentile's value. Everything in between is untouched.

With only 8 data points in our toy example, exact percentile math is not meaningful (you'd need hundreds of stocks for 1st/99th percentile to bite cleanly on one or two points). So for this illustration, we'll cap NVDA's value down to 25 — the illustrative "next most extreme reasonable value" — to show the *effect* of winsorization. In Project 1's actual implementation (P1-Build-2/3), the winsorization threshold will be computed properly as a real percentile across 100-500 stocks.

### 4.3 Worked example — winsorize, then re-run z-scoring

| Stock | Sector | Raw (%) | Winsorized (%) |
|---|---|---|---|
| AAPL | Tech | 18 | 18 |
| MSFT | Tech | 22 | 22 |
| NVDA | Tech | 95 | **25** (capped) |
| INTC | Tech | -5 | -5 |
| DUK | Utilities | 3 | 3 |
| SO | Utilities | 5 | 5 |
| AEP | Utilities | 2 | 2 |
| NEE | Utilities | 8 | 8 |

New mean: (18+22+25-5+3+5+2+8)/8 = 78/8 = 9.75
New standard deviation: ≈ 10.0

| Stock | Sector | Winsorized (%) | Deviation | z-score |
|---|---|---|---|---|
| AAPL | Tech | 18 | +8.25 | 0.825 |
| MSFT | Tech | 22 | +12.25 | 1.225 |
| NVDA | Tech | 25 | +15.25 | 1.525 |
| INTC | Tech | -5 | -14.75 | -1.475 |
| DUK | Utilities | 3 | -6.75 | -0.675 |
| SO | Utilities | 5 | -4.75 | -0.475 |
| AEP | Utilities | 2 | -7.75 | -0.775 |
| NEE | Utilities | 8 | -1.75 | -0.175 |

Compare the two z-score columns side by side:

| Stock | Z-score (no winsorization) | Z-score (winsorized) |
|---|---|---|
| AAPL | -0.017 | 0.825 |
| MSFT | 0.116 | 1.225 |
| NVDA | 2.546 | 1.525 |
| INTC | -0.782 | -1.475 |
| DUK | -0.516 | -0.675 |
| SO | -0.449 | -0.475 |
| AEP | -0.549 | -0.775 |
| NEE | -0.349 | -0.175 |

After winsorization, AAPL and MSFT — real, meaningful momentum differences — are properly differentiated (0.825 vs 1.225) instead of being crushed near zero. NVDA still ranks highest, as it should (it *is* the strongest momentum stock) — but it no longer swallows the entire scale.

**Order of operations matters:** winsorize the raw factor *first*, then compute the z-score on the cleaned data — not the reverse. If you z-score first and winsorize the z-scores afterward, you've already let the outlier distort your mean and standard deviation before you touch it, which defeats the purpose.

---

## 5. Sector Neutralization — the most important trap in this lesson

### 5.1 Why this exists — the motivating problem

Look again at the winsorized z-score table above. Notice a pattern: **every single Tech stock has a positive z-score, and every single Utilities stock has a negative z-score** (except NEE, which is close to zero).

Ask yourself: is this signal telling you "which stocks have the best momentum," or is it really just telling you "Tech had a good period and Utilities didn't"? If you built a portfolio going long the top z-scores and short the bottom z-scores, you would end up **long Tech, short Utilities** — a sector bet dressed up as a momentum strategy. That's Problem 3 from Section 2, and it's a real, common mistake in factor research: an "alpha" signal that is secretly just an unintentional sector or industry tilt.

This matters enormously for how the strategy would be evaluated. If Tech simply outperforms Utilities over your backtest period for reasons having nothing to do with momentum (interest rate environment, sector rotation, whatever), your backtest will look great — but you haven't actually found a momentum signal. You've found "own Tech." That's not a discovery; that's noise mistaken for skill.

### 5.2 The method — normalize within groups, not across the whole universe

**Sector neutralization** means computing the z-score *within* each sector separately, rather than across the entire universe at once. Instead of asking "how does this stock's momentum compare to every stock in my universe," you ask "how does this stock's momentum compare only to its direct sector peers." This isolates genuine stock-picking skill *within* a sector from a sector-level tilt.

### 5.3 Worked example — same data, sector-neutral z-scores

**Tech sector only** (AAPL, MSFT, NVDA, INTC — using winsorized values):

| Stock | Winsorized (%) | Deviation from Tech mean (15.0) | Sector z-score |
|---|---|---|---|
| AAPL | 18 | +3.0 | 0.254 |
| MSFT | 22 | +7.0 | 0.593 |
| NVDA | 25 | +10.0 | 0.847 |
| INTC | -5 | -20.0 | -1.694 |

(Tech standard deviation ≈ 11.81)

**Utilities sector only** (DUK, SO, AEP, NEE):

| Stock | Winsorized (%) | Deviation from Utilities mean (4.5) | Sector z-score |
|---|---|---|---|
| DUK | 3 | -1.5 | -0.655 |
| SO | 5 | +0.5 | 0.218 |
| AEP | 2 | -2.5 | -1.092 |
| NEE | 8 | +3.5 | **1.528** |

(Utilities standard deviation ≈ 2.29)

### 5.4 The payoff — compare universe-wide vs sector-neutral

| Stock | Sector | Universe-wide z-score | Sector-neutral z-score |
|---|---|---|---|
| AAPL | Tech | 0.825 | 0.254 |
| MSFT | Tech | 1.225 | 0.593 |
| NVDA | Tech | 1.525 | 0.847 |
| INTC | Tech | -1.475 | -1.694 |
| DUK | Utilities | -0.675 | -0.655 |
| SO | Utilities | -0.475 | 0.218 |
| AEP | Utilities | -0.775 | -1.092 |
| NEE | Utilities | -0.175 | **1.528** |

This is the entire point of the lesson, in one row: **NEE (a utility) goes from the *worst-ranked* stock in the universe-wide view (-0.175, near the bottom) to the *best-ranked* stock of all eight once you neutralize for sector (1.528, higher than every single Tech name).**

The universe-wide z-score was hiding NEE's genuinely strong relative momentum *within its own peer group* behind the fact that Utilities as a sector was weaker than Tech as a sector overall. Sector neutralization is what lets a momentum signal actually find "the best mover in each neighborhood" instead of just "which neighborhood had a better year."

---

## 6. Putting the full pipeline together

The signal construction pipeline, in order:

1. **Compute the raw factor** (e.g., 12-1 month momentum, using adjusted-close log returns per the P1-L3 convention)
2. **Winsorize** the raw factor cross-sectionally (cap extreme values at a percentile threshold — Project 1 default: 1st/99th percentile, configurable)
3. **Z-score within sector groups** (sector-neutral), not across the whole universe, as the default signal
4. (Optional, for comparison/diagnostics) Also compute the universe-wide z-score, to be able to show *how much* of a naive signal was actually a sector bet — useful for the methodology validator in P1-Build-8

This ordering — raw → winsorize → sector-neutral z-score — is the "signal" that P1-L5 (portfolio construction) will consume directly to build decile portfolios.

---

## 7. Summary table — concepts from this lesson

| Concept | What it is | Why it matters |
|---|---|---|
| Raw factor value | Literal computed number per stock, in native units | Not comparable across stocks or factor types directly |
| Signal | Normalized, cross-sectionally comparable version of a raw factor | What portfolio construction actually consumes |
| Cross-sectional | Comparing across stocks at one point in time (vs. time-series: one stock across time) | Signal construction is always cross-sectional |
| Standard deviation | Measure of typical spread/dispersion in a group of numbers | The "yardstick" a z-score measures distance in |
| Z-score | (value − mean) / standard deviation | Puts every factor on the same, comparable scale |
| Winsorization | Capping (not deleting) extreme values at a percentile threshold | Prevents one outlier from distorting the whole signal |
| Trimming (contrast) | Deleting outlier observations entirely | Different from winsorization — loses the stock, not just the extreme value |
| Sector neutralization | Z-scoring within sector groups instead of across the whole universe | Prevents a signal from secretly being a disguised sector bet |

---

## 8. Explain-it-back prompt (for reference)

*"Why can't I just rank stocks by raw P/E ratios? What does z-scoring give me?"* — the full answer: raw P/E ratios aren't comparable across different scales, get distorted by outliers, and can secretly encode sector membership rather than genuine relative value. Z-scoring (after winsorizing, and done within sector) fixes all three.

---

## What's next

**P1-L5: Portfolio construction from signals** picks up exactly where this lesson ends — taking the sector-neutral z-scores just built and turning them into decile/quintile portfolios (long-only vs. long-short), which is the next concrete step toward an actual backtest.
