# P1-L8: The Biases That Kill Backtests

**Completed:** 2026-07-13
**Estimated time:** 2-3 hours
**Track:** Finance (Project 1: Factor Research Copilot)

> This lesson matters more than most. Everything in it compounds into how
> believable your entire Project 1 backtest is to a skeptical hiring
> manager. It also resolves three items explicitly deferred here from
> earlier lessons: survivorship bias construction mechanics (from P1-L2),
> the yfinance delisting-return limitation (from P1-L3), and the
> dollar-neutral vs. beta-neutral distinction (from P1-L5).

---

## 1. Look-ahead bias (deep dive)

**What it fundamentally is:** using information in a backtest simulation
that would not have actually existed yet, at the point in time the
backtest pretends a decision was being made.

**Analogy:** imagine a trader who gets to read tomorrow's Wall Street
Journal before placing today's trade. Every trade looks brilliant — not
because the trader is skilled, but because the "decision" was made with
information from the future. Look-ahead bias is exactly this, except it
usually creeps in through a data pipeline bug rather than anything a
researcher does on purpose.

This is the single most dangerous bias in quant research because it's
invisible in your code — the backtest runs, produces a beautiful equity
curve, and nothing throws an error. The strategy simply fails the moment
it goes live, because live trading can't cheat and look at the future.

### 1.1 Source 1: Fundamental data restatement / reporting lag

Companies report quarterly earnings **after** the quarter ends — usually
3-6 weeks later. A naive backtest that aligns a "Q1 ending March 31"
earnings number as being *known* on March 31 is wrong; it wasn't known
until the actual earnings release date (commonly early-to-mid May).

Worse: companies sometimes **restate** prior earnings due to accounting
corrections. If your data source only stores the *current, final* number
for "Q1 2024 EPS (Earnings Per Share)," and you use that final number as
if it were known back when Q1 2024 ended, you've smuggled in a correction
that wouldn't be published for months or years.

**Worked example:**

| Item | Value | Known as of |
|---|---|---|
| Quarter end date | March 31 | — |
| EPS originally reported (May 5 release) | $2.00 | May 5 |
| EPS after later restatement (accounting correction) | $1.80 | Filed 14 months later |
| P/E ratio using stock price $40 | | |
| — using originally-reported EPS ($2.00) | 20.0x | Correct point-in-time value |
| — using restated EPS ($1.80), naively dated March 31 | 22.2x | **Look-ahead — this number didn't exist yet** |

If your factor is "cheap stocks based on low P/E," using the restated
$1.80 figure changes which bucket this stock falls into on March 31 —
using information nobody had until 14 months later. A signal built this
way will look more predictive in backtest than it could possibly be live,
because it's quietly using a cleaned-up version of reality.

**P1 relevance:** Project 1's factors (momentum, volatility, liquidity,
possibly a value factor) draw primarily on price and volume data, which
is less exposed to this specific restatement problem than earnings-based
factors would be — but if a value factor (P1-Build-3) uses fundamentals,
this becomes directly relevant and must be handled by using an
announcement-date-aligned fundamentals source, not a quarter-end-aligned
one.

### 1.2 Source 2: Point-in-time index membership (revisited from P1-L2)

Already introduced in P1-L2 at the intro level. The deep-dive addition
here: this is a **look-ahead** bias, not just a survivorship bias — the
two are related but distinct. Using today's S&P 500 (Standard & Poor's
500) constituent list for a 2015 backtest doesn't just exclude companies
that failed (survivorship); it also *includes* companies that weren't yet
large/established enough to be in the index in 2015 (like Tesla, which
joined the S&P 500 in December 2020). A backtest that includes 2015-era
Tesla in a momentum universe is testing a stock that, in 2015, the market
didn't yet treat as an S&P 500-caliber name — that's a look-ahead leak
about which companies "made it."

### 1.3 Source 3: Sector classification changes

GICS (Global Industry Classification Standard) sectors get reclassified
periodically — companies move between sectors as their business models
shift (a well-known example: several large tech-platform companies were
moved from Information Technology into Communication Services in 2018).
If P1-Build-2/3's sector-neutral z-scoring uses **today's** GICS sector to
sector-neutralize a signal in a 2016 backtest, it's assuming a sector
assignment that didn't exist yet — a subtler version of the same
look-ahead pattern.

**P1 mitigation:** use point-in-time sector classification if the data
source supports it; if only current classification is available (likely,
given the free-tier tools in scope), disclose this as a limitation rather
than silently accepting it.

---

## 2. Survivorship bias (deep dive)

The intuition was covered in P1-L2. This section does the two things
deferred from there: **quantifying** the bias with real arithmetic, and
walking through **how** a survivorship-bias-free universe is actually
constructed.

### 2.1 Quantifying the magnitude

**Worked example:** a tiny 5-stock universe over one year.

| Stock | 1-year return | Status |
|---|---|---|
| A | +12% | Survived, still trades today |
| B | +8% | Survived, still trades today |
| C | +15% | Survived, still trades today |
| D | +5% | Survived, still trades today |
| E | **-100%** | Went bankrupt in month 6, delisted |

**Average return, all 5 stocks (what actually happened):**

(12% + 8% + 15% + 5% + (-100%)) / 5 = **-12%**

**Average return, survivors only (what a naive "today's tickers" backtest sees):**

(12% + 8% + 15% + 5%) / 4 = **+10%**

**Bias magnitude in this toy example: 22 percentage points.** This is
deliberately exaggerated (one stock going to zero in a 5-stock universe is
an extreme illustration) to make the mechanism obvious. In a real
100-500 stock universe over many years, the effect is far smaller per
year — which is where the earlier-cited real-world estimate of roughly
**0.5-1.5 percentage points per year** of inflation for US equity
universes comes from — but it compounds: over a 10-year backtest, even
0.75%/year compounds to a noticeably better-looking equity curve than
reality would have produced.

### 2.2 How a survivorship-bias-free universe is actually built (the mechanics)

This was flagged in P1-L2 as an area you were shaky on. Here's the real
answer:

1. **Get the delisted-security list.** Institutional-grade sources (CRSP
   — the Center for Research in Security Prices at the University of
   Chicago — or Bloomberg/FactSet) maintain a "delisting file" — every
   ticker that ever traded, with the date and *reason* it stopped trading
   (bankruptcy, acquisition, going private, exchange delisting for
   compliance failure, etc.).
2. **Assign a delisting return.** For an acquisition, the delisting
   return is usually well-defined (shareholders got cash or acquirer
   stock at a known price). For a bankruptcy, trading often halts before
   the stock formally hits zero, so CRSP applies a **standard assumed
   delisting-return convention** for stocks that vanish without a final
   observable trade price — commonly a roughly −30% haircut applied to
   the last traded price for certain delisting-reason codes, rather than
   either 0% (too generous) or −100% (sometimes too harsh, since some
   equity often does recover a few cents on the dollar in bankruptcy).
3. **Union the lists.** A true point-in-time universe at any historical
   date = (stocks trading that day that are still around today) **∪**
   (stocks trading that day that later delisted, each carrying its
   correct historical return up to its exit and then its delisting-return
   event).
4. **Reconstruct membership per rebalance date**, not just per stock —
   the S&P 500 (or NASDAQ-100) constituent list itself needs a historical
   snapshot for each specific rebalance date, which is a *separate* data
   product from the delisting file.

This is exactly why it's expensive: it's not one dataset, it's two
(point-in-time index membership + point-in-time delisting/return data),
maintained by a small number of paid vendors.

### 2.3 The yfinance delisting-return limitation (carried from P1-L3)

Practical consequence for Project 1: yfinance is built to serve
**currently-tradable** tickers. If you ask it for a delisted ticker, you
typically get an error or empty data — it has no mechanism for serving
"AAPL as of 2015, plus WaMu which delisted in 2008." This means:

- Any universe built by pulling "today's NASDAQ-100/S&P 500 list" from
  yfinance is **automatically survivorship-biased by construction** —
  there's no way around this without a paid data source.
- This is not a bug to fix; it's a documented limitation of the free
  tooling used for a learning project, and it belongs explicitly in the
  methodology risk memo (P1-Polish-4), alongside the general
  survivorship-bias disclosure already planned there.
- **Decision for Project 1:** disclosed as a known limitation, not
  solved. Optionally, if a clean illustrative example is easy to find
  (e.g., one NASDAQ-100 constituent removed for a known reason in recent
  years), it can be manually appended to the dev universe as a
  demonstration of understanding the mechanism — but this is a
  nice-to-have, not a requirement.

---

## 3. Selection bias

Survivorship bias is actually one specific *type* of a broader problem:
**selection bias** — any systematic, non-random choice in how you
assembled your data or your test that tilts the result, usually toward
the researcher's preferred conclusion, often without the researcher even
intending it.

### 3.1 Three forms relevant to Project 1

**Universe selection bias.** NASDAQ-100 is tech-heavy. If momentum
happened to perform unusually well in tech stocks over your specific
backtest window, testing momentum *only* on NASDAQ-100 will overstate how
well momentum works as a general phenomenon — you've selected a universe
that happens to flatter this specific factor.

**Time-period selection bias.** Choosing which years to backtest over is
itself a choice that can be selected (consciously or not) to flatter a
result.

**Worked example:**

| Backtest window | Market regime | Illustrative momentum Information Ratio (IR) |
|---|---|---|
| 2009 - 2021 | Long bull market, low-rate era | 0.9 (strong) |
| 2000 - 2002 | Dot-com crash | -0.3 (momentum famously crashed here) |
| 2007 - 2009 | Global Financial Crisis | -0.5 (momentum crashed again) |
| **Full period 2000 - 2021** | **Mixed** | **~0.3 (still positive, much weaker)** |

If a report only shows the 2009-2021 number, the reader walks away
thinking momentum is a much stronger, safer strategy than the full-history
evidence supports. This isn't fabrication — it's often just researchers
unconsciously gravitating toward the window that "worked" during
exploratory analysis, then reporting only that window as if it were the
plan all along.

**Factor selection bias (publication bias / the "factor zoo," tying back
to P1-L1).** Of the 400+ factors that have been published in academic
finance, most don't replicate under rigorous out-of-sample retesting.
This happens because journals (and researchers building a career) are far
more likely to publish "we found a new factor that predicts returns" than
"we tested this and it didn't work." So the pool of factors you'd find by
reading finance literature is *already* pre-filtered toward things that
happened to work in *someone's* specific historical sample — before
you've run a single line of your own code. This means even a completely
honest, single-test replication of a published factor is inheriting
selection bias from the literature it came from.

**Mitigation for Project 1:** the honest framing in your product brief
and case study is *"I am replicating well-established, heavily-retested
factors (momentum), not claiming factor discovery."* Momentum and value
are among the more robustly retested factors in the literature (unlike
many of the 400+ factor-zoo entries), which is exactly why they were
chosen for this project.

---

## 4. Data snooping

Easy to confuse with the multiple-testing / p-hacking problem coming up
in P1-LB3 — the line between them:

**Multiple testing (P1-LB3, not yet covered):** *you*, personally, test
several factor variants (12-month momentum, 6-month momentum, 3-month
momentum) and report only the one with the best backtest result. This is
something you do, and something you can control.

**Data snooping (this lesson):** a broader, structural problem — the
same historical dataset (e.g., US equity prices from roughly 1970-present)
has been reused by thousands of researchers over decades. Even if *you*
test exactly one factor exactly once, that factor's existence in the
literature already reflects an enormous amount of implicit "testing" —
every researcher who tried a factor idea on this same data and got a null
result simply didn't publish it. The dataset itself has been mined so
heavily by the broader research community that "it worked once on this
data" carries much weaker evidence than it would on a truly fresh
dataset.

**Analogy:** it's the equivalent of a large asset manager running the
same historical market data through hundreds of quant researchers' models
over 20 years. Even without any one researcher cherry-picking, the *pool*
of surviving ideas that reach a portfolio manager's desk is already
filtered by "did this look good on the data everyone shares."

**Why this matters for Project 1 specifically:** it's the reason the
methodology validator (P1-Build-8, the build sprint — not to be confused
with this lesson) and the honest framing in your polish materials should
distinguish "I found a signal that backtested well" from "I replicated a
well-known, independently-verified signal (momentum) using rigorous
methodology." The former is a much weaker evidentiary claim than it
sounds; the latter is exactly what your project should claim.

**Mitigation available to you (limited but real):** where possible,
evaluate a factor on a market or period that's *less* commonly snooped —
e.g., testing momentum out-of-sample on data from a period after the
original discovery paper, or on international markets — provides
slightly more independent evidence than yet another test on the same
well-trodden 1990s-2020s US large-cap sample. Not required for Project
1's scope, but worth a sentence in the risk memo as an acknowledged
limitation of "replicated on the same over-mined dataset as everyone
else."

---

## 5. Dollar-neutral vs. beta-neutral construction (carried from P1-L5, resolved here)

This was flagged as an open item in P1-L5: a long-short portfolio
balanced in *dollars* can still carry hidden market exposure if the long
and short buckets have systematically different average **betas**.

**What beta fundamentally is** (quick refresher, since it's central here):
beta measures how sensitive a stock's return is to the overall market's
return. A beta of 1.3 means "when the market moves 1%, this stock tends
to move about 1.3%" — more volatile/sensitive than the market. A beta of
0.9 means it tends to move less than the market.

**Why momentum portfolios are especially prone to this problem:**
momentum's top bucket (recent winners) tends to include high-beta,
high-momentum growth names that ran hard in a rally. The bottom bucket
(recent losers) tends to include lower-beta, beaten-down names. So a
"neutral" long-short momentum portfolio can accidentally be a leveraged
bet *on the market itself*, dressed up as a market-neutral factor
strategy.

### 5.1 Worked numerical example

| Bucket | Stocks | Individual betas | Average beta |
|---|---|---|---|
| Long (top quintile, momentum winners) | 2 stocks | 1.4, 1.2 | **1.30** |
| Short (bottom quintile, momentum losers) | 2 stocks | 1.0, 0.8 | **0.90** |

**Step 1 — Dollar-neutral construction (50% long, 50% short by dollars):**

Portfolio beta = (weight_long × avg beta_long) − (weight_short × avg beta_short)
= (0.50 × 1.30) − (0.50 × 0.90)
= 0.65 − 0.45
= **+0.20 net market beta**

Even though the portfolio is perfectly dollar-neutral (equal dollars long
and short), it still has a **+0.20 beta to the market**. If the market
rallies 10%, this portfolio would be expected to gain roughly +2% from
pure market exposure alone — a result that has nothing to do with whether
momentum "worked," but would show up in your P&L (profit and loss)
looking like factor skill.

**Step 2 — Beta-neutral construction (solving for the weights that cancel beta, not just dollars):**

We need: w_long × 1.30 = w_short × 0.90, with w_long + w_short = 1 (in
absolute terms, one side positive one negative).

Solving: w_long = 0.90 / (1.30 + 0.90) = 0.409 (40.9% long)
w_short = 1.30 / (1.30 + 0.90) = 0.591 (59.1% short)

**Check:** 0.409 × 1.30 = 0.532, and 0.591 × 0.90 = 0.532 — beta-weighted
exposures now match and cancel exactly.

| Construction | Long weight | Short weight | Dollar-neutral? | Beta-neutral? |
|---|---|---|---|---|
| Equal-dollar (P1-L5 default) | 50% | 50% | Yes | **No (+0.20 beta)** |
| Beta-matched | 40.9% | 59.1% | **No** | Yes |

This table is the whole point: **you generally can't have both
simultaneously** unless the two buckets happen to have equal average
betas. It's a genuine tradeoff, not a bug to "fix" — you have to choose
which kind of neutrality you're prioritizing.

### 5.2 Decision for Project 1

Given the scope and learning goals of Project 1, full beta-neutral
construction (which requires estimating rolling betas for every stock at
every rebalance date, then solving a weighting problem like the one
above) is **not implemented** — dollar-neutral equal-weighting (already
locked in P1-L5) remains the default. This is now an **explicitly
disclosed limitation**, not a silent gap: the methodology risk memo
(P1-Polish-4) will state that the long-short portfolio is dollar-neutral,
not beta-neutral, and that residual market beta was not measured or
hedged — a legitimate "what I'd build next" item for the case study
(P1-Polish-5).

---

## 6. Cheat sheet: the methodology gotchas summary

| Bias | Core mechanism | Project 1 mitigation | Residual risk (disclosed in memo) |
|---|---|---|---|
| **Look-ahead bias — restatement/reporting lag** | Using a corrected/future-known data value as if known historically | Momentum/volatility/liquidity factors use price/volume, largely avoiding this; value factor (if built) must align to announcement date, not quarter-end | If a value factor is added, fundamentals-restatement risk applies unless announcement-date alignment is verified |
| **Look-ahead bias — index membership** | Using today's constituent list for historical dates | Universe parameterized (NASDAQ-100 dev, S&P 500 final); acknowledged as not truly point-in-time | Full point-in-time membership requires paid data (CRSP/FactSet) — out of scope |
| **Look-ahead bias — sector reclassification** | Using today's GICS sector for historical sector-neutral z-scoring | Uses current GICS sector via yfinance/static mapping | Historical sector reclassifications not modeled |
| **Survivorship bias** | Backtesting only on stocks that still exist today | Acknowledged explicitly; NASDAQ-100/S&P 500 chosen with this in mind | ~0.5-1.5%/year inflation estimate (real-world convention); yfinance cannot serve delisted tickers |
| **Selection bias — universe** | Universe choice happens to flatter the tested factor | NASDAQ-100 (dev) vs. S&P 500 (final) noted as different universes with different sector composition | Tech-heavy NASDAQ-100 dev results may not generalize |
| **Selection bias — time period** | Backtest window happens to flatter the factor | Full available history used rather than a cherry-picked window | Still bounded by yfinance's available history depth |
| **Selection bias — factor/publication** | Published factors are pre-filtered toward "worked once" | Momentum/value chosen as heavily-retested, robust literature factors, not a novel discovery claim | Even robust factors carry residual literature-wide selection bias |
| **Data snooping** | Same historical dataset reused by the whole research community for decades | Framed honestly as replication, not discovery, in product brief/case study | No independent/fresh dataset used to re-validate |
| **Dollar-neutral ≠ beta-neutral** | Long/short buckets can have different average betas, leaving residual market exposure | Dollar-neutral equal-weighting used (P1-L5 default); beta-neutral not implemented | Residual market beta unmeasured and unhedged — flagged as future work |

---

## Summary of decisions and carried-forward items from this lesson

**Decisions locked:**
- Beta-neutral construction is explicitly out of scope for Project 1; dollar-neutral equal-weighting (P1-L5) remains the default, with the residual market-beta risk disclosed rather than solved.
- Survivorship bias and the yfinance delisting-return limitation are treated as documented, disclosed limitations of the free-tooling learning project — not solved.
- Factor and universe choices are framed honestly as replication of established, heavily-retested literature (not factor discovery), directly addressing publication/data-snooping bias.

**Carried forward:**
- → P1-Polish-4 (methodology risk memo): add explicit sections for look-ahead bias (restatement/reporting lag, index membership, sector reclassification), selection bias (universe and time-period choices), data snooping framing, and the dollar-neutral vs. beta-neutral disclosure with the worked-example numbers above.
- → P1-Build-3 (value factor, if built): fundamentals must be aligned to announcement date, not quarter-end date, to avoid restatement-driven look-ahead bias.
- → P1-Polish-5 (case-study one-pager): beta-neutral construction is a legitimate "what I'd build next" talking point.
- → P1-Build-8 (methodology validator, build sprint): validator should be able to flag a single-window backtest report (time-period selection bias) as a red flag, similar to the existing single-period-IC flag from P1-L6.
