# P1-L3: Returns — The Foundation Everything Builds On

**Date:** 2026-07-12
**Phase:** Project 1, Phase 1 (Concept Lessons), Lesson 3 of 10

Everything downstream in Project 1 — factors, signals, backtests, Sharpe ratios — is a function of how returns are calculated. Get this wrong and every later number is quietly wrong too.

---

## 1. Why we don't just use prices

A stock price by itself tells you almost nothing useful for research. Apple at $210 and Netflix at $650 aren't comparable — the scale is arbitrary (it depends on how many shares the company decided to split into). What you actually want to compare across stocks, time periods, and asset classes is **return** — the percentage change in value. Returns are unit-less, so a $10 stock and a $10,000 stock become comparable the moment you look at their returns instead of their prices.

## 2. Simple returns

The simple return over one period is:

```
R_t = (P_t - P_(t-1)) / P_(t-1)
```

Where P_t is the price today and P_(t-1) is the price yesterday. If a stock goes from $100 to $105, the simple return is 5%.

**Intuition:** this is "how much richer or poorer did I get, as a fraction of what I started with." It's the number a normal human means when they say "the stock is up 5% today."

**Key property — simple returns are additive across stocks, not across time.** If you hold a portfolio of two stocks, each 50% weighted, and one returns 10% and the other returns 4%, your portfolio's simple return is the weighted average: 7%. That works cleanly.

But simple returns do **not** chain additively over time. If a stock returns 10% in period 1 and then -10% in period 2, you might guess it's back to breakeven. It isn't:

```
$100 → $110 (up 10%) → $99 (down 10% of $110, i.e. -$11)
```

You're down 1%, not flat. This asymmetry — a loss requires a bigger subsequent gain to recover, and a gain can be wiped out by a smaller-looking subsequent loss — is a real, important property of compounding, not a math error. But it means you can't just add up daily simple returns to get a multi-day return. You have to multiply the growth factors:

```
Total growth = (1 + R_1) × (1 + R_2) × ... × (1 + R_n)
```

**Tying the formula to the numbers:** with R_1 = 10% and R_2 = -10%:

```
Total growth = (1 + 0.10) × (1 - 0.10)
             = 1.10 × 0.90
             = 0.99
```

A growth factor of 0.99 means you end up with 99% of your starting value — a **-1% total return**, which matches $100 → $110 → $99 exactly. Multiplying 1.10 × 0.90 does not give 1.00 because the -10% in period 2 applies to the larger $110 base, not the original $100. This is the mechanical reason the naive "+10% then -10% nets to zero" intuition fails.

## 3. Log returns

### 3.0 What a log return actually is

Before the formula: a **log return** is also called a **continuously compounded return**. Here's the intuition.

A simple return answers: "what fraction did the price change by, measured as one discrete jump from yesterday to today?" A log return answers a different question: "what constant, continuous growth rate — if compounded every instant, non-stop, throughout the period — would take yesterday's price to today's price?"

Think of the difference between simple interest and continuously compounded interest on a savings account. Simple return is like being told "your money grew by exactly X% at the end of the day, in one lump step." Log return is like imagining the growth happening smoothly and continuously the entire day, compounding on itself moment by moment, such that by day's end you've arrived at the same ending price — just via a smooth curve instead of one jump.

Mechanically, this "continuous compounding" question is answered using the natural logarithm (`ln`), which is the mathematical inverse of `e^x` (e ≈ 2.71828, the base of natural/continuous growth — the same constant that shows up in continuously compounded interest formulas). If price growth from P_(t-1) to P_t is expressed as a ratio P_t / P_(t-1), taking the natural log of that ratio converts "how many times bigger did the price get" into "what continuous growth rate produced that multiple." That's all a log return is: the natural log of the price ratio.

**A useful sanity check:** for small returns (a few percent or less), log returns and simple returns are nearly numerically identical — a stock up 2% has a simple return of 2.00% and a log return of about 1.98%. They only start diverging noticeably for large moves (the -10%/+10% example elsewhere in this lesson shows a meaningful gap). So for everyday small daily moves, don't expect log returns to look "different" from simple returns — the difference is in how they behave once you start chaining many of them together, not in their day-to-day size.

### 3.1 The formula

The log return is:

```
r_t = ln(P_t / P_(t-1))
```

Where `ln` is the natural logarithm. Using the same $100 → $110 → $99 example: ln(110/100) = 0.0953 (9.53%), then ln(99/110) = -0.1054 (-10.54%). Add those two log returns: 0.0953 + (-0.1054) = -0.0101, or about -1%. Take e^(-0.0101) and you get back to the correct -1% total change. **Log returns over multiple periods just add.** No multiplying growth factors, no compounding gymnastics — sum them and exponentiate once at the end.

This is the "mathematically nicer" property you'll hear quant people reference: log returns are **time-additive**. Simple returns are additive **across assets** (for portfolio weighting) but not **across time**; log returns are additive across time but not exactly across assets in a portfolio (portfolio log return isn't quite the weighted sum of constituent log returns — it's close for small returns, but breaks down more as returns get large).

There's a second reason log returns are preferred in research: they treat gains and losses symmetrically in a way that matches how compounding actually behaves, and they make a stock's return distribution better-behaved statistically (closer to symmetric, easier to model, less bounded by awkward constraints — a simple return can't go below -100%, but this asymmetry disappears in log-return space, which matters for the statistical tests you'll do in P1-L6 on Information Coefficient (IC)).

**When to use which:**
- **Log returns:** any time you're chaining returns over multiple periods, running statistical tests (t-stats, regressions), or doing anything where the math needs to behave nicely. This will be your default in Project 1's factor and backtest calculations.
- **Simple returns:** any time you're combining returns *across* multiple assets at a single point in time — e.g., "what's my portfolio's return this month given these weights and these constituent returns." Performance reporting to a portfolio manager or client also conventionally uses simple returns, because "the fund was up 8.3%" is what non-quant humans understand; nobody wants to hear "the fund's log return was 0.0797."

You'll use both in Project 1 — log returns internally for factor math, simple returns when generating the final memo language a portfolio manager reads.

## 4. Adjusted vs raw prices

Here's a trap that will quietly corrupt every return calculation if you don't handle it: raw prices from a data source don't just move because of market performance. They also jump for two mechanical, non-economic reasons.

**Stock splits.** If a company does a 2-for-1 split, each share is now worth half as much, but you own twice as many shares. Nothing economically changed — your total position value is identical before and after. But if you look at raw closing prices, you'll see the price cut in half overnight, which looks like a -50% return if you compute it naively. That's not a real loss; it's an artifact of share count changing.

**Dividends.** When a company pays a dividend, the stock price typically drops by roughly the dividend amount on the ex-dividend date (the company just paid cash out of itself, so it's worth a bit less), but you as a shareholder received that cash. If you only look at price and ignore the dividend you were paid, you'll understate your actual return.

**Adjusted prices** are prices that have been mathematically corrected for both effects — split-adjusted (retroactively rescaling all historical prices to reflect the current share count) and dividend-adjusted (adding back the value of dividends paid, so the adjusted price series reflects what your money actually did if dividends were reinvested). **Raw prices** are the actual historical trading prices, unadjusted, exactly as they printed on the tape each day.

**For Project 1: always use adjusted close prices for return calculations, never raw close.** yfinance gives you both — historically the `Adj Close` column (API details on exact column naming may have shifted; verify when you pull data in P1-Build-1). Raw close is useful only if you specifically need to know what the price actually was on a given day (e.g., for computing dollar transaction costs at the actual traded price), which is a P1-Build-5 concern, not a return-calculation concern.

### 4.1 Worked example — stock split

Company XYZ trades at **$200/share**. It announces a 2-for-1 split. After the split, you own twice as many shares, each worth half as much — your total position value is unchanged.

| | Raw Close | Adjusted Close |
|---|---|---|
| Day before split | $200 | $100 (retroactively halved) |
| Day of/after split | $100 | $100 |
| Naive return using raw close | (100 - 200)/200 = **-50%** ❌ | — |
| Return using adjusted close | — | (100 - 100)/100 = **0%** ✓ |

The raw close makes it look like you lost half your money overnight. Nothing economically happened — the adjustment retroactively rescales the *historical* pre-split prices (dividing them by 2) so the series is continuous and the return calculation correctly shows 0%.

### 4.2 Worked example — dividend

Company ABC trades at **$100/share** and pays a **$2 dividend**. On the ex-dividend date, the raw price typically drops by roughly the dividend amount, to $98 (the company just paid $2 of its own cash out).

| | Value |
|---|---|
| Price before ex-div date | $100 |
| Raw close on ex-div date | $98 |
| Dividend received (cash) | $2 |
| Naive return using raw close | (98 - 100)/100 = **-2%** ❌ |
| Actual investor outcome | $98 (share) + $2 (cash) = $100 → **0%** ✓ |

If you only look at raw price, it looks like you lost 2%. But you received that $2 in cash — your true economic position didn't change. Adjusted close builds this in by scaling the historical price series so that a return calculated directly off adjusted close already reflects the dividend, without you having to separately track cash payments received.

### 4.3 How far back does the adjustment reach — and does it ever stop?

This is a subtlety worth being explicit about, because it has real consequences for how you build the data ingestion layer in P1-Build-1.

**The adjustment is backward-looking, not forward-looking, and it is permanent.** Today's raw close and today's adjusted close are always the same number for today's date. The adjustment doesn't project a dividend or split forward into the future — it rescales the *entire past*. Every price before the ex-dividend date (or split date) gets multiplied by a scaling factor so the historical series lines up with today's price on a "what would this have been worth if I'd reinvested everything / if share count had always been today's share count" basis.

**Every historical price since the stock's very first recorded day gets touched, with no cutoff.** There is no window where old adjustments "expire" or get left alone. If a company IPO'd in 1990 and is still splitting and paying dividends today, every one of those corporate actions over 30+ years has left a multiplicative mark on the 1990 price, compounding all the way through to now.

**Splits compound.** Once a stock does a 2-for-1 split, every price before that date gets divided by 2, permanently (until a further split happens). A later 3-for-1 split divides everything before *that* date by 3 again — including prices that were already adjusted for the first split. The adjustment factors stack multiplicatively across a stock's whole history; they never reset.

**Dividends compound in exactly the same way, and the effect is much larger in practice because dividends happen far more often than splits.** Each ex-dividend date applies its own small downward scaling factor (roughly (1 - dividend/price)) to every price before that date. Nothing "wears off" after one payment — every subsequent dividend adds one more multiplicative layer on top of all the prior layers.

**A concrete illustration of scale:** a company paying **quarterly** dividends for **50 years** has made roughly 200 dividend payments (4/year × 50 years). Each one of those ~200 events compounds its own small adjustment factor into every price before it. So the adjusted close for that company's very first trading day today reflects all ~200 of those compounding factors (plus any splits on top). A useful mental model: think of it like coats of paint. Each dividend event doesn't just repaint the recent past — it adds one more coat over the *entire* history up to that point, including every previous coat. By year 50, the earliest prices carry 200+ layers of adjustment, individually small but cumulatively large. This is exactly why long-dividend-history stocks (utilities, consumer staples, Real Estate Investment Trusts (REITs) — think Coca-Cola, Procter & Gamble) often show a dramatic-looking gap between raw close and adjusted close way back in their price history. That's not a data error; it's 200+ compounding adjustments doing their job.

**Raw close, by contrast, never changes.** Raw close (sometimes just labeled "Close" in a data source, distinct from "Adj Close") is the actual price that printed on the tape that day, frozen forever. Pull AAPL's raw close for a date in 2015 today, or pull it again in 2030 — you get the identical number both times, because nothing about raw close gets revised by later corporate actions.

**Practical consequence — this is not a static, one-time calculation.** Because the adjusted series keeps getting rescaled every time a new split or dividend occurs, adjusted close is a *moving target*: pull the same historical date range from yfinance in January, then again in June, and you can get two different adjusted-close values for the exact same historical day — even though nothing about that specific day changed. What changed is everything that happened *after* it, which retroactively reshapes the adjustment factor applied to it.

**Design implication for P1-Build-1 (data ingestion / caching):** appending new rows to a cached raw-close series is safe — raw prices never get revised. But for adjusted close, a new corporate action (dividend or split) technically invalidates the *entire* previously cached historical series, not just the newest day — because the whole history needs to be re-scaled from today backward. Simply tacking on the newest date to a cached adjusted-close series will leave you with stale, mismatched historical values once any new corporate action occurs. The caching logic needs to treat "a new dividend/split was announced" as a trigger to re-pull and re-adjust the full history, not as a simple append.

## 5. Total return vs price return

**Price return** is the return from price appreciation alone — literally just (P_t - P_(t-1))/P_(t-1) using the raw or split-adjusted-but-not-dividend-adjusted price.

**Total return** is price return *plus* dividends reinvested. It's what an actual investor holding the stock and reinvesting every dividend actually earned.

Over short horizons for non-dividend-paying growth stocks, these two are nearly identical. Over long horizons, or for high-dividend sectors (utilities, Real Estate Investment Trusts (REITs), financials), the gap is enormous. A large fraction of the S&P 500's long-run historical return has come from reinvested dividends, not price appreciation alone. If you accidentally use price return where you meant total return, you will systematically understate performance, and it gets worse the longer your backtest window is.

**For Project 1: total return is the correct default for factor research and backtesting**, because you're trying to measure what an investor actually earned. This is exactly what dividend-adjusted close prices give you automatically — that's the whole point of the adjustment. So in practice: adjusted close → total return, raw close → price return. Pick adjusted close and you get total return "for free."

### 5.1 Worked example — price return vs total return

A stock starts the year at **$100** and ends the year at **$105**, having paid **$3** in dividends over the course of the year (assume not reinvested, for simplicity).

| | Calculation | Result |
|---|---|---|
| Price return only | (105 - 100)/100 | **5%** |
| Total return (price + dividends) | (105 - 100 + 3)/100 | **8%** |

If you used price return where you meant total return, you'd understate this stock's actual performance by 3 percentage points — in this example, from dividends alone. Over a multi-year backtest on a high-dividend universe (utilities, REITs, financials), that gap compounds year after year and can meaningfully distort every downstream number: Sharpe ratio, Information Coefficient (IC), decile spreads — all of it. This is exactly why adjusted close (which bakes dividends in) is the required default, not raw close.

## 6. How this connects back to P1-L2

Recall the survivorship bias and point-in-time universe issues from L2. There's a return-side analogue worth flagging now and revisiting properly in L8 (biases): if a stock gets delisted (bankruptcy, acquisition) mid-backtest, how your data source handles the "last price" matters enormously. Some data feeds just stop reporting the stock with no record of the wipeout; others record a proper -100% (or whatever recovery value there was) return on the delisting event. yfinance, being free retail data, does **not** reliably capture delisting returns — this is one of the "free tool" limitations you'll acknowledge honestly in the P1-Polish-4 risk memo, alongside survivorship bias itself.

## 7. Worked micro-example (by hand, no code)

Say a stock trades as follows over 3 days, adjusted close:

| Day | Adj Close |
|-----|-----------|
| 0   | $100.00 |
| 1   | $103.00 |
| 2   | $101.94 |

**Step 1 — daily returns:**

| Day | Simple Return | Log Return |
|---|---|---|
| Day 1 | (103 - 100)/100 = **3.00%** | ln(103/100) = **2.956%** |
| Day 2 | (101.94 - 103)/103 = **-1.03%** | ln(101.94/103) = **-1.036%** |

**Step 2 — combining into a 2-day return:**

| Method | Calculation | 2-Day Return | Correct? |
|---|---|---|---|
| Naive sum of simple returns | 3.00% + (-1.03%) | 1.97% | ❌ Wrong — simple returns don't add across time |
| Compounded simple returns (growth factors) | (1.03 × 0.9897) - 1 | ≈1.94% | ✓ Correct, but requires multiplication |
| Sum of log returns | 2.956% + (-1.036%) | 1.920% | ✓ Correct — just add, no extra step |
| Log return converted back to simple terms | e^0.01920 - 1 | ≈1.938% | ✓ Matches compounded simple return (rounding aside) |

**Takeaway:** log returns let you skip the compounding-factor multiplication and just sum, which is why every return series in your factor calculations (P1-Build-2 onward) will be built on log returns internally.

---

## Concepts I'm Still Shaky On
*(fill in if any apply after review)*

## Carried-Forward Action Items

- **(P1-L3) → P1-Build-1 (data ingestion module):** Confirm exact yfinance adjusted-close column name/behavior at time of implementation (API details may have shifted); ensure data ingestion pulls adjusted close, not raw close, as the default price series.
- **(P1-L3) → P1-Build-1 (data ingestion module):** Caching logic must account for the fact that adjusted close is a moving target — a new dividend or split invalidates the entire historical cached series for that ticker, not just the newest day. Raw close, by contrast, is safe to cache with simple row-append. Design cache invalidation accordingly (e.g., periodic full re-pull of adjusted series, or detect new corporate actions and trigger re-adjustment).
- **(P1-L3) → P1-Polish-4 (methodology risk memo):** Add explicit note that yfinance does not reliably capture delisting returns, alongside the existing survivorship bias disclosure. Full technical treatment deferred to P1-L8.

## Deliverable Status

- Notes: complete (this file)
- Small Jupyter notebook computing both return types on AAPL data: **not yet built** — per hard coding-ownership rule, this is written by Salil, not generated here. Suggested next step: pull AAPL adjusted close via yfinance, compute both simple and log daily returns over a short window, and verify by hand that log returns sum correctly across a multi-day window while simple returns require compounding.
