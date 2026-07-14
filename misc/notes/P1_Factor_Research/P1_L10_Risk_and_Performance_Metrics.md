# P1-L10: Risk and Performance Metrics

**Completed:** 2026-07-14
**Track:** Finance (Phase 1, Concept Lessons) — final lesson in this track (10 of 10 complete)

This is the final lesson in the Finance track. Everything before this (Information Coefficient (IC), Information Ratio (IR), turnover, transaction costs) measured whether your **signal** works. This lesson measures whether the **portfolio built from that signal** is actually good — the metrics a portfolio manager or allocator would actually look at before writing a check.

---

## 1. Why we need risk-adjusted metrics at all

Here's the core problem: **raw return alone is a bad way to judge a strategy.**

Imagine two portfolios, both returning 12% over a year:

| Portfolio | Monthly returns (illustrative) | Annual return |
|---|---|---|
| A ("Steady") | +1%, +1.2%, +0.8%, +1.1%, +0.9%, +1%, +1%, +0.9%, +1.1%, +1%, +1%, +1% | ~12% |
| B ("Wild") | +8%, -6%, +9%, -4%, +7%, -3%, +6%, -2%, +5%, +1%, +1%, +1% | ~12% |

Same destination, wildly different rides. Portfolio B's 12% could easily have been -12% with slightly different luck — the return was earned by taking on a lot of risk, not by skill. Portfolio A's 12% came from a much more *repeatable*, *predictable* process.

**Analogy from your world:** this is the same reason a portfolio manager (PM) doesn't just look at "how much money did the fund make this year" — they look at it relative to how much risk was taken to get there. A PM who made 12% by placing one enormous concentrated bet that happened to work looks very different from a PM who made 12% through a diversified, disciplined process, even though the headline number is identical. Risk-adjusted metrics are how you tell those two apart mathematically.

Every metric in this lesson is a different way of asking: **"return relative to what kind of pain, measured how?"**

| Metric | What "pain" means | What it answers |
|---|---|---|
| Sharpe ratio | Total volatility (up and down) | Return per unit of overall bumpiness |
| Sortino ratio | Downside volatility only | Return per unit of bad bumpiness |
| Max drawdown | Worst peak-to-trough loss | How bad could it have gotten if you had the worst possible timing |
| Drawdown duration | Time spent underwater | How long would you have had to wait to get your money back |
| Calmar ratio | Max drawdown | Return per unit of worst-case pain |
| Beta-to-market | Market sensitivity | How much of your return is just "the market went up," not skill |

---

## 2. Sharpe Ratio

### Intuition
The Sharpe ratio asks: **for every unit of volatility (bumpiness) I tolerated, how much excess return did I earn?**

"Excess return" matters here — you should compare a risky strategy's return not to zero, but to what you could have earned completely risk-free (e.g., US Treasury bills). If T-bills pay 4% and your risky strategy returns 6%, you only *really* earned 2% of compensation for taking on risk. The **risk-free rate (rf)** is that baseline.

**Analogy:** it's like asking "how much extra salary am I getting paid for the extra stress of this job, per unit of stress?" If a new job pays $10K more but is twice as stressful, that's a worse deal per unit of stress than a job paying $5K more for the same increase in stress.

### Formula

Sharpe = (mean portfolio return − risk-free rate) / standard deviation of portfolio returns

Where:
- Mean portfolio return = average return over the period
- Risk-free rate = return over the same period from a risk-free asset (e.g., T-bills)
- Standard deviation of portfolio returns = the volatility/bumpiness measure over the period (same concept you used for z-scoring in P1-L4, just applied to a return time series instead of a cross-section of stocks)

### Worked example

Six months of portfolio returns, risk-free rate = 0.33%/month (≈4%/year):

| Month | Return | Return − Mean | (Return − Mean)² |
|---|---|---|---|
| 1 | 2.0% | 0.83% | 0.0069% |
| 2 | -1.0% | -2.17% | 0.0471% |
| 3 | 1.5% | 0.33% | 0.0011% |
| 4 | 3.0% | 1.83% | 0.0335% |
| 5 | -0.5% | -1.67% | 0.0279% |
| 6 | 2.0% | 0.83% | 0.0069% |

- Mean monthly return = (2.0 - 1.0 + 1.5 + 3.0 - 0.5 + 2.0) / 6 = **1.17%**
- Sum of squared deviations = 0.1234%
- Variance = 0.1234% / (6-1) = 0.0247% *(sample variance, dividing by n-1)*
- Standard deviation = √0.0247% ≈ **1.57%**
- Monthly Sharpe = (1.17% − 0.33%) / 1.57% ≈ **0.535**

### Annualizing

A monthly Sharpe isn't directly comparable to industry benchmarks, which are almost always quoted annualized. Because standard deviation scales with the square root of time (a statistical property — variance is additive across independent periods, so std dev scales by √n, not n), you annualize by multiplying by √12:

Annualized Sharpe = Monthly Sharpe × √12

Annualized Sharpe = 0.535 × √12 ≈ 0.535 × 3.464 ≈ **1.85**

**Rule-of-thumb interpretation (industry convention, not a hard law):**

| Annualized Sharpe | Interpretation |
|---|---|
| < 0 | Losing money relative to risk-free, don't bother |
| 0 – 0.5 | Weak |
| 0.5 – 1.0 | Acceptable |
| 1.0 – 2.0 | Good to very good |
| > 2.0 | Excellent — and worth double-checking for bugs or overfitting, same caution as unusually high IC from P1-L6 |

**Connection to P1-L6:** notice the structural resemblance — Sharpe is "(signal − baseline) / dispersion," exactly the same shape as a z-score (P1-L4) and conceptually the same shape as Information Ratio (P1-L6, which was mean IC / std of IC). This is a recurring pattern in quantitative finance: **signal-to-noise ratios show up everywhere**, just applied to different objects (stock values, IC across time, returns across time).

---

## 3. Sortino Ratio

### Intuition
Sharpe's flaw: standard deviation penalizes *upside* volatility exactly as much as downside volatility. But no investor complains about a return stream that occasionally jumps up a lot — that's not the "risk" anyone cares about. Sortino ratio fixes this by only counting *downside* deviations in the denominator.

**Analogy:** imagine judging a sales rep's consistency by penalizing them equally for an unexpectedly *huge* month and an unexpectedly *terrible* month. That's clearly wrong — you only actually care about the bad surprises. Sortino applies that same logic to returns.

### Formula

Sortino = (mean portfolio return − minimum acceptable return) / downside deviation

Where:
- Minimum acceptable return (MAR) = a threshold below which a return counts as "bad" (often 0%, or the risk-free rate — a threshold choice, not a universal constant)
- Downside deviation = only look at returns that fall below the MAR, square those shortfalls, average them (typically over *all* periods, not just the down ones — dividing by total N), and take the square root

Downside deviation = sqrt[ (1/N) × Σ (shortfall below MAR)² for all returns below MAR ]

### Worked example

Same six months of returns, MAR = 0% (simplest common choice):

| Month | Return | Below MAR (0%)? | Shortfall² |
|---|---|---|---|
| 1 | 2.0% | No | — (treated as 0 in the sum) |
| 2 | -1.0% | Yes | 0.0100% |
| 3 | 1.5% | No | — |
| 4 | 3.0% | No | — |
| 5 | -0.5% | Yes | 0.0025% |
| 6 | 2.0% | No | — |

- Sum of downside shortfalls² = 0.0125%
- Downside variance = 0.0125% / 6 = 0.00208%
- Downside deviation = √0.00208% ≈ **0.456%**
- Mean return (from before) = 1.17%, MAR = 0%
- Monthly Sortino = (1.17% − 0%) / 0.456% ≈ **2.57**
- Annualized Sortino = 2.57 × √12 ≈ **8.89**

**Compare:** Sortino (8.89 annualized) is dramatically higher than Sharpe (1.85 annualized) for the *same* return stream. That's expected and correct — this portfolio's volatility was mostly *upside* (the big +2%, +3% months), which Sharpe punished but Sortino doesn't. This is exactly why Sortino is often reported alongside Sharpe: **a large gap between the two tells you whether a strategy's volatility is "good" (upside) or "bad" (downside) in character**, information Sharpe alone hides.

---

## 4. Maximum Drawdown

### Intuition
Max drawdown answers a very human, very practical question: **"If I had the worst possible luck and invested right at the peak, how much of my money would I have watched disappear before things turned around?"**

This is arguably the single number that best predicts whether a real investor would panic and pull out. Sharpe and Sortino are statistical summaries; drawdown is the *lived experience* of holding the strategy through its worst stretch.

**Analogy:** Sharpe ratio is like a car's average fuel efficiency rating. Max drawdown is like asking "what's the steepest hill this car has ever had to climb, and how much did the engine strain?" You want to know both — how it performs on average, and how bad the worst moment gets.

### Formula

For a cumulative equity curve (portfolio value over time), at each point in time:

Drawdown at time t = (Value at t − Running Peak at t) / Running Peak at t

Where Running Peak at t = the highest portfolio value reached at any point up to and including time t.

Max Drawdown = the most negative drawdown value across the whole history (the deepest hole)

### Worked example

Portfolio value starting at $100, monthly:

| Month | Value | Running Peak | Drawdown |
|---|---|---|---|
| 0 | $100.00 | $100.00 | 0.0% |
| 1 | $108.00 | $108.00 | 0.0% |
| 2 | $103.00 | $108.00 | (103−108)/108 = **−4.63%** |
| 3 | $95.00 | $108.00 | (95−108)/108 = **−12.04%** |
| 4 | $90.00 | $108.00 | (90−108)/108 = **−16.67%** ← deepest point |
| 5 | $97.00 | $108.00 | (97−108)/108 = −10.19% |
| 6 | $105.00 | $108.00 | (105−108)/108 = −2.78% |
| 7 | $112.00 | $112.00 (new peak) | 0.0% |

**Max drawdown = −16.67%**, occurring at month 4, measured against the peak set at month 1.

Notice the mechanic: the "peak" resets upward every time a new high is hit (month 1 → month 7), but it never resets downward — it's a running maximum, so it only ever holds steady or increases. Every month's drawdown is measured against the *highest point seen so far*, not against the starting value or the previous month.

---

## 5. Drawdown Duration

### Intuition
Max drawdown tells you *how deep* the hole was. Drawdown duration tells you *how long you were stuck in it* — from the moment the portfolio fell off its peak until the moment it climbed back to a new all-time high. This matters because two portfolios can have identical max drawdowns but very different "time spent suffering," and investors care a lot about the second thing — a fund that takes 18 months to recover is a much harder sell than one that recovers in 2.

**Analogy:** if two flights both hit the same turbulence (same max drawdown), but one clears it in 5 minutes and the other stays bumpy for 3 hours, passengers remember those very differently — even though the worst single jolt was identical.

### Definition

Using the same equity curve from above:

| Phase | Months | Length |
|---|---|---|
| Decline (peak → trough) | Month 1 ($108) → Month 4 ($90) | 3 months |
| Recovery (trough → new peak) | Month 4 ($90) → Month 7 ($112, new high) | 3 months |
| **Total drawdown duration (peak → new peak)** | Month 1 → Month 7 | **6 months** |

The portfolio was "underwater" (below its previous all-time high) for 6 consecutive months, even though the deepest point of pain (−16.67%) only lasted an instant at month 4. This total figure — peak-to-new-peak — is what's usually reported as "drawdown duration" or "time underwater."

**Why this matters beyond the single worst drawdown:** a full backtest typically has *many* drawdowns of varying depth and length, not just one. In practice you'd compute this for every peak-to-new-peak cycle across the whole backtest and report both the single worst (max drawdown, longest duration) and the *average* drawdown duration — the average tells you what a "typical" bad stretch looks like, not just the single worst-case tail event.

---

## 6. Calmar Ratio

### Intuition
Calmar ratio is Sharpe ratio's cousin, but instead of dividing by *volatility*, it divides by *max drawdown*. It answers: **"how much annualized return am I earning per unit of worst-case pain I'd have to survive?"**

This matters because Sharpe can look great even for a strategy with one catastrophic drawdown buried in an otherwise smooth history — Sharpe uses *average* volatility across the whole period, which can dilute a single severe event. Calmar specifically targets the worst single event, which is exactly the thing that gets a PM fired or an investor to redeem.

### Formula

Calmar = Annualized Return / |Max Drawdown|

(Absolute value in the denominator, since max drawdown is a negative number and you want a positive ratio.)

### Worked example

Using an illustrative annualized return of 15% and the max drawdown computed above (−16.67%):

Calmar = 15% / 16.67% ≈ **0.90**

**Interpretation convention (industry rule-of-thumb, not universal):**

| Calmar Ratio | Interpretation |
|---|---|
| < 0.5 | Weak — drawdown risk is large relative to what you're earning |
| 0.5 – 1.0 | Acceptable |
| 1.0 – 3.0 | Good to very good |
| > 3.0 | Excellent (and, as with Sharpe/IC, worth scrutinizing for a short or lucky backtest window) |

**Why report Calmar alongside Sharpe, not instead of it:** Sharpe captures *typical* bumpiness; Calmar captures the *worst single episode*. A strategy could have a mediocre Sharpe (choppy day-to-day) but a strong Calmar (never actually suffered a severe multi-month collapse) — or the reverse (smooth most of the time, but one brutal tail event). Reporting both gives a fuller risk picture than either alone, which connects directly to the multiple-testing/cherry-picking caution from P1-L6 and P1-L8: reporting only the flattering metric is a red flag the methodology validator (P1-Build-8) should watch for.

---

## 7. Beta-to-Market

### Intuition
This connects directly back to two things you already know: the factor model from **P1-L1** (return = exposure × factor return + idiosyncratic) and the dollar-neutral vs. beta-neutral discussion from **P1-L8**, where you used *assumed* beta values (1.30 and 0.90) in a worked example without yet knowing how those numbers actually get calculated. This lesson closes that loop.

**Beta** measures how sensitive a portfolio's returns are to the overall market's returns. A beta of 1.0 means the portfolio tends to move exactly in line with the market. A beta of 2.0 means it tends to move twice as much (both up and down) as the market. A beta of 0.0 means its returns are statistically unrelated to the market's moves at all — which, for a long-short factor portfolio, is exactly the goal (per P1-L5's reasoning for why long-short isolates the "pure" factor effect).

**Analogy:** think of beta as a "sensitivity dial." A high-beta stock is like a speedboat — it reacts fast and dramatically to every wave (market move). A low-beta stock is like a barge — it barely notices the same wave. Beta measures how tightly coupled your portfolio's motion is to the ocean's motion (the market), separate from how big or small the waves themselves are.

### Formula

Beta is the slope of a linear regression of portfolio returns against market returns — mechanically, the same "line of best fit" concept from basic statistics:

Beta = Covariance(Portfolio Return, Market Return) / Variance(Market Return)

Where:
- Covariance(Portfolio, Market) = a measure of how much two things move *together*. Positive covariance = they tend to move in the same direction; negative = opposite directions; near-zero = no consistent relationship.
- Variance(Market) = the market's own bumpiness, squared (same variance concept from the Sharpe ratio calculation above, just applied to the market's return series instead of the portfolio's)

### Worked example

Five months of paired portfolio and market returns:

| Month | Portfolio Return | Market Return | Portfolio dev. from mean | Market dev. from mean | Product |
|---|---|---|---|---|---|
| 1 | 3.0% | 2.0% | 1.0% | 0.6% | 0.0060% |
| 2 | -1.0% | -0.5% | -3.0% | -1.9% | 0.0570% |
| 3 | 4.0% | 2.5% | 2.0% | 1.1% | 0.0220% |
| 4 | 0.0% | 1.0% | -2.0% | -0.4% | 0.0080% |
| 5 | 4.0% | 2.0% | 2.0% | 0.6% | 0.0120% |

- Mean portfolio return = (3.0 − 1.0 + 4.0 + 0.0 + 4.0)/5 = **2.0%**
- Mean market return = (2.0 − 0.5 + 2.5 + 1.0 + 2.0)/5 = **1.4%**
- Sum of products (for covariance) = 0.0060 + 0.0570 + 0.0220 + 0.0080 + 0.0120 = 0.1050%
- Covariance = 0.1050% / (5−1) = **0.02625%** *(sample covariance, dividing by n−1)*

Now variance of the market returns:

| Month | Market dev. from mean | Squared |
|---|---|---|
| 1 | 0.6% | 0.0036% |
| 2 | -1.9% | 0.0361% |
| 3 | 1.1% | 0.0121% |
| 4 | -0.4% | 0.0016% |
| 5 | 0.6% | 0.0036% |

- Sum of squares = 0.0570%
- Variance = 0.0570% / (5−1) = **0.01425%**

Beta = 0.02625% / 0.01425% ≈ **1.84**

**Interpretation:** this portfolio has a beta of ~1.84 — it moves roughly 1.84x as much as the market, in the same direction. This is a *high-beta* portfolio. If you were building a long-short factor portfolio and got this result, it would be a warning sign: per P1-L8, the whole point of long-short construction is to cancel out market exposure and isolate the factor effect. A long-short book with beta ≈ 1.84 has failed to do that — it's really more of a leveraged market bet than a factor-pure signal, and this is precisely the kind of check the methodology validator (P1-Build-8) should run.

**Direct link to P1-L8:** in that lesson, you used *assumed* long-bucket beta (1.30) and short-bucket beta (0.90) to show that a dollar-neutral book still carried +0.20 net beta. This lesson shows you how those per-bucket betas actually get estimated in the first place — you'd run this exact regression separately for the long bucket's returns vs. the market, and for the short bucket's returns vs. the market, then combine per the dollar-neutral or beta-neutral weighting math already locked in P1-L8.

---

## 8. Full metrics glossary for Project 1

| Metric | Formula (plain terms) | What it measures | Project 1 role | Desired Direction |
|---|---|---|---|---|
| Sharpe Ratio | (mean return − risk-free rate) / std dev of returns | Return per unit of total volatility | Primary risk-adjusted return metric, reported annualized | As high as possible |
| Sortino Ratio | (mean return − MAR) / downside deviation | Return per unit of downside-only volatility | Secondary metric; large Sharpe/Sortino gap flags whether volatility is upside- or downside-heavy | As high as possible |
| Max Drawdown | Most negative (value − running peak)/running peak across history | Worst peak-to-trough loss | Headline "worst case" risk number for the memo | As small in magnitude as possible (closer to zero) |
| Drawdown Duration | Time from peak → trough → new peak | How long a drawdown lasted, and how long recovery took | Reported alongside max drawdown; average duration across all drawdowns also useful | As low as possible (shorter is better) |
| Calmar Ratio | Annualized Return / |Max Drawdown| | Return per unit of worst-case pain | Catches strategies that look good on Sharpe but hide one severe drawdown | As high as possible |
| Beta-to-Market | Covariance(portfolio, market) / Variance(market) | Sensitivity of portfolio returns to market returns | Validates that long-short construction actually achieved low market exposure (ties to P1-L8) | As close to zero as possible (not "low" — a strongly negative beta is just as much a red flag as a strongly positive one, for a long-short book whose goal is market-exposure cancellation) |

**Note on the "Desired Direction" column:** Sharpe, Sortino, and Calmar behave conventionally — higher is unambiguously better. Max drawdown and drawdown duration also behave conventionally — smaller/shorter is unambiguously better. Beta-to-market is qualitatively different: it isn't a "more is better" or "less is better" metric at all, it's a "closer to a target value (zero) is better" metric. This distinction matters for P1-Build-8 (methodology validator): the validator logic for beta-to-market should flag deviation from zero in either direction, not just flag "high" values the way it would for the other five.

---

## 9. Carried-forward items surfaced by this lesson

- **P1-Build-6 (metrics calculation module):** Implement Sharpe (annualized via ×√12 for monthly data), Sortino (with MAR configurable, default 0%), max drawdown, drawdown duration (both single-worst and average across all drawdown cycles in the backtest), Calmar, and beta-to-market (computed via covariance/variance regression against a market benchmark return series).
- **P1-Build-6:** Beta-to-market should be computed both for the overall long-short portfolio (should be near zero, validating the dollar-neutral construction's effectiveness) and separately for the long and short legs (feeding the same dollar-neutral vs. beta-neutral analysis locked in P1-L8).
- **P1-Build-8 (methodology validator):** Flag a reported Sharpe ratio without an accompanying max drawdown / Calmar ratio as an incomplete risk picture — same "don't report only the flattering metric" principle already applied to single-period IC (P1-L6) and single-window backtests (P1-L8).
- **P1-Polish-4 (methodology risk memo) / metrics glossary deliverable:** This lesson's Section 8 table is the direct source material for the "metrics glossary for your repo" deliverable specified in the curriculum.
- **Open question for P1-Build-6:** need to decide what market benchmark series to use for beta-to-market calculation (e.g., S&P 500 index return via yfinance ^GSPC, or an equal-weighted return of the NASDAQ-100/S&P 500 universe itself). Not resolved in this lesson — revisit at build time.

---

## 10. What's still ahead for Project 1

This closes out the **Finance track** (10 of 10 complete). Three tracks remain before Phase 2 (Architecture):

- **AI/Agentic track** (0 of 14) — recommend starting immediately with P1-LA1, since this track is now maximally behind the Finance track
- **Backtesting Rigor track** (0 of 3)
- **Evals track** (0 of 1)

All four tracks must be checked off before Phase 2 (Architecture & Design) begins.
