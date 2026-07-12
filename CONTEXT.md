# AI Investment Platform - Context Journal

## Current State
- **Active project:** Project 1 - Factor Research Copilot
- **Active phase:** Phase 1 - Concept Lessons (4 of 10 complete)
- **Last session:** 2026-07-12 - P1-L4 complete (raw vs normalized factors, z-scoring, winsorization, sector neutralization intuition)
- **Next session goal:** P1-L5 - Portfolio construction from signals (decile/quintile portfolios, long-only vs long-short, equal weighting vs signal weighting)
- **Target start of Lesson 5:** Next available session

## Career Pivot Decisions (cross-project)
- 2026-04-26 - Pivoting from quant research path to hands-on AI Product Manager 
  roles in finance and AI-native firms
- 2026-04-26 - Confirmed I will not pursue WQU MScFE or pure quant researcher 
  path; weak quant math foundation makes that low-EV given my profile of an established senior product manager
- 2026-04-26 - Building 4 projects (skipping Options Risk Copilot unless a 
  derivatives interview pipeline materializes); 3 projects deeply built beats 
  5 surface-level
- 2026-04-26 - Stack decisions: Python 3.11, VS Code (not PyCharm), FastAPI, 
  Streamlit, pandas/numpy/scipy, Anthropic API (claude-sonnet-4-6), Claude Code
- 2026-04-26 - Data source: yfinance to start, will upgrade to Polygon.io in Project 2
- 2026-04-26 - Working approach with Claude: 4 phases per project (Concept 
  lessons → Architecture → Build sprints → Polish), intuition first then math, 
  teach finance from scratch as if MS Financial Engineering student
- 2026-04-26 - Hard commitment: I write code with my own hands. No copy-paste 
  of generated code without understanding and modifying it.
- 2026-04-26 - Conversation naming convention: P[#]-[Type]: [Topic] (e.g., 
  P1-L1, P1-Arch, P1-Build, P1-Debug, P1-Eval, P1-Polish)
- 2026-04-26 - Realistic timeline target: 9 months to AI PM role at finance/
  fintech firm; frontier labs (Anthropic/OpenAI/DeepMind) are Phase 2 (18-24 
  months out, after first AI PM role lands)
- 2026-04-26 - Will probe internal Fidelity AI roles in parallel with external 
  applications - higher EV than ChatGPT implied

## Anthropic Courses Plan (mapped to monthly timeline)
- Month 1: Claude 101, AI Fluency: Framework & Foundations, Claude Code 101
- Month 2: Claude Code in Action, Building with Claude API (start)
- Month 3: Building with Claude API (finish), Intro to MCP
- Month 4: Intro to Agent Skills, Intro to Subagents
- Month 5: Intro to Claude Cowork, MCP Advanced Topics
- Month 6: AI Capabilities and Limitations, one cloud course (Bedrock or Vertex)
- Month 7: Other cloud course, revisit API course evals sections
- Months 8-9: Stop course-taking, focus on interviewing

## Environment Setup Checklist (COMPLETE 2026-05-25)
- [x] WSL2 + Ubuntu 26.04 LTS installed
- [x] Python 3.11.9 installed via pyenv
- [x] VS Code + extensions (Python, Pylance, Jupyter, GitLens, Ruff, Error Lens, etc.)
- [x] Git configured + GitHub account with SSH keys (sidsalil@gmail.com)
- [x] Node.js + npm via nvm
- [x] Repo `ai_investment_platform/` created with full directory structure
- [x] Virtual environment + requirements.txt installed and verified
- [x] Anthropic API key created, .env configured, test script passes
- [x] Claude Code installed and authenticated (Claude Pro)
- [x] yfinance verified imports correctly (full download test deferred to P1)
- [x] Claude Project "AI PM - Career Pivot" created with custom instructions
- [x] CONTEXT.md and resume uploaded to project knowledge
- [x] First commit + .gitkeep commit pushed to GitHub

## Dev Environment (as of 2026-05-25)
- OS: Windows 11 with WSL2 (Ubuntu 26.04 LTS "Resolute")
- Hostname: SidSalilLaptop
- Linux user: sidsa
- Python: 3.11.9 via pyenv (~/.pyenv/)
- Node: v24.16.0 LTS via nvm
- Editor: VS Code on Windows, connected to WSL via Remote-WSL extension
- Project location: ~/projects/ai_investment_platform (Linux filesystem)
- GitHub: github.com/sidsalil/ai_investment_platform (private)
- All dev work happens in WSL, not native Windows
- Claude Code: installed via npm in WSL, authenticated (Claude Pro plan)
- Default model: claude-sonnet-4-5 (anthropic SDK 0.97.0)

## Stack Versions (as of 2026-05-25 setup)
- Python: 3.11.9 via pyenv
- anthropic: 0.97.0
- yfinance: 1.3.0
- pandas: 2.2.3
- numpy: 2.1.3
- scipy: 1.14.1
- jupyter: 1.1.1
- fastapi: 0.115.5
- streamlit: 1.40.2
- ruff: 0.8.2
- pytest: 8.3.4
- node: v24.16.0
- npm: 11.13.0
- claude-code: 2.1.150

## Historical Milestones (compressed)

- 2026-04-26: Pivot decision made. Quant path rejected, AI PM path chosen.
- 2026-05-25: Full dev environment setup complete (WSL, Python, Claude Code, GitHub).
- 2026-05-25: Started Project 1. Completed P1-L1 (What is a factor and why does anyone care).
- 2026-05-25: Completed P1-L2 (universe, survivorship bias, point-in-time problem). Universe decision locked: NASDAQ-100 → S&P 500.
- 2026-07-12: Completed P1-L3 (simple vs log returns, adjusted vs raw prices, total return vs price return).
- 2026-07-12: Completed P1-L4 (raw vs normalized factors, z-scoring, winsorization, sector neutralization).
- [date]: Shipped Project 1.
- [date]: Started Project 2.
- [date]: Began external applications.

---

## Project 1: Factor Research Copilot

### Status
- Phase: Phase 1 (Concept Lessons) — 4 of 10 lessons complete
- Started: 2026-05-25
- Target ship date: TBD (estimate 6-10 weeks once started)

### Concepts Learned

**P1-L1: What is a factor and why does anyone care** (2026-05-25)
- A **factor** is a common return driver shared across many stocks (market, value, size, momentum, quality, etc.). Stock returns can be loosely decomposed as: return = sum(exposure × factor return) + idiosyncratic.
- **Exposure** (also called loading or beta) measures how plugged-in a particular stock is to a given factor. **Idiosyncratic return** (the residual) is the stock-specific leftover.
- Historical arc: Capital Asset Pricing Model (CAPM) in the 1960s — market-only factor model. Fama-French 3-factor (1992) added Small Minus Big (SMB, size) and High Minus Low (HML, value). Carhart 4-factor (1997) added Up Minus Down (UMD, momentum). Modern "factor zoo" contains 400+ proposed factors, most of which don't replicate under proper retesting.
- Factors that have held up reasonably well: market, size, value, momentum, quality, low-volatility, investment, profitability.
- Two distinct uses of factors to keep mentally separate:
  - **Factor as risk model** — decompose returns after the fact (Barra/Morgan Stanley Capital International (MSCI) world; risk and performance attribution teams)
  - **Factor as alpha source** — proactively construct portfolios that harvest factor premiums (smart-beta Exchange-Traded Funds (ETFs), AQR Capital Management (AQR), Dimensional Fund Advisors (DFA))
- **Project 1 sits on the alpha-source side.**
- **Cross-asset applicability:** the factor framework extends to fixed income (term, credit, carry, value, momentum), Foreign Exchange (FX) (carry, momentum, value, defensive), commodities (carry, momentum, value), options/volatility (Volatility Risk Premium (VRP), variance/skew premia), credit derivatives, Private Equity (PE), and private credit. Equity is the most mature; data quality and statistical power decline in other asset classes.
- **Phalippou critique of PE:** private equity returns largely decompose to equity beta + size + value + leverage + illiquidity premium. Once those are adjusted for, PE "alpha" is much smaller than the industry claims. Industry-contested but academically rigorous view.
- Cross-asset factor research stream: "Value and Momentum Everywhere" (Asness, Moskowitz, Pedersen, 2013) is the canonical paper showing value and momentum work across equities, bonds, currencies, and commodities.

**P1-L2: The universe — what stocks am I testing on** (2026-05-25)
- A **universe** is the set of securities eligible for research or a strategy — the quantitative equivalent of an investment mandate. Must be defined explicitly before any signal becomes meaningful.
- Four reasons to restrict a universe: tradability (microcaps' alpha isn't capturable), data quality (small/foreign stocks have messier corporate-action histories), hypothesis specificity ("12-month-minus-1-month momentum on US large-caps" is testable; "momentum works" is not), computational cost (faster iteration loops during research).
- **Survivorship bias (intro level; deeper in P1-L8):** backtesting on today's Standard & Poor's 500 (S&P 500) constituents excludes every company that failed, was acquired, or fell out of the index — Lehman Brothers, Washington Mutual, Bear Stearns, Enron, WorldCom, Time Warner, Compaq, EMC, J.C. Penney, GE during its long demotion. Effect: inflates measured returns by roughly 0.5–1.5% per year for US equity mutual fund universes; substantially larger for hedge fund universes and small-cap universes.
- **Point-in-time universe problem:** index composition changes over time. The S&P 500 of 2005 had different constituents than today's (Tesla wasn't public, Meta didn't exist, Nvidia was much smaller). Rigorous backtests require "what was the S&P 500 on this exact rebalance date" for every rebalance. Available from Center for Research in Security Prices (CRSP), Bloomberg, S&P Dow Jones Indices, FactSet. **Not available from yfinance.** Academic CRSP access runs thousands per year; commercial higher.
- Mental model for survivorship bias: it's like backtesting a strategy called "buy stocks I bought in 2010 that did well." Of course it works — you're peeking at the answer key.
- **Senior-PM move on this entire issue:** acknowledge survivorship bias openly in the methodology risk memo, document expected magnitude, describe the production fix path. Owning the limitation beats pretending free tools solved point-in-time. Honesty about limits is model-risk awareness, directly relevant to AI PM positioning.
- The broader pattern that will repeat across Project 1: every methodology choice carries a bias. Universe choice → survivorship bias. Return calculation → look-ahead in price adjustment. Portfolio construction → selection bias. The work is not to eliminate bias (impossible with free tools); it's to know which biases you're carrying and quantify their direction.

**P1-L3: Returns — the foundation everything builds on** (2026-07-12)
- A **simple return** = (P_t - P_(t-1))/P_(t-1) — the intuitive "how much richer/poorer" percentage. Additive **across assets** at a point in time (portfolio weighting works cleanly) but NOT additive across time — multi-period simple returns must be chained via **growth factor multiplication**: (1+R_1)×(1+R_2)×...×(1+R_n). Verified numerically: +10% then -10% nets to -1%, not 0%, because (1.10)×(0.90) = 0.99, not 1.00 — the loss compounds off the larger post-gain base.
- A **log return** (also called **continuously compounded return**) = ln(P_t/P_(t-1)), where `ln` is the natural logarithm (inverse of e^x, e ≈ 2.71828). Intuition: it answers "what constant, continuous growth rate — compounded every instant — would take yesterday's price to today's price," analogous to continuously compounded interest vs simple interest. For small returns (a few percent), log and simple returns are nearly numerically identical; they diverge meaningfully only for large moves.
- **Log returns are time-additive** — they can be summed directly across multiple periods without the growth-factor multiplication simple returns require. This is the single biggest reason they're preferred for quant research: chaining returns over a backtest window, running statistical tests (t-stats, regressions, Information Coefficient (IC) calculations in P1-L6), all become simple addition. Tradeoff: log returns are not exactly additive across assets in a portfolio (close for small returns, diverges for large ones) — simple returns are needed there instead.
- **Project 1 convention:** log returns internally for factor math and backtest chaining; simple returns for combining across assets at a point in time and for final memo language read by a portfolio manager ("the fund was up 8.3%," not "log return of 0.0797").
- **Adjusted vs raw prices:** raw close is the actual unadjusted historical traded price — frozen forever, never revised no matter when re-pulled. Adjusted close is mathematically corrected for stock splits (retroactively rescaling all prior prices to reflect current share count) and dividends (adding back reinvested-dividend value). **Rule: always use adjusted close for return calculations; raw close is reserved for computing actual dollar transaction costs (P1-Build-5).**
- **Critical mechanic — price adjustments are backward-looking and permanent, with no cutoff.** Every historical price since a stock's very first trading day gets rescaled every time a new split or dividend occurs — not just recent history. Splits and dividends both compound multiplicatively across the stock's entire history (a 50-year quarterly dividend payer has ~200 compounding adjustment layers baked into its earliest prices). This means adjusted close is a **moving target**: pulling the same historical date range on two different days can yield two different adjusted-close values for the identical historical day, because something that happened *after* that day changed the adjustment factor applied to it. Raw close never has this problem — it's a frozen historical fact.
- **Design consequence for P1-Build-1:** caching logic must treat "a new dividend or split occurred" as an event that invalidates the *entire* previously cached adjusted-close history for that ticker (not just the newest day). Raw close is safe to cache via simple row-append; adjusted close is not.
- **Total return vs price return:** price return = appreciation only; total return = price return + reinvested dividends = what an investor actually earned. Adjusted close (dividend-adjusted) gives total return automatically. Using price return where total return is meant systematically understates performance, worse over long horizons and for high-dividend sectors (utilities, REITs — Real Estate Investment Trusts, financials) — a meaningful share of the S&P 500's long-run historical return comes from reinvested dividends, not price appreciation alone.
- **Connection to P1-L2:** yfinance does not reliably capture delisting returns when a stock goes bankrupt or gets acquired mid-backtest — a data-quality limitation to disclose in P1-Polish-4 alongside survivorship bias. Full treatment deferred to P1-L8 (biases).

**P1-L4: Signal construction — turning data into predictions** (2026-07-12)
- A **raw factor value** is the literal computed number for a stock in its natural units (e.g., NVDA's 12-month-minus-1-month momentum = 95%). A **signal** is that raw value after it's been transformed onto a scale comparable across every stock in the universe on that date (e.g., NVDA's momentum z-score = 1.53). Every downstream step (portfolio construction, IC calculation) operates on the signal, not the raw factor.
- **Cross-sectional** means comparing across all stocks at one point in time, as opposed to **time-series** (one stock across many dates). Signal construction is always a cross-sectional exercise.
- Three problems that make raw factors unusable directly: (1) different factors live on different scales (momentum % vs P/E ratio vs dollar volume — not directly comparable), (2) outliers dominate and distort the whole scale, (3) a naive signal can secretly encode a sector bet rather than genuine differentiation.
- **Standard deviation** measures the typical spread/dispersion of a group of numbers around their mean — it's the "yardstick" against which unusualness gets measured.
- A **z-score** = (value − mean) / standard deviation, computed cross-sectionally. It answers "how unusual is this value, in units of typical spread, relative to its peer group." Worked numerically on 8 stocks (4 Tech, 4 Utilities) with raw momentum values: a single outlier (NVDA at 95%, vs. peers in the single/low-double digits) inflated the mean and standard deviation so much that it compressed all other real differentiation (AAPL 18% vs MSFT 22%) into a narrow band near zero (z-scores -0.017 vs 0.116) while NVDA's z-score (2.546) dwarfed everyone else.
- **Winsorization** is capping extreme values at a percentile threshold (e.g., 1st/99th or 5th/95th percentile) rather than deleting them — distinct from **trimming**, which removes the outlier observation entirely. Winsorization keeps every stock in the universe; it only caps the value. Re-running the same 8-stock example after winsorizing NVDA's value down from 95% to an illustrative 25% cap produced a materially different, more balanced z-score distribution (AAPL 0.825, MSFT 1.225, NVDA 1.525) — real differentiation among non-outlier stocks was recovered.
- **Order of operations matters:** winsorize the raw factor first, then z-score the cleaned data — not the reverse. Z-scoring before winsorizing lets the outlier distort the mean/standard deviation before it's ever capped, defeating the purpose.
- **Sector neutralization** is computing the z-score within each sector group separately, rather than across the whole universe — because a naive universe-wide z-score can be dominated by which sector performed better overall rather than genuine within-sector differentiation. Worked example: in the 8-stock universe, every Tech stock had a positive universe-wide z-score and every Utilities stock had a negative one (except one borderline case) — meaning a long/short portfolio built on the naive signal would really just be a long-Tech/short-Utilities sector bet, not a momentum strategy. After sector-neutral z-scoring, NEE (a utility, universe-wide z-score of -0.175, near the bottom of the whole universe) became the **highest-ranked stock of all 8** (sector z-score 1.528, higher than every Tech name) — its strong momentum *relative to other utilities* had been completely hidden by the universe-wide comparison.
- **Full signal construction pipeline for Project 1 (in order):** (1) compute raw factor using adjusted-close log returns per P1-L3 convention, (2) winsorize cross-sectionally at a percentile threshold, (3) z-score within sector groups (sector-neutral) as the default signal, with universe-wide z-scoring retained as an optional diagnostic to quantify how much of a naive signal is actually a sector bet.

### Concepts I'm Still Shaky On
- (from P1-L2) Exact mechanics of constructing a survivorship-bias-free universe in practice — combining current tickers with delisted ones via a paid source. Revisit in P1-L8.
- (from P1-L2) Statistical machinery for quantifying survivorship bias's effect on a specific backtest (not just the qualitative direction). Revisit in P1-L8.
- (from P1-L2) Interaction of point-in-time universe with point-in-time fundamentals — restated earnings, late filings, accounting revisions. Revisit when fundamentals enter the picture in P1-Build-3 (value factor).

### Code Written
- (none yet)

### Decisions Made (P1-specific)
- 2026-05-25 — **Universe for Project 1: NASDAQ-100 during build sprints (fast iteration loops while learning the pipeline); switch to S&P 500 for the final eval and demo (the standard learner deliverable, deeper liquidity universe).** Survivorship bias acknowledged explicitly in P1-Polish-4 (methodology risk memo). The data ingestion module (P1-Build-1) must parameterize the universe so the NASDAQ-100 ↔ S&P 500 switch is a config change, not a refactor.
- 2026-07-12 — **Return convention for Project 1: log returns for all internal factor/backtest math (time-additive, needed for chaining and statistical tests); simple returns for cross-asset portfolio combination and final memo/reporting language.** Adjusted close (not raw close) is the required default price series for all return calculations, since it yields total return automatically. Raw close reserved for P1-Build-5 transaction cost calculations only.
- 2026-07-12 — **Signal construction pipeline order for Project 1: raw factor → winsorize (cross-sectional, 1st/99th percentile default, configurable) → sector-neutral z-score.** Sector-neutral z-scoring is the default signal used in portfolio construction (P1-L5 onward); universe-wide z-scoring is retained only as an optional diagnostic to detect and quantify sector-bet contamination in a signal, surfaced in the methodology validator (P1-Build-8).

### Open Questions
- (none open)

### Mistakes & Lessons
- (empty — will accumulate)

### Carried-Forward Action Items
Things surfaced in completed lessons that need to be remembered when we reach the relevant phase. Format: `(source lesson) → target phase: action`.

- **(P1-L2) → P1-Build-1 (data ingestion module):** Parameterize the universe so NASDAQ-100 ↔ S&P 500 switch is a config change. Universe constituents sourced from a stable public source (Wikipedia is the standard); freeze the snapshot date for reproducibility.
- **(P1-L2) → P1-Polish-4 (methodology risk memo):** Include explicit "Universe choice and survivorship-bias acknowledgment" section. Document expected magnitude (~0.5–1.5%/year inflation on US equity universes; larger for hedge funds and small-caps). Describe the production fix path (CRSP / FactSet / S&P Dow Jones Indices point-in-time membership data) and why it was out of scope for the learning project.
- **(P1-L3) → P1-Build-1 (data ingestion module):** Confirm exact yfinance adjusted-close column name/behavior at time of implementation (API details may have shifted); ensure data ingestion pulls adjusted close, not raw close, as the default price series.
- **(P1-L3) → P1-Build-1 (data ingestion module):** Caching logic must account for the fact that adjusted close is a moving target — a new dividend or split invalidates the entire historical cached series for that ticker, not just the newest day. Raw close, by contrast, is safe to cache with simple row-append. Design cache invalidation accordingly (e.g., periodic full re-pull of adjusted series, or detect new corporate actions and trigger re-adjustment).
- **(P1-L3) → P1-Polish-4 (methodology risk memo):** Add explicit note that yfinance does not reliably capture delisting returns, alongside the existing survivorship bias disclosure. Full technical treatment deferred to P1-L8.
- **(P1-L4) → P1-Build-2/3 (factor calculation modules):** Implement winsorization at 1st/99th percentile (configurable) applied before z-scoring, not after. Implement sector-neutral z-scoring as the default signal construction path, with universe-wide z-scoring available as a flag for diagnostic comparison.
- **(P1-L4) → P1-Build-2/3 (factor calculation modules):** Need a sector classification data source for NASDAQ-100/S&P 500 constituents (e.g., Global Industry Classification Standard (GICS) sector via yfinance's `.info` field, or a static mapping file). Must confirm at build time whether yfinance reliably provides sector data for the full universe, or whether a supplementary static mapping is needed.
- **(P1-L4) → P1-Build-8 (methodology validator):** Validator should flag signals where the universe-wide z-score and sector-neutral z-score diverge sharply for many stocks in the same direction — a diagnostic for "this signal may really be a sector bet," directly building on the P1-L4 worked example.

---

## Project 2: Backtesting Copilot
*Not started. Will populate when Project 1 ships.*

---

## Project 3: Portfolio Construction Copilot
*Not started. Will populate when Project 2 ships.*

---

## Project 4: ML Signal Lab
*Not started. Will populate when Project 3 ships.*
