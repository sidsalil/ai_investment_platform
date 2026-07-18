# P1-L9: Transaction Costs and Real-World Frictions

**Completed:** 2026-07-14

---

## 1. Why this lesson matters — the paper-to-live gap

Every backtest number computed so far (Information Coefficient (IC) in P1-L6, decay/turnover in P1-L7) assumes trades happen for free, instantly, at whatever price the data shows. That's never true. The gap between what a backtest reports and what a live portfolio actually earns is called **implementation shortfall** — and transaction costs are the single biggest driver of it.

Analogy: this is the same gap between a trade a portfolio manager (PM) *wants* to do at the price on their screen, and the price the trading desk actually gets filled at once the order hits the market.

Three cost sources, in order of size for a typical institutional equity trade:
1. **Bid-ask spread** — the toll for crossing from buyer's price to seller's price
2. **Market impact** — the price concession needed to get your size filled
3. **Commissions** — the explicit fee paid to broker/exchange

Then a look at costs a backtest *can't* model at all — the true backtest-vs-live gap.

---

## 2. Bid-ask spread

**What it fundamentally is:** at any moment, a stock has two prices, not one. The **bid** is the highest price someone is currently willing to *pay* to buy it. The **ask** (or offer) is the lowest price someone is currently willing to *accept* to sell it. The ask is always higher than the bid — that gap is the market maker's/liquidity provider's compensation for standing ready to trade with you instantly.

Analogy: a currency exchange kiosk buys your dollars at one rate and sells you dollars at a slightly worse rate. You never trade at the "true" price — you always cross a small toll in whichever direction you trade.

**The mechanic that costs you money:** a backtest presumably uses one price per stock per day (the close, per the P1-L3 adjusted-close convention) — effectively the **mid-price** (halfway between bid and ask). But in reality, if you're *buying*, you pay the ask (above mid); if you're *selling*, you receive the bid (below mid). You lose the difference every single time you trade.

**Formula:**

spread = ask − bid

spread_bps = [(ask − bid) / mid] × 10,000

Since a backtest marks to mid, the cost of a single one-way trade (buy or sell) is approximately **half the spread**:

half-spread cost_bps = spread_bps / 2

**Worked example** (using a 10,000-share trade at $100/share = $1,000,000 notional, to make the dollar impact concrete):

| Quantity | Value |
|---|---|
| Bid | $99.95 |
| Ask | $100.05 |
| Mid (what a backtest "sees") | $100.00 |
| Spread ($) | $0.10 |
| Spread (basis points (bps), where 100 bps = 1%) | $0.10 / $100.00 × 10,000 = **10 bps** |
| Half-spread cost (bps, one-way) | **5 bps** |
| **Half-spread cost ($, 10,000 shares / $1M notional)** | **$500** |
| Round-trip cost (bps) | **10 bps** (full spread) |
| **Round-trip cost ($, same trade)** | **$1,000** |

For context: highly liquid mega-caps (Apple Inc. (AAPL), Microsoft Corporation (MSFT)) often trade at spreads of 1-3 bps. Less liquid NASDAQ-100 names can run 5-15 bps. Small/mid-cap names outside this project's universe can run 30-100+ bps — one more reason universe selection (P1-L2) matters for realism.

---

## 3. Market impact

**What it fundamentally is:** the bid-ask spread only covers a *small* order — the size the market maker is quoted for. If an order is larger than what's available at the ask, it has to "walk up the order book," paying progressively higher prices for each subsequent slice. The market *moves against you* simply because you're trading — this is market impact.

Analogy: think of an order book like a grocery store's shelf of a sale item. The first 10 units are $2 each. Once those sell out, the store restocks at $2.10, then $2.20. Buying 200 units means an *average* price well above $2 — not because the item's fair value changed, but because the buyer's own demand consumed the cheap supply. That's impact.

**Two flavors, worth distinguishing:**

| Type | What it is | Does it recover? |
|---|---|---|
| **Temporary impact** | Price concession needed to complete the trade *right now*, given available liquidity | Yes — reverts once the order finishes and the book refills |
| **Permanent impact** | Price move that persists because the trading itself signaled new information to the market (e.g., "someone big is buying, maybe they know something") | No — becomes the new price level |

For a research project like this, the two don't need to be separated precisely — only a reasonable *total* impact estimate is needed.

**The core intuition — impact grows with size, but not proportionally:** trading twice as much does *not* create twice the impact. Impact grows roughly with the **square root** of how much of the day's normal trading volume the order consumes. This is one of the most well-established empirical results in market microstructure (the "square-root law of market impact").

**Why square root, intuitively:** the deeper an order eats into the book, the more new liquidity providers step in to offer shares at progressively higher prices — supply isn't linear, it thickens as price moves. Diminishing pain per additional dollar traded, but never zero.

**Simplified formula for intuition-building** (not a precisely calibrated model — real ones are proprietary and estimated from tick data this project doesn't have access to):

impact_bps = k × sqrt(Q / V)

where:
- Q = the dollar size of the order
- V = the stock's average daily dollar trading volume (Average Daily Volume, ADV)
- Q/V = the **participation rate** — what fraction of a normal day's volume the order represents
- k = an empirical scaling constant (illustrated with k=20 bps, a reasonable order-of-magnitude figure for liquid large-caps — real desks calibrate this from historical execution data)

**Worked example — impact at increasing participation rates (same stock, growing order size, $50M ADV assumed so order size Q is implied by each participation rate):**

| Participation (Q/V) | Order size (Q, vs. $50M ADV) | sqrt(Q/V) | Impact (bps), k=20 | **Impact cost ($)** |
|---|---|---|---|---|
| 1% | $500,000 | 0.10 | **2.0 bps** | **$100** |
| 4% | $2,000,000 | 0.20 | **4.0 bps** | **$800** |
| 9% | $4,500,000 | 0.30 | **6.0 bps** | **$2,700** |
| 16% | $8,000,000 | 0.40 | **8.0 bps** | **$6,400** |
| 25% | $12,500,000 | 0.50 | **10.0 bps** | **$12,500** |

Note that the dollar cost grows faster than the bps figure alone suggests — both the bps rate *and* the order size are growing together as participation rises.

**Reading the table:** going from 1% to 4% participation (4x the size) only doubles the impact cost (2 bps → 4 bps), and going from 4% to 16% (4x again) only doubles it again (4 bps → 8 bps). That's the square-root relationship in action — proportionally smaller pain per additional dollar as size grows, but never free. This is also *why* portfolio capacity is finite: at some assets under management (AUM), rebalancing orders become large enough relative to ADV that impact costs eat the strategy's edge entirely (see Section 6).

---

## 4. Commissions

**What it fundamentally is:** the explicit, contractually-fixed fee paid to a broker and/or exchange for executing the trade — the one cost component that's completely transparent and known in advance, unlike spread and impact which depend on market conditions at the moment of trading.

**Common structures:**

| Structure | Typical for | Example |
|---|---|---|
| Per-share | Institutional equity trading | $0.0035–$0.01/share |
| Per-trade flat fee | Retail brokers (older model) | $4.95/trade regardless of size |
| Commission-free | Modern retail brokers (Robinhood, Fidelity retail, etc.) | $0 (broker earns via payment-for-order-flow or spread instead) |
| Basis points of notional | Some institutional agreements | 1–2 bps of trade value |

**Worked example:**

| Trade | Shares | Price | Notional | Per-share commission ($0.005) | Commission in bps |
|---|---|---|---|---|---|
| Buy AAPL | 10,000 | $100.00 | $1,000,000 | 10,000 × $0.005 = $50 | $50 / $1,000,000 × 10,000 = **0.5 bps** |

Commissions are the smallest of the three cost sources for institutional-scale trading in liquid large-caps — but not zero, and don't disappear even for "free" retail brokers (the cost shows up through a worse effective spread instead — worth knowing, but out of scope to model precisely here).

---

## 5. Putting it together — total transaction cost model

**Full one-way trading cost:**

total cost_bps = half-spread_bps + impact_bps + commission_bps

**Worked example — a single $2M trade in a liquid NASDAQ-100 name:**

| Component | Assumption | Cost (bps) | **Cost ($, on $2M notional)** |
|---|---|---|---|
| Half-spread | 10 bps spread ÷ 2 | 5.0 | **$1,000** |
| Market impact | $2M order, $50M ADV → participation = 4%, k=20 | 4.0 | **$800** |
| Commission | $0.005/share on a $100 stock | 0.5 | **$100** |
| **Total one-way cost** | | **9.5 bps** | **$1,900** |
| **Round-trip cost (buy + later sell)** | | **~19 bps** | **~$3,800** |

Rounded to a clean **10 bps one-way** working assumption for Project 1 (see Section 7).

**Connecting to P1-L7's turnover formula:** the turnover-cost relationship from P1-L7 measures *how much* of the portfolio trades at each rebalance; the cost-per-unit-turnover assumption (which P1-L7 left as a 5 bps *placeholder*, explicitly flagged as illustrative) determines how much that turnover *costs*. This lesson replaces that placeholder with a grounded estimate.

cost drag per rebalance = turnover × cost_bps per unit turnover

**Recomputing the P1-L7 worked example with the updated (10 bps) assumption, vs. the old 5 bps placeholder:**

| Rebalancing frequency | Turnover per rebalance | Rebalances/year | Old estimate (5 bps/unit) | Updated estimate (10 bps/unit) |
|---|---|---|---|---|
| Monthly | 25% | 12 | 15 bps/year | **30 bps/year** |
| Weekly | 25% | 52 | 65 bps/year | **130 bps/year** |
| Daily | 25% | ~252 | 315 bps/year | **630 bps/year** |

**Same table converted to dollars, assuming an illustrative $10M portfolio** (matching the smallest AUM tier used later in the capacity-decay table):

| Rebalancing frequency | Turnover/rebalance | Rebalances/year | Cost/rebalance (bps) | $ traded/rebalance (on $10M) | **$ cost/rebalance** | Annualized cost (bps) | **Annualized $ cost (on $10M)** |
|---|---|---|---|---|---|---|---|
| Monthly | 25% | 12 | 10 bps | $2,500,000 | **$2,500** | 30 bps/yr | **$30,000/yr** |
| Weekly | 25% | 52 | 10 bps | $2,500,000 | **$2,500** | 130 bps/yr | **$130,000/yr** |
| Daily | 25% | ~252 | 10 bps | $2,500,000 | **$2,500** | 630 bps/yr | **$630,000/yr** |

The per-rebalance dollar cost is identical across frequencies (same turnover, same $10M base) — what changes is how many times per year that cost is paid. Daily rebalancing pays the $2,500 roughly 252 times a year instead of 12.

The relative story from P1-L7 (frequent rebalancing gets punished disproportionately by cost drag) is unchanged — but the *absolute* numbers roughly double once the per-unit-turnover cost is grounded in an actual spread+impact+commission estimate rather than a round-number placeholder. This is exactly the kind of thing an interviewer would probe: "was your cost assumption justified, or just a guess?" This lesson provides a defensible answer with the components broken out.

**What this means for net returns:** if a factor strategy generates, say, 3.0% gross annualized excess return (illustrative), a 30 bps/year cost drag at monthly rebalancing eats about **10% of the gross edge** before slippage, capacity, or crowding effects are even considered (Section 6). This is why transaction-cost-aware backtesting is not an optional nice-to-have — a strategy that looks great gross-of-costs can be marginal or negative net-of-costs, and *that* gap is one of the most common reasons quant strategies fail to survive contact with live trading.

---

## 6. The backtest-vs-live gap ("implementation shortfall")

**What it fundamentally is:** even after subtracting spread + impact + commission from backtest returns, live performance will *still* differ from what the backtest predicted. **Implementation shortfall** is the finance-industry term for the total gap between the price at the moment a trade *decision* was made (the "decision price," e.g., yesterday's close, which is what a backtest uses) and the price actually *achieved* once the trade was fully executed in the real world.

The cost model from Sections 2-5 captures *some* of this gap. It does not capture all of it. What's left over:

| Backtest assumption | Live reality | Why it creates a gap |
|---|---|---|
| Trade fills exactly at the known close price | Real orders execute throughout the trading day via an execution algorithm, at a *blend* of prices that may be worse than the close | "Fill price idealization" — the backtest effectively assumes perfect foresight of the exact settlement price |
| Signal-to-trade is instantaneous | There's a real delay between when a model generates a signal (e.g., after market close) and when the trade actually executes (next morning's open, or spread across the day) | **Execution latency** — the market can move between decision and execution, especially for news-driven or fast-decaying signals (recall P1-L7's decay curve — a signal that's already lost value by the time it can be acted on) |
| Impact/cost estimates are fixed regardless of portfolio size | A strategy tested on a hypothetical $10M book behaves very differently once real AUM reaches $500M — the same rebalance now represents a much higher participation rate (Section 3's table) at every single name | **Capacity constraints** — most strategies have a maximum AUM beyond which costs overwhelm the edge; this is a real, quantifiable ceiling, not a vague caveat |
| The strategy's trades are the only ones happening | If a factor becomes popular (e.g., momentum strategies proliferate industry-wide), many funds trade the same signal at the same time, competing for the same liquidity and moving prices against *everyone* simultaneously | **Crowding** — impact costs rise industry-wide when a strategy becomes consensus, independent of any single fund's own AUM |

**Worked illustrative example — capacity decay:** using the square-root impact model from Section 3, this shows what happens to a fixed rebalancing strategy as AUM scales up (same % turnover, same universe, same ADV per stock — only the dollar size of each trade grows):

| Strategy AUM | Illustrative order size per rebalanced name | Participation rate (vs. $50M ADV) | Impact cost (bps) | Total one-way cost (5 bps spread + impact + 0.5 bps commission) | **$ cost per name, per rebalance** |
|---|---|---|---|---|---|
| $10M | $50,000 | 0.1% | 0.6 | 6.1 bps | **$30.50** |
| $100M | $500,000 | 1.0% | 2.0 | 7.5 bps | **$375** |
| $500M | $2,500,000 | 5.0% | 4.5 | 10.0 bps | **$2,500** |
| $2B | $10,000,000 | 20.0% | 8.9 | 14.4 bps | **$14,400** |

The dollar column is cost *per name, per rebalance* — multiply by the number of names traded at each rebalance and the number of rebalances/year to get the full annualized dollar drag on the fund. At $10M AUM, trading costs barely dent the strategy. At $2B AUM, one-way costs have more than doubled — and this is a *single name's* impact; the effect compounds across every position in the portfolio, every rebalance. This is exactly why a strategy that looks excellent in a backtest can become uninvestable at the AUM scale of an actual asset manager — and it's a legitimate, sophisticated point to raise in interviews: "my backtest returns are gross of capacity constraints; here's how I'd model AUM-scaled costs in production."

---

## 7. Data limitation for Project 1

**The honest problem:** yfinance — Project 1's only data source per the P1-L2/P1-L3 decisions — provides daily Open/High/Low/Close/Volume (OHLCV) bars. It does **not** provide historical bid/ask quotes or intraday volume-at-price data. That means:

- Spread costs (Section 2) **cannot be empirically measured** per stock per date from the available data — there's no bid/ask column to compute it from.
- Market impact (Section 3) **cannot be calibrated** from real execution data — that requires proprietary broker/exchange execution records (Trade and Quote (TAQ) data, or a broker's own transaction cost analysis (TCA) history), which are paid, institutional-only data sources.

**This is the same category of limitation as the survivorship-bias/point-in-time-data gaps disclosed in P1-L2/L3/L8:** free tooling genuinely cannot replicate what a production trading desk has access to. The right move (same senior-PM instinct as before) is to disclose this explicitly rather than pretend a computed-from-data cost model exists when it doesn't.

**Resolution for Project 1:** use a **flat, assumed basis-point cost parameter** — grounded in this lesson's worked reasoning (spread + impact + commission for a typical liquid NASDAQ-100/S&P 500 large-cap trade at modest institutional size), not computed from per-stock market data. This is explicitly a simplification, and it is disclosed as one.

---

## 8. Decisions locked this lesson

1. **Transaction cost model for Project 1: flat assumed basis-point parameter, not computed from market data** (yfinance has no bid/ask or execution data). Default value: **10 bps one-way** (≈ 5 bps half-spread + ≈ 4 bps illustrative market impact + ≈ 0.5-1 bps commission, rounded), configurable in the backtest engine.
2. **Turnover-cost drag formula (from P1-L7) updated:** `cost drag per rebalance = turnover × cost_bps_per_unit_turnover`, with the default `cost_bps_per_unit_turnover` **updated from the P1-L7 illustrative 5 bps placeholder to 10 bps**, now grounded in this lesson's component breakdown rather than a round-number guess.
3. **Square-root market impact model (Section 3) is understood conceptually and documented, but not implemented against real data** in Project 1 — it requires execution-level data Project 1 doesn't have access to. Logged as a "what I'd build next" item for the case study (P1-Polish-5).
4. **Capacity constraints and crowding (Section 6) are conceptually understood and will be discussed qualitatively in the methodology risk memo**, but not quantitatively modeled in the backtest engine — Project 1 runs at a fixed illustrative AUM assumption, not a capacity-curve sweep. Also a "what I'd build next" item.
5. **Implementation shortfall is formally named and distinguished from the P1-L8 bias categories** (look-ahead, survivorship, selection, data snooping): those are *research methodology* biases; implementation shortfall is the *execution reality* gap. Both belong in the methodology risk memo, but as separate sections.

---

## 9. Follow-up: worked example at scale — $2B AUM, 100 names, monthly rebalance

**The question:** given a $2B AUM fund/strategy with 100 names, monthly rebalance, what's the total transaction cost on a monthly and annual basis, in both bps and dollars?

**Setup / assumptions used:**

| Input | Value | Source |
|---|---|---|
| AUM | $2,000,000,000 | given |
| Universe held | 100 names | given |
| Rebalance frequency | Monthly | P1-L7 locked default |
| One-way turnover per rebalance | 25% | P1-L7 illustrative working figure (not yet a measured backtest result) |
| Cost assumption | 10 bps flat default, and 14.4 bps AUM-scaled estimate | P1-L9 |

Note: at the portfolio level, the turnover-cost-drag framework expresses turnover as a % of AUM directly — the number of names cancels out of that calculation. The 100-names figure only matters when sizing an individual trade against a specific stock's average daily volume (ADV), which is what produced the 14.4 bps figure in Section 6's capacity table.

**The ambiguity this surfaced:** Project 1's locked default is dollar-neutral long-short (P1-L5) — a $2B AUM fund holds a $2B long book *and* a $2B short book simultaneously (200% gross exposure). P1-L7 stated that turnover for long-short portfolios is "calculated separately for both legs and combined," but Section 5's recomputed turnover-cost-drag table had illustrated only a single-book convention (applying turnover % once to a $10M base), creating an internal inconsistency that this worked example exposed.

**Method A — flat 10 bps default:**

| | Single-book convention (turnover applied once to $2B) | Long-short both-legs convention ($2B long + $2B short, turnover applied to each) |
|---|---|---|
| $ traded one-way, monthly | $500,000,000 | $1,000,000,000 |
| Cost, monthly (bps of AUM) | 2.5 bps | 5.0 bps |
| **Cost, monthly ($)** | **$500,000** | **$1,000,000** |
| Cost, annual (bps of AUM) | 30 bps | 60 bps |
| **Cost, annual ($)** | **$6,000,000** | **$12,000,000** |

**Method B — AUM-scaled 14.4 bps (from Section 6's capacity-decay table, which already models $2B specifically):**

| | Single-book convention | Long-short both-legs convention |
|---|---|---|
| $ traded one-way, monthly | $500,000,000 | $1,000,000,000 |
| Cost, monthly (bps of AUM) | 3.6 bps | 7.2 bps |
| **Cost, monthly ($)** | **$720,000** | **$1,440,000** |
| Cost, annual (bps of AUM) | 43.2 bps | 86.4 bps |
| **Cost, annual ($)** | **$8,640,000** | **$17,280,000** |

**Which numbers are right, and why this matters:**
- **Method B over Method A:** the flat 10 bps default was calibrated for modest institutional-scale trades (Section 5's $2M example), not for the ~20% ADV participation rate the capacity table showed a $2B fund actually hitting per name. This is the capacity-constraint point from Section 6 in practice — the cost assumption itself should scale with AUM, and a fund this size is well past the point where the flat default is realistic.
- **Both-legs over single-book:** this is now the **locked convention** for Project 1 (see decision below) — it matches P1-L7's original wording and avoids understating cost by exactly 2x for the long-short book.

**Decision locked (2026-07-14, follow-up to P1-L9):** **Long-short turnover convention is locked to "both-legs."** For a dollar-neutral long-short portfolio, one-way turnover is calculated separately for the long book and the short book, and the resulting traded-dollar amounts are summed — per P1-L7's original wording. Concretely, for AUM of $X with 100% long and 100% short exposure (200% gross, dollar-neutral), one-way turnover % applies to the long book ($X) AND separately to the short book ($X), for a combined one-way traded-dollar amount of turnover% × 2X — not turnover% × X. **All turnover-cost-drag calculations in P1-Build-5/P1-Build-6 must use the both-legs convention for the long-short book.** The long-only top-quintile alternative view (P1-L5's practitioner-facing construction) has only one leg, so this convention doesn't change its calculation — turnover% × AUM applies directly there, unchanged.

---

## 10. Follow-up: is this level of cost scrutiny overblown? Materiality framing

**Context — where this section comes from:** Section 9 worked out annual transaction costs of roughly $12M-$17M for a $2B fund (averaging to ~$15M), which is about 0.75% of AUM. A natural pushback surfaced: *0.75% of AUM sounds tiny — isn't the whole transaction-cost exercise disproportionate to how small that number is relative to the fund's total capital?* This section captures that pushback and the resolution, because it's a legitimate challenge to the lesson's premise and the reasoning is worth keeping alongside the worked numbers it's reacting to.

**Why 0.75% of AUM is the wrong denominator:** "rounding error" implicitly compares 0.75% against total AUM. But the number that actually matters isn't "cost as % of AUM" — it's **cost as % of the edge the strategy is trying to capture.** That is a completely different scale, and it's the comparison a real portfolio manager (PM) or limited partner (LP) allocator actually makes: not "is this small relative to $2B" but "how much of my alpha did I just hand over to execution."

**Benchmark table — reading it correctly:** each row compares the $15M/year (0.75% of AUM) cost drag against a different reference point. Column 2 is the benchmark's own typical size (as a % of AUM or return); column 3 answers *"if you divide 0.75%/year by that benchmark number, what fraction of it does it represent?"* — i.e., 0.75% ÷ benchmark value, expressed as a percentage or multiple.

| Benchmark | Typical value | The math | 0.75%/year as % of it |
|---|---|---|---|
| Gross excess return targeted by a factor long-short strategy (illustrative — the kind of edge Project 1 is trying to capture) | 3-5% | 0.75 ÷ 4 (midpoint) | **~15-25%** (range covers the 3-5% span) |
| Typical "2 and 20" hedge fund management fee | 2.0% of AUM | 0.75 ÷ 2.0 | **~38%** of the management fee alone |
| Equity risk premium (S&P 500 long-run average excess return) | ~5-6% | 0.75 ÷ 5.5 (midpoint) | **~13%** |
| Mutual fund expense ratio (a passive index fund) | 0.03-0.10% | 0.75 ÷ 0.05 (midpoint) | **~15x, up to 25x** a passive fund's entire cost structure |

**What each row is actually telling you:**
- **Row 1 (most important):** if the strategy targets 3-5% gross excess return per year — the entire point of building it — transaction costs alone consume roughly a fifth to a quarter of that, before salaries, overhead, or anything else. This is cost measured against the thing the strategy is actually trying to produce.
- **Row 2:** a "2 and 20" hedge fund charges investors 2% of AUM as a flat management fee regardless of performance. The cost drag is more than a third the size of that fee — trading costs alone are comparable in magnitude to what the fund charges clients just to exist.
- **Row 3:** the equity risk premium is the baseline extra return stocks have historically paid over risk-free assets. A ~13% bite out of that baseline is a meaningful sanity-check scale, not noise.
- **Row 4:** a plain index fund — the cheap passive alternative the strategy is implicitly competing against — costs 0.03-0.10%/year total. Transaction costs alone are 15-25x *that entire fund's cost structure*, meaning the strategy has to clear a much higher hurdle than "just buy the index" before the added complexity is worth it.

**The compounding problem — a static 0.75%/year understates the real damage:** this cost recurs every year, forever, and compounds against the fund the same way a fee does. Over a 10-year horizon on $2B:

| | No cost drag | 0.75%/year cost drag | Cumulative gap |
|---|---|---|---|
| $2B compounding at 6%/year, 10 years | $3.58B | — | — |
| $2B compounding at 5.25%/year, 10 years | — | $3.32B | **~$260M foregone** |

A quarter-billion dollars of compounded difference is exactly the kind of figure that shows up in an institutional due-diligence deck comparing a fund against a lower-cost competitor.

**Where the skepticism is fair — conceded, not dismissed:** there's a real difference between "transaction costs matter a lot" (true, not overblown) and "you need an elaborate, precisely-calibrated square-root impact model to capture that" (often overkill). Plenty of funds run fine with a simple flat-bps assumption, revisited periodically against actual fills, rather than a full market-impact model requiring proprietary execution data. The sophistication of the *cost model* should scale with the strategy's turnover and size:
- A low-turnover, buy-and-hold fundamental strategy can reasonably treat transaction costs as close to a rounding error.
- A monthly-rebalanced, dollar-neutral, quintile-based long-short strategy — Project 1's actual construction — cannot, because turnover is baked into the strategy's design, not incidental to it.

**Resulting framing (for the methodology risk memo and interview conversations):** cost *materiality* is high for a strategy shaped like Project 1's; cost *modeling precision* should be proportionate to the strategy's turnover profile rather than maximally elaborate by default. A clean way to state this: "the cost model wasn't over-engineered, because the strategy's turnover profile didn't demand a full market-impact calibration — but the *order of magnitude* had to be right, because at this AUM the cost drag is a meaningful fraction of gross alpha (15-25% by the benchmarks above), not a rounding error against total capital."

---

## Concepts still shaky (flagged for possible revisit)

- The precise difference between temporary and permanent market impact in practice (both introduced conceptually; distinguishing them empirically requires data this project doesn't have — likely stays qualitative-only for Project 1).
- How real trading desks estimate the impact coefficient (k in Section 3's formula) from historical execution data — out of scope for Project 1, but a good "how would you productionize this" interview question to be ready for.
