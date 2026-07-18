# P1-L6: Information Coefficient and Statistical Evaluation

**Completed:** 2026-07-13
**Track:** Finance (Phase 1, Concept Lessons)

## Where this fits

You've now got a signal (sector-neutral z-score, P1-L4) and a way to turn it into a portfolio (quintile buckets, long-short, P1-L5). The question this lesson answers: **does any of this actually predict anything, or are you just building an elaborate machine that produces numbers with no relationship to future returns?**

That's what Information Coefficient (IC) and its companion metrics measure.

---

## Part 1: What does "predictive" actually mean here?

Every stock in your universe has, on a given date, a **signal value** — something you know *today* (the sector-neutral z-score). Some period later — a day, a week, a month — you observe what actually happened: the **forward return**, the return the stock earned *after* that date.

"Predictive" means: stocks with a higher signal value today tend to earn a higher forward return, and stocks with a lower signal value tend to earn a lower forward return — more often than you'd expect from pure chance.

This is a fundamentally different question from "did my portfolio make money this month" (that's one blended outcome). It's asking about the **relationship, stock by stock, at every rebalance date** between what the signal said and what actually happened next. That's what all five metrics in this lesson measure, from different angles.

---

## Part 2: The Information Coefficient (IC)

**Intuition.** Think of the IC as a report card for your signal's guessing ability. If you ranked 10 stocks by signal and then watched what they actually returned, the IC asks: how tightly do those two things move together? An IC of 1.0 means perfect prediction (the highest-signal stock always has the highest return, in exact proportion). An IC of 0 means no relationship at all — the signal tells you nothing. An IC of -1.0 means the signal is perfectly *backwards*.

Mechanically, IC is just the **Pearson correlation coefficient** (the standard "correlation" from basic statistics) computed between signal values and forward returns, across all stocks in the universe on a given date.

**Formula:**

IC = [ Σ(xᵢ − x̄)(yᵢ − ȳ) ] / [ √Σ(xᵢ − x̄)² × √Σ(yᵢ − ȳ)² ]

where xᵢ is stock i's signal, yᵢ is stock i's forward return, and x̄, ȳ are the averages.

**Worked example.** Ten stocks, sector-neutral z-score signal (from P1-L4/L5 style pipeline) and their next-period forward return:

| Stock | Signal (z) | Forward Return (%) |
|---|---|---|
| A | 2.1 | 8 |
| B | 1.5 | 5 |
| C | 1.0 | 6 |
| D | 0.6 | 2 |
| E | 0.2 | 3 |
| F | -0.1 | -1 |
| G | -0.5 | 1 |
| H | -0.9 | -3 |
| I | -1.4 | -4 |
| J | -2.0 | -6 |

Mean signal x̄ = 0.05. Mean return ȳ = 1.1%.

| Stock | xᵢ−x̄ | yᵢ−ȳ | product | (xᵢ−x̄)² | (yᵢ−ȳ)² |
|---|---|---|---|---|---|
| A | 2.05 | 6.9 | 14.145 | 4.2025 | 47.61 |
| B | 1.45 | 3.9 | 5.655 | 2.1025 | 15.21 |
| C | 0.95 | 4.9 | 4.655 | 0.9025 | 24.01 |
| D | 0.55 | 0.9 | 0.495 | 0.3025 | 0.81 |
| E | 0.15 | 1.9 | 0.285 | 0.0225 | 3.61 |
| F | -0.15 | -2.1 | 0.315 | 0.0225 | 4.41 |
| G | -0.55 | -0.1 | 0.055 | 0.3025 | 0.01 |
| H | -0.95 | -4.1 | 3.895 | 0.9025 | 16.81 |
| I | -1.45 | -5.1 | 7.395 | 2.1025 | 26.01 |
| J | -2.05 | -7.1 | 14.555 | 4.2025 | 50.41 |
| **Sum** | | | **51.45** | **15.065** | **188.9** |

IC = 51.45 / √(15.065 × 188.9) = 51.45 / √2845.78 = 51.45 / 53.35 = **0.9645**

**IC ≈ 0.96.** That's an extremely strong IC — because this is a clean, small, hand-built toy example with only one stock (G) breaking the pattern. **Real-world daily/monthly ICs are almost never this high.** In actual equity factor research, a daily IC of 0.02–0.05 is considered *good*, and anything above 0.10 is considered excellent and somewhat suspicious (worth double-checking for a bug or look-ahead bias). The reason: real markets are dominated by noise — earnings surprises, macro news, sector rotations — that has nothing to do with your factor. Don't be discouraged when your real backtest produces an IC of 0.03; that can still be a genuinely valuable, tradeable signal if it holds up consistently (Part 6).

**Does one stock "verify" the IC? What actually drove the 0.96?** A natural question when looking at this worked example: Stock A had the highest signal (2.1) *and* the highest forward return (8%) — is that single match what makes IC = 0.96?

**Answer: no. IC is not a single-stock verification — it's a summary statistic across the whole group at once.** It's not "did my top pick do best," it's "across everyone, did higher signal generally go with higher return, and lower signal with lower return, in a consistent pattern." Stock A matching is only one of many data points feeding the calculation, not proof of it on its own.

What actually drove the 0.96 is that **nine of the ten stocks** lined up in the expected direction:

| Stock | Signal | Return | Behaved as predicted? |
|---|---|---|---|
| A (highest signal) | 2.1 | 8% (highest) | Yes |
| B | 1.5 | 5% | Yes — positive signal, positive return |
| C | 1.0 | 6% | Yes — positive signal, positive return |
| D | 0.6 | 2% | Yes — positive signal, positive return |
| E | 0.2 | 3% | Yes — positive signal, positive return |
| F | -0.1 | -1% | Yes — negative signal, negative return |
| **G** | -0.5 | **+1%** | **No — negative signal, positive return** |
| H | -0.9 | -3% | Yes — negative signal, negative return |
| I | -1.4 | -4% | Yes — negative signal, negative return |
| J (lowest signal) | -2.0 | -6% (lowest) | Yes |

If A alone had matched and every other stock's return were random noise unrelated to its signal, IC would land close to zero — one lucky hit out of ten barely moves a correlation coefficient. IC = 0.96 instead reflects that **almost the entire ranking held together across all 10 stocks**, not just the top one. The single exception, G, is exactly why IC is 0.96 and not a perfect 1.0 — that one misfire is what pulls it down from a perfect score.

**Practical distinction:** if what you actually want to check is "did my top-ranked pick perform well," that's a different, narrower question than IC — closer to what hit rate or a top-bucket-only return check answers (P1-L5's quintile construction). IC is answering the broader "does the whole cross-sectional ranking hold up, on average, across every stock" question, not a single-stock verification.

---

## Part 3: Rank IC (Spearman rank correlation)

**Intuition.** IC (Pearson) cares about *exact magnitude* — it's sensitive to how big the numbers are, not just their order. Rank IC asks a simpler, more robust question: **forget the magnitudes — if I just rank the stocks by signal, and separately rank them by what they actually returned, do the two rankings agree?** It's like judging a horse race only by finish order, not by how many lengths each horse won by.

**Formula (Spearman's rho):**

ρ = 1 − [6 × Σdᵢ²] / [n(n²−1)]

where dᵢ = (rank of stock i by signal) − (rank of stock i by forward return), and n = number of stocks.

**Worked example**, same 10 stocks. Rank 1 = highest.

| Stock | Signal rank | Return rank | dᵢ | dᵢ² |
|---|---|---|---|---|
| A | 1 | 1 | 0 | 0 |
| B | 2 | 3 | -1 | 1 |
| C | 3 | 2 | 1 | 1 |
| D | 4 | 5 | -1 | 1 |
| E | 5 | 4 | 1 | 1 |
| F | 6 | 7 | -1 | 1 |
| G | 7 | 6 | 1 | 1 |
| H | 8 | 8 | 0 | 0 |
| I | 9 | 9 | 0 | 0 |
| J | 10 | 10 | 0 | 0 |
| **Sum** | | | | **6** |

ρ = 1 − (6×6)/(10×99) = 1 − 36/990 = 1 − 0.0364 = **0.9636**

**Rank IC ≈ 0.96**, very close to Pearson IC here — that's a coincidence of this particular dataset having no extreme outlier. Rank IC and Pearson IC diverge sharply once an outlier return shows up, which is the whole reason rank IC exists.

**Why rank IC matters more in practice — an outlier illustration.** Take 4 stocks with a clean, perfectly-ordered relationship:

| Stock | Signal | "Normal" Return | Signal Rank | Return Rank |
|---|---|---|---|---|
| A | 3 | 12% | 1 | 1 |
| B | 2 | 8% | 2 | 2 |
| C | 1 | 4% | 3 | 3 |
| D | 0 | 0% | 4 | 4 |

Perfect order → Pearson IC = 1.0, Rank IC = 1.0. Now suppose stock D — the *lowest*-signal stock, which should have the *worst* return — gets hit by a surprise takeover bid and its return spikes to +50%, completely unrelated to the factor:

| Stock | Signal | Return (with outlier) | Signal Rank | Return Rank |
|---|---|---|---|---|
| A | 3 | 12% | 1 | 2 |
| B | 2 | 8% | 2 | 3 |
| C | 1 | 4% | 3 | 4 |
| D | 0 | **50%** | 4 | **1** |

Computing both:

| Metric | Value | Why |
|---|---|---|
| Pearson IC | **-0.67** | The 50% return has huge *magnitude*, and it lands on the worst-signal stock, so it drags the whole sum-of-products calculation sharply negative |
| Rank IC | **-0.20** | D just moved from rank 4 to rank 1 — a full best-to-worst reversal. At only 4 stocks, that reversal is a large fraction of the whole sample, so rank IC takes real damage too — this is *not* a case where rank IC is unaffected. |

(Rank IC math for this 4-stock case: dᵢ values are A: 1-2=-1, B: 2-3=-1, C: 3-4=-1, D: 4-1=3. Σdᵢ² = 1+1+1+9 = 12. ρ = 1 − 6(12)/(4×15) = 1 − 72/60 = 1 − 1.2 = **-0.2**. Pearson calc: x̄=1.5, ȳ=18.5; deviations dx=(1.5,0.5,-0.5,-1.5), dy=(-6.5,-10.5,-14.5,31.5); Σdxdy = -9.75-5.25+7.25-47.25 = -55; Σdx²=5; Σdy²=1355; IC = -55/√(5×1355) = -55/82.31 = **-0.668**.)

**Correction — this move in rank IC is not small, and "robust" needs a precise meaning.** Rank IC dropping from 1.0 to -0.20 is a genuinely large move. "Robust" here doesn't mean "immune to disruption" — it means "less damaged than Pearson IC by the *same* event." That's a relative claim, and at n=4 the relative advantage is much smaller than it looks, because one full best-to-worst rank reversal is a huge fraction of a 4-stock sample.

There's a clean formula for exactly this scenario — one stock flipping from last place to first place, with everyone else shifting down by one rank to make room:

ρ = 1 − 6/(n+1)

| Universe size (n) | ρ after one full best↔worst flip |
|---|---|
| 4 (the example above) | 1 − 6/5 = **-0.20** |
| 10 | 1 − 6/11 = **0.45** |
| 100 (NASDAQ-100 scale) | 1 − 6/101 = **0.94** |
| 500 (S&P 500 scale) | 1 − 6/501 = **0.99** |

Same disruptive event — one stock's return completely unrelated to its signal, flipping it from worst to best — but the damage to rank IC shrinks fast as the universe grows. At n=4, one bad apple is 25% of the data, so of course it wrecks the correlation. At n=500 (Project 1's actual scale), that same single stock is 0.2% of the universe, and rank IC barely notices it.

Pearson IC doesn't get this same protection from scale. Its sensitivity comes from the *squared magnitude* of the outlier's deviation from the mean, and if one return is astronomically larger than everyone else's, that one squared term can still dominate the sum even sitting among hundreds of ordinary-sized numbers — more stocks doesn't reliably shrink Pearson IC's vulnerability to one huge number the way it shrinks rank IC's vulnerability to one misplaced rank.

**Corrected takeaway:** a single unrelated news event (M&A, earnings surprise) can swing the Pearson IC dramatically because Pearson IC is sensitive to the *size* of returns, and financial returns are famously "fat-tailed" (occasional huge moves). Rank IC only cares about *order*, so it dampens the influence of any one extreme observation — but that dampening effect is weak in small samples and only becomes strong at realistic universe sizes (100s of stocks). At toy scale (n=4), rank IC still takes a real hit, just usually a smaller one than Pearson IC. This is still why **rank IC (Spearman) is the industry-standard headline metric** for factor evaluation at real universe sizes — Pearson IC is retained as a diagnostic, but rank IC is what you'd lead with in a research memo.

---

## Part 4: Hit rate

**Intuition.** The simplest possible metric of all: forget magnitude, forget rank order — just ask, **"did I call the direction right?"** Like a coin-flip win/loss record. If your signal says a stock should go up, and it goes up (regardless of by how much), that's a win.

**Formula:**

Hit Rate = (# correct sign matches) / N

**Worked example**, original 10-stock table:

| Stock | Signal sign | Return sign | Match? |
|---|---|---|---|
| A | + | + | Yes |
| B | + | + | Yes |
| C | + | + | Yes |
| D | + | + | Yes |
| E | + | + | Yes |
| F | − | − | Yes |
| G | − | + | **No** |
| H | − | − | Yes |
| I | − | − | Yes |
| J | − | − | Yes |

Hit Rate = 9/10 = **90%**

**Caveat:** a coin flip gets you 50% by pure chance, so hit rate is always read relative to that 50% baseline, not against 0%. Hit rate is easy to explain to a non-technical stakeholder ("we called the direction right 9 times out of 10"), but it throws away a lot of information — it doesn't care how *big* the win or loss was, and it doesn't reward getting the relative *ranking* among winners right. Use it as a communication metric alongside IC, not as a replacement for it.

---

## Part 5: Is this IC real, or just noise? — The t-statistic

**Intuition.** With only 10 hand-picked stocks and a clean story, it's easy to convince yourself a relationship is real when it might just be luck. The t-statistic answers: *"if there were actually zero relationship between signal and return, how likely is it we'd see a correlation this strong purely by random chance?"* This is a **hypothesis test** — you're testing the "null hypothesis" that the true IC is zero.

**Getting the direction right — this is easy to misread.** A **higher** t-statistic means the relationship is **less likely to be a coincidence**, not more. Think of it as a signal-to-noise ratio: it's asking how big the correlation is *relative to how much random wobble you'd expect at this sample size purely from chance*. A low t-stat means the correlation you found is small relative to that expected noise — entirely plausible as pure luck, so you can't rule out coincidence. A high t-stat means the correlation towers over what randomness alone could produce — very unlikely to be coincidence, meaning good evidence of a real relationship. Concretely: IC = 0.05 at N = 500 gave t ≈ 1.12 (low → can't rule out coincidence); IC = 0.96 at N = 10 gave t ≈ 10.3 (high → very unlikely to be coincidence). **One-line rule: higher |t| = more confident the relationship is real, not more confident it's a coincidence.**

**Formula** (significance of a correlation coefficient):

t = [ IC × √(N−2) ] / √(1 − IC²)

with N−2 degrees of freedom. As a rule of thumb, with reasonably large samples, a t beyond roughly **±2.0** is considered statistically significant at the conventional 95% confidence level (the exact critical value depends on sample size and shrinks toward 1.96 as N grows large).

**Worked example 1 — our toy dataset:** IC = 0.9645, N = 10, degrees of freedom = 8.

t = (0.9645 × √8) / √(1 − 0.9645²) = (0.9645 × 2.828) / √0.0697 = 2.728 / 0.264 = **10.3**

t ≈ 10.3 — wildly significant. But remember, this toy example was built to be clean; it's not realistic.

**Worked example 2 — realistic institutional scale.** Suppose you get an IC of 0.05 on a single rebalance date (a genuinely *good* real-world IC), across a universe of 500 stocks (S&P 500-sized), so N = 500:

t = (0.05 × √498) / √(1 − 0.05²) = (0.05 × 22.32) / √0.9975 = 1.116 / 0.9987 = **1.12**

t ≈ 1.12 — **not statistically significant** by the usual ~2.0 threshold.

**This is the important, somewhat counterintuitive lesson:** a realistic, genuinely useful IC (0.05) measured on a *single day* is almost never statistically distinguishable from pure noise, no matter how large your universe is. One clean-looking day proves nothing. Real evidence that a signal works has to come from **consistency across many rebalance periods over time** — which is exactly what the next metric measures.

---

## Part 6: The Information Ratio (IR)

**Intuition.** Instead of asking "was today's IC good," IR asks: **"across many rebalance dates, is my average IC reliably positive, or does it whipsaw between great days and terrible days?"** Two signals can have the same *average* IC, but one is steady (small day-to-day swings) and one is streaky (huge swings, occasionally negative). The steady one is more trustworthy — and more likely to actually be skill rather than luck. This is the signal-quality equivalent of the Sharpe ratio (which measures consistency of portfolio *returns*; IR measures consistency of signal *predictive power*).

**Precisely what IR captures — it's a ratio, not raw volatility.** IR is not just "how volatile is the IC" — the standard deviation in the denominator does capture that volatility, but IR combines it with the mean IC in the numerator. It's a **signal-to-noise ratio for predictive skill over time**: two signals with identical IC volatility can have very different IRs if their average IC differs, and two signals with the same average IC can have very different IRs if one is far steadier than the other. High mean + low volatility = high IR; the volatility alone tells only half the story.

**Formula:**

IR = mean(IC₁, IC₂, ..., IC_T) / std(IC₁, IC₂, ..., IC_T)

across T time periods (e.g., monthly IC values over a year).

**Worked example.** Six months of hypothetical monthly ICs:

| Month | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| IC | 0.08 | 0.05 | -0.02 | 0.10 | 0.06 | 0.03 |

Mean IC = (0.08+0.05−0.02+0.10+0.06+0.03)/6 = 0.30/6 = **0.05**

Deviations from mean: 0.03, 0.00, −0.07, 0.05, 0.01, −0.02
Squared deviations: 0.0009, 0, 0.0049, 0.0025, 0.0001, 0.0004 → sum = 0.0088
Sample variance = 0.0088 / (6−1) = 0.00176
Sample std = √0.00176 = **0.0420**

IR = 0.05 / 0.0420 = **1.19**

**IR ≈ 1.19** — this would be considered a very strong IR. As a loose, commonly-cited rule of thumb from the institutional-factor-investing tradition (associated with Grinold & Kahn's *Active Portfolio Management*), monthly/annualized IRs in the range of roughly 0.3–1.0 are typically viewed as good-to-strong for a real signal; treat these as approximate industry convention rather than a hard, universally agreed threshold — different shops and time horizons use different benchmarks.

**How many periods (T) do you actually need before trusting an IR?** There's no single universal number, but three separate considerations govern it:

1. **Statistical trustworthiness of the IR estimate itself.** As Part 7 shows, t = IR × √T — with T=6, even a strong IR of 1.19 only produces t ≈ 2.9, barely over the significance threshold and easily inflated by a lucky short stretch. You need enough periods that the mean and std themselves aren't noisy estimates. Institutional practice generally wants **at least a few years of monthly data (roughly T = 36–60 months)**, often more, before placing real confidence in an IR.
2. **Covering multiple market regimes, not just enough data points.** This is a separate reason from pure sample-size statistics: a signal tested only over 6 calm bull-market months tells you nothing about how it behaves in a selloff, a rate-hiking cycle, or a sharp sector rotation. You want T large enough to span both up and down markets, not merely large enough for the math to work — an IR of 1.19 measured entirely within one uninterrupted bull run is less trustworthy than the same IR spanning varied regimes.
3. **Rebalance frequency changes what "T periods" means, and introduces a subtle trap.** Monthly rebalancing over 3 years gives T=36; daily rebalancing over 3 years gives T≈750 — far more data points, but daily forward-return windows often *overlap* (e.g., a 5-trading-day forward window means consecutive days share 4 of 5 days of underlying data), making those ICs statistically dependent rather than independent observations. This overlap inflates the effective T and can make an IR look more statistically solid than it really is. This connects directly to the forward-return-window decision deferred to **P1-L7**.

---

## Part 7: Tying it together — is the *average* IC statistically real?

Now that we have a time series of ICs, we can ask the practically important significance question: is the *mean* IC over time reliably different from zero, given how much it bounces around?

**Formula:**

t = IR × √T

**Worked example:** IR = 1.19, T = 6 months.

t = 1.19 × √6 = 1.19 × 2.449 = **2.92**

t ≈ 2.92 — technically above the ~2.0 significance threshold. **But** T=6 is a dangerously small sample to trust in practice — six data points can produce a flattering IR purely by luck. In real evaluation you'd want years of history (T = 36+ months, ideally much more) before placing real confidence in an IR estimate. This formula — not the single-cross-section t from Part 5 — is the one that actually matters for deciding whether a signal has real, durable skill.

---

## Part 8: Summary table — all five metrics

| Metric | What it measures | Formula | Value in this lesson | Robust to return outliers? | Needs multiple time periods? | Want high or low? |
|---|---|---|---|---|---|---|
| IC (Pearson) | Linear correlation between signal and forward return, on one date | Σ(x−x̄)(y−ȳ) / √(Σ(x−x̄)² Σ(y−ȳ)²) | 0.96 (toy example) | No — sensitive to magnitude | No (single cross-section) | **Higher (more positive) is better.** Closer to +1 = strong, reliable prediction. Near 0 = no relationship. Realistic values are 0.02–0.10; near 1.0 is suspiciously high. |
| Rank IC (Spearman) | Correlation between signal *rank* and return *rank*, on one date | 1 − 6Σdᵢ² / (n(n²−1)) | 0.96 (toy); -0.20 vs -0.67 in outlier example | **Yes** (more so at realistic scale) | No (single cross-section) | **Higher (more positive) is better** — same logic as IC, but this is the more trustworthy version to actually rely on. |
| Hit rate | % of stocks where signal direction matched return direction | correct sign matches / N | 90% | Partially (ignores magnitude entirely) | No (single cross-section) | **Higher is better**, but only meaningful relative to the 50% coin-flip baseline — 50% means no skill at all. |
| t-stat (single period) | Whether one day's IC is distinguishable from zero-skill | IC√(N−2) / √(1−IC²) | 10.3 (toy, N=10); 1.12 (realistic, N=500) | Inherits Pearson's sensitivity | No | **Higher \|t\|, in either direction, is better** — but this measures *confidence the IC is real*, not the quality of the signal itself. A t near 0 means "can't rule out coincidence." |
| Information Ratio (IR) | Consistency of IC skill across many periods | mean(IC over T) / std(IC over T) | 1.19 | Depends on which IC feeds it | **Yes** | **Higher is better** — a high, steady average IC beats a streaky one, even if both average out to the same mean. |
| t-stat (time-series mean IC) | Whether the *average* IC across history is real, not luck | IR × √T | 2.92 (T=6, too small to trust) | Depends on which IC feeds it | **Yes** | **Higher \|t\| is better** — same "confidence, not quality" caveat as the single-period t-stat above. |

---

## Part 9: Where this lands in Project 1

- **P1-Build-6 (Metrics calculation module)** will implement all five of these: IC and rank IC computed at every rebalance date, hit rate as a supporting metric, then IR and the time-series t-stat aggregated across the *entire* backtest history — not just reported for a single flattering period.
- **Forward return window** (should "forward return" mean 1-day, 1-week, or 1-month ahead?) is itself a real design decision, and it's tightly linked to how fast a signal's predictive power fades — that's exactly what **P1-L7 (factor decay and turnover)** covers next. Deferring the final choice to that lesson.
- **P1-Build-8 (Methodology validator)** should flag a specific failure mode this lesson surfaces directly: reporting only the single best-looking period's IC while ignoring the full time series is a form of cherry-picking, closely related to the multiple-testing/p-hacking problem in P1-LB3. The validator should require IR and the time-series t-stat, not just a headline IC, before treating a signal as validated.

## Part 10 (follow-up): How does IC relate to Beta?

A natural question once you've worked with Beta (stock sensitivity to market) elsewhere: is Pearson IC conceptually the same idea?

**Same family, different question.** Both Beta and Pearson IC are built from **covariance** — how much two things move together, in raw units. What differs is what you divide the covariance by.

| | Beta | IC (Pearson correlation) |
|---|---|---|
| Formula | Cov(stock, market) / Var(market) | Cov(signal, return) / [SD(signal) × SD(return)] |
| Question it answers | "For a 1% move in the market, how much does *this stock* move?" | "How tightly does my signal's ranking track what actually happened?" |
| Units | Has units — can be 0.3, 1.0, 2.5, negative, anything | Unitless, bounded strictly between -1 and +1 |
| What varies | One stock, tracked over **time**, against the market | Many stocks, on **one date**, signal vs. forward return |

**Sensitivity vs. tightness-of-fit.** Beta tells you *magnitude of response* — a stock with beta = 2.0 moves twice as hard as the market — but says nothing about how *reliably* it does so. You could have beta = 2.0 with a very sloppy, noisy relationship or beta = 2.0 with a very tight one; beta alone doesn't distinguish those. IC (correlation) tells you the opposite thing — how tight the relationship is — but says nothing about magnitude. If you wanted the beta-style "expected extra return per unit of z-score" answer for a signal, you'd run a regression of forward return on signal value and look at the **slope**; the correlation (IC) instead tells you how much scatter there is around that line — conceptually close to what R² (which is just IC squared, in a single-variable regression) tells you about a beta regression: how much of the stock's movement the market actually explains, versus idiosyncratic noise.

**Direction of variation — the other big difference.** Beta is a **time-series** exercise: one stock, many dates, against the market. IC is a **cross-sectional** exercise: many stocks, one date, signal vs. forward return. This is the same cross-sectional-vs-time-series distinction introduced in P1-L4, showing up again here.

**Summary:** same mathematical family (covariance-based), same general spirit ("do these two things move together"), but Beta measures *how hard* one thing responds to another over time, while IC measures *how reliably* one thing predicts another across a universe at a point in time.

## Carried-forward action items from this lesson

- **(P1-L6) → P1-L7 (factor decay/turnover):** Forward-return window choice (1-day, 1-week, 1-month) not yet decided — depends on signal decay speed, covered next lesson. Decision feeds directly into P1-Build-6 metrics module.
- **(P1-L6) → P1-Build-6 (metrics calculation):** Implement Pearson IC, rank IC (Spearman), hit rate at each rebalance date; implement IR and time-series t-stat aggregated across the full backtest window (not per-period, to avoid cherry-picking).
- **(P1-L6) → P1-Build-8 (methodology validator):** Flag reporting of a single best-period IC without accompanying IR/time-series t-stat as a p-hacking-adjacent red flag (ties to P1-LB3, multiple-testing problem).
- **(P1-L6) → open/shaky:** Formal significance testing for hit rate (e.g., a binomial test against the 50% chance baseline) was only touched informally in this lesson — revisit if a rigorous treatment is needed later.
- **(P1-L6) → P1-L7 (factor decay/turnover) / P1-Build-6 (metrics calculation):** Overlapping forward-return windows (e.g., daily rebalancing with a multi-day forward window) make consecutive-period ICs statistically dependent rather than independent, inflating the effective T used in IR and its time-series t-statistic. Needs an explicit handling decision (e.g., non-overlapping sampling, or an autocorrelation-adjusted standard error) once the forward-return window is chosen in P1-L7.
