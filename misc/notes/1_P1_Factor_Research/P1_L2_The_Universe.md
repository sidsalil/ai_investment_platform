# P1-L2: The Universe — what stocks am I testing on?

**Project:** Factor Research Copilot (Project 1)
**Phase:** Phase 1 — Concept Lessons (Lesson 2 of 10)
**Date:** 2026-05-25
**Estimated effort:** 1 hour
**Status:** Complete

---

## 1. What is a "universe" in quant research?

A **universe** is the set of securities that are eligible for your research or
strategy — the pool of candidates *before* you apply any signal, ranking, or
filter. It is the answer to: *"out of all the stocks in the world, which ones
am I even considering?"*

**Analogy from the PM world:** the universe is the **mandate**. A team that
runs "U.S. small-cap value" or "global ex-U.S. equity" is defining a universe.
Anything outside the mandate is off the desk's screen. Quant research is the
same, except you define the mandate in code, and the universe definition
becomes a piece of your methodology you have to defend in writing.

---

## 2. Why restrict the universe at all?

Four reasons, in rough order of importance:

### 2.1 Tradability

If your backtest universe includes a $30M-market-cap microcap that trades
$50,000 per day, any "alpha" you find on it is not capturable in real
trading. You cannot execute meaningful size without moving the price.
Portfolio Managers (PMs) at large asset managers would not have looked at
that stock; the research shouldn't either.

### 2.2 Data quality

Historical fundamentals, corporate actions, dividend adjustments, and split
adjustments are dramatically messier for small-cap, foreign, or thinly-traded
stocks. Bad data produces results that look real but are not. Restricting to
a high-quality subset reduces the data-quality variance in your inputs.

### 2.3 Hypothesis specificity

*"Momentum works"* is not a testable claim. *"12-month-minus-1-month momentum
generates positive Information Coefficient (IC) on U.S. large-cap equities
since 1990"* **is** testable. Without a defined universe, the hypothesis
doesn't really exist — it's vibes.

### 2.4 Computational cost

More stocks × more rebalance dates × more factors = slower iteration loops.
For a learning project, you want the iteration loop short so you can
experiment quickly. You can always expand the universe later.

---

## 3. The first big trap: survivorship bias

> Covered at intro level here. P1-L8 (the biases that kill backtests) goes
> deeper.

### 3.1 The setup

You download "the Standard & Poor's 500 (S&P 500)" from Wikipedia today. You
get ~500 tickers (technically 503 — a few companies like Alphabet and
Berkshire Hathaway have dual share classes counted separately). You pull 15
years of price data from yfinance for each. You run momentum. Great results.

### 3.2 The problem

The list you just downloaded contains **only companies that survived to
today as S&P 500 members.** It excludes:

| Removed for | Examples |
|---|---|
| Bankruptcy | Lehman Brothers, Washington Mutual, Bear Stearns |
| Accounting collapse | Enron, WorldCom |
| Mergers and Acquisitions (M&A) — acquired, delisted | Time Warner, Compaq, EMC |
| Fell out of index (shrank too much) | J.C. Penney, GE (during its long demotion) |

Every single stock in your dataset is, by definition, a stock that made it.
Your backtest is implicitly assuming you would have picked these winners 15
years ago. You wouldn't have.

### 3.3 The effect

**Returns are inflated. Risk is understated.** Academic studies on U.S.
equity mutual funds typically estimate survivorship bias inflates measured
annual returns by roughly **0.5–1.5% per year**. The effect is larger for
hedge fund universes and small-cap universes, sometimes substantially so.

### 3.4 The mental model

It's like backtesting a strategy called *"buy stocks I bought in 2010 that
did well."* Of course it works. You're peeking at the answer key.

---

## 4. The second trap: the universe changes over time (point-in-time universe)

Even if you somehow solved survivorship bias for *individual* stocks (e.g.,
by including delisted ones in your dataset), there's a second related
problem: **index membership changes over time.**

### 4.1 Concrete example

The S&P 500 today contains Tesla, Meta, and Nvidia at large weights. In
2005:
- Tesla was not yet a public company
- Meta (then Facebook) did not exist
- Nvidia was a fraction of its current size

The S&P 500 of 2005 had a different composition. The S&P 500 of 1995 was
different again.

### 4.2 What rigorous research needs

A rigorous backtest needs the answer to:

> *"What was the S&P 500 composition on March 31, 2010? On April 30, 2010?
> On every rebalance date in my test?"*

This is called **point-in-time** universe data — the actual index membership
*as it stood on each historical date*, not as it stands today.

### 4.3 Where to get it

| Provider | Notes |
|---|---|
| Center for Research in Security Prices (CRSP) — University of Chicago | Academic standard. Subscription required. |
| Bloomberg | Available via Bloomberg Terminal or Data License. Expensive. |
| S&P Dow Jones Indices | The index owner. Sells historical constituent data. |
| FactSet | Available via institutional subscription. |
| **yfinance** | **Does not provide point-in-time index membership.** |

This data exists but is expensive (academic CRSP access runs thousands per
year; commercial access higher). **Project 1 will not solve this problem
with free tools.** The right response is honesty in the methodology risk
memo, not pretending the bias isn't there.

---

## 5. Universe options for Project 1

| Option | Description | Pros | Cons |
|---|---|---|---|
| **A** | Current S&P 500 constituents (Wikipedia or equivalent free source) | ~500 liquid, well-data'd tickers. Standard learner choice. | Survivorship-biased. |
| **B** | A smaller subset — Dow 30 or NASDAQ-100 | Fast iteration. 30–100 tickers. | Smaller sample for statistical tests. Survivorship-biased. |
| **C** | Self-defined universe (e.g., "top 200 by market cap as of 2026-01-01") | Cleaner intellectually. | You're now responsible for defending the choice. |
| **D** | Paid point-in-time data provider | Right answer for production research. | Out of scope for P1 — cost. |

---

## 6. Decision for Project 1

**Universe: Option B (NASDAQ-100) for development → Option A (S&P 500) for the
final deliverable.**

### 6.1 Reasoning

- **NASDAQ-100 for development:** keeps the iteration loop tight while
  learning. Waiting four minutes for a 500-ticker yfinance bulk download on
  every tweak would destroy momentum during build sprints.
- **S&P 500 for the final eval and demo:** the standard learner deliverable;
  the deeper liquidity universe; the right size for the methodology to
  generalize.
- **Survivorship bias acknowledged openly in P1-Polish-4 (methodology risk
  memo).** Not hidden, not glossed. The senior move is to own the
  limitation, document its expected magnitude, and describe how it would be
  fixed with paid data.

### 6.2 Why this is more impressive than pretending to solve point-in-time

A hiring manager reviewing the project will respect:

> *"I used current S&P 500 constituents. The expected effect of survivorship
> bias on my measured returns is ~0.5–1.5% per year. In production, I'd
> source point-in-time membership from CRSP or FactSet, here's how I'd
> integrate it..."*

…much more than they will respect a backtest that quietly suffers the bias
and doesn't mention it. Honesty about limits is a senior-PM trait. It also
signals model-risk awareness — directly relevant to AI Product Manager
positioning.

---

## 7. Key terms

| Term | Definition |
|---|---|
| Universe | The set of securities eligible for inclusion in research or a strategy. |
| Mandate | The PM-world equivalent — the investment scope a team operates within. |
| Survivorship bias | Bias from analyzing only securities that survived to the analysis date; excludes failures, inflates measured returns. |
| Point-in-time data | Historical data reflecting *what was known* on each historical date — including which stocks were in an index *as of that date*. |
| Index constituency | The list of securities included in a given index at a given point in time. |
| Standard & Poor's 500 (S&P 500) | A market-cap-weighted index of ~500 large-cap U.S. stocks, curated by an S&P committee. |
| NASDAQ-100 | A market-cap-weighted index of the 100 largest non-financial NASDAQ-listed companies. |
| Dow Jones Industrial Average (Dow 30) | A price-weighted index of 30 large-cap U.S. stocks. |
| Center for Research in Security Prices (CRSP) | Research data center at the University of Chicago providing high-quality historical securities data, including point-in-time index constituency. |

---

## 8. Connections to other lessons

- **P1-L1 (What is a factor):** factors are tested *on* a universe. The
  universe definition is upstream of every factor calculation.
- **P1-L8 (The biases that kill backtests):** survivorship bias and
  point-in-time issues are revisited in depth, alongside look-ahead bias,
  selection bias, and multiple testing.
- **P1-Polish-4 (Methodology risk memo):** the survivorship-bias
  acknowledgment lives here as a documented limitation of the project.
- **P2 (Backtesting Copilot):** when the data source upgrades to Polygon.io,
  point-in-time index membership becomes a feature to revisit. Polygon's
  reference data includes historical ticker changes but membership lists
  still typically require a separate source.

---

## 9. What still feels shaky (to revisit in P1-L8)

- The exact mechanics of *how* to construct a survivorship-bias-free
  universe in practice (combining current + delisted tickers via a paid
  source).
- The precise statistical machinery for *quantifying* survivorship bias's
  effect on a specific backtest.
- How point-in-time fundamentals (not just membership) interact with
  point-in-time universe — e.g., restated earnings, late filings.

---

## 10. Action items emerging from this lesson

- [ ] Capture the universe decision (B → A) in CONTEXT.md under Project 1 →
      Decisions Made.
- [ ] Add "Universe choice and survivorship-bias acknowledgment" as a
      planned section in the methodology risk memo (P1-Polish-4).
- [ ] In P1-Build-1 (data ingestion module), parameterize the universe so
      switching NASDAQ-100 → S&P 500 is a config change, not a refactor.
- [ ] Source: scrape the current NASDAQ-100 and S&P 500 constituent lists
      from a stable public source (Wikipedia is the standard; freeze the
      snapshot date for reproducibility).

---

## 11. Lesson complete — proceed to P1-L3

Next lesson: **P1-L3: Returns — the foundation everything builds on.**
Concepts: simple vs log returns, when each is appropriate, adjusted vs raw
prices (dividends, splits), total return vs price return.
