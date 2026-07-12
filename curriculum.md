# AI Investment Platform - Curriculum

> Living curriculum for the 4-project journey to hands-on AI Product Manager roles.
> Last updated: 2026-07-12

---

## How to use this document

- **Check off lessons as you complete them.** "Complete" means: concepts understood AND deliverables produced AND completion criteria met. Not "I read about it."
- **Lessons within a phase should generally be done in order.** Phases must be done in order.
- **Time estimates assume focused work, not calendar time.** At 10 hrs/week realistic pace, divide by 10 to get weeks.
- **Update CONTEXT.md after every lesson.** This curriculum tracks what's done; CONTEXT.md tracks where you are now.
- **One lesson ≈ one Claude conversation, typically.** Some short lessons might combine; some hard ones might span two conversations.
- **Don't skip the "Explain it back" checkpoints.** They're the difference between learning and pattern-matching.

---

## Cross-Project Meta-Skills

Skills you accumulate across all 4 projects. Track maturity as you progress.

| Skill | After P1 | After P2 | After P3 | After P4 |
|-------|----------|----------|----------|----------|
| Python (pandas, numpy) | Comfortable | Strong | Strong | Production |
| Quant finance vocabulary | Factor research basics | + backtesting | + portfolio theory | + ML for finance |
| LLM API (Anthropic) | Basic structured outputs | Tool use | Multi-step reasoning | Agentic loops |
| Evaluation discipline | First eval set built | Iterating evals | Multi-dimensional evals | Production evals |
| Product thinking | Product brief written | Architecture maturity | User journey mastery | Roadmap thinking |
| Financial data handling | Time series basics | Multi-asset | Portfolio-level | Feature engineering |
| Methodology rigor | Look-ahead bias awareness | Walk-forward validation | Constraint validation | Leakage detection |

---

# PROJECT 1: Factor Research Copilot

**Goal:** Build an AI assistant that converts natural-language investment hypotheses into Python-based factor research with statistical validation, methodology checks, and auto-generated research memos.

**Estimated effort:** 60-80 hours focused work (6-10 weeks at 10 hrs/week)

**Status:** In progress — Phase 1 (Concept Lessons), 3 of 10 lessons complete

## Phase 1: Concept Lessons (~15-25 hours)

The foundation. You learn the quant finance vocabulary and reasoning you'll use across all 4 projects. Don't rush this phase - everything else compounds off it.

### [x] P1-L1: What is a factor and why does anyone care? — **completed 2026-05-25**
- **Concepts:** What a factor is, why factor investing exists, the major historical factors (value, momentum, size), CAPM → Fama-French history
- **Explain back:** "In your own words: what is a factor, and why would a portfolio manager care about one?"
- **Deliverable:** Notes in CONTEXT.md under "Concepts Learned"
- **Estimated time:** 1-2 hours

### [x] P1-L2: The universe - what stocks am I testing on? — **completed 2026-05-25**
- **Concepts:** Why we restrict the universe, survivorship bias intro, the S&P 500 as a starting universe, point-in-time universe problem
- **Explain back:** "Why is using today's S&P 500 to backtest from 2010 problematic? What would happen if I used 'all stocks that ever traded'?"
- **Deliverable:** Notes; decision on what universe Project 1 will use
- **Decision logged:** NASDAQ-100 for development → S&P 500 for final eval/demo. Survivorship bias acknowledged in P1-Polish-4.
- **Estimated time:** 1 hour

### [x] P1-L3: Returns - the foundation everything builds on — **completed 2026-07-12**
- **Concepts:** Simple vs log returns, when each is appropriate, adjusted vs raw prices (dividends, splits), total return vs price return
- **Explain back:** "Why are log returns mathematically nicer? When should you use simple returns instead?"
- **Deliverable:** Notes (P1_L3_Returns.md); a small Jupyter notebook computing both return types on AAPL data (notebook still to be hand-written per coding-ownership rule — see CONTEXT.md carried-forward items)
- **Decision logged:** Log returns for internal factor/backtest math; simple returns for cross-asset combination and reporting language. Adjusted close is the required default price series for all return calculations.
- **Estimated time:** 1-2 hours

### [ ] P1-L4: Signal construction - turning data into predictions
- **Concepts:** Raw factors vs normalized factors, z-scoring, winsorization, sector neutralization (intuition only)
- **Explain back:** "Why can't I just rank stocks by raw P/E ratios? What does z-scoring give me?"
- **Deliverable:** Notes; notebook with z-scoring example
- **Estimated time:** 2 hours

### [ ] P1-L5: Portfolio construction from signals
- **Concepts:** Decile/quintile portfolios, long-only vs long-short, equal weighting vs signal weighting
- **Explain back:** "If I have a momentum signal, how do I turn it into a portfolio? What does long-short isolate?"
- **Deliverable:** Notes; a hand-computed decile example for 20 stocks
- **Estimated time:** 1-2 hours

### [ ] P1-L6: Information Coefficient and statistical evaluation
- **Concepts:** IC, rank IC, Information Ratio, hit rate, t-statistics for IC, what "predictive" actually means statistically
- **Explain back:** "If my IC is 0.05, is that good? Why or why not?"
- **Deliverable:** Notes; notebook computing IC on a toy example
- **Estimated time:** 2 hours

### [ ] P1-L7: Factor decay and turnover
- **Concepts:** How long signals predict (1-day, 1-week, 1-month forward returns), decay curves, turnover, the turnover-cost relationship
- **Explain back:** "Why would a strategy with high turnover and a great backtest fail in production?"
- **Deliverable:** Notes
- **Estimated time:** 1-2 hours

### [ ] P1-L8: The biases that kill backtests
- **Concepts:** Look-ahead bias (deep), survivorship bias (deep), selection bias, multiple testing bias, data snooping
- **Explain back:** "Give me three different ways look-ahead bias can sneak into a backtest unnoticed."
- **Deliverable:** Notes; a "methodology gotchas" cheat sheet for your repo
- **Estimated time:** 2-3 hours - **this lesson matters more than most**

### [ ] P1-L9: Transaction costs and real-world frictions
- **Concepts:** Bid-ask spread, market impact, commissions, the gap between backtest and live performance
- **Explain back:** "A backtest shows 12% annual return. What questions should I ask before believing this number?"
- **Deliverable:** Notes; cost assumptions to use in Project 1
- **Estimated time:** 1-2 hours

### [ ] P1-L10: Risk and performance metrics
- **Concepts:** Sharpe ratio, Sortino, max drawdown, drawdown duration, Calmar, beta-to-market
- **Explain back:** "Why is Sharpe alone insufficient? What does drawdown duration tell you that max drawdown doesn't?"
- **Deliverable:** Notes; a "metrics glossary" for your repo
- **Estimated time:** 1-2 hours

**Phase 1 completion criteria:**
- All 10 lessons checked off
- You can explain factor research end-to-end to a non-quant friend in 10 minutes
- CONTEXT.md "Concepts Learned" section is populated with your own-words summaries

## Phase 2: Architecture & Design (~5-8 hours)

Now you have the vocabulary. Design the system before writing code.

### [ ] P1-Arch-1: System design
- **Deliverable:** Architecture diagram showing the major components (data layer, factor calc, portfolio construction, metrics, LLM, validation, UI, reporting)
- **Format:** Markdown with ASCII diagram OR a tool like Excalidraw, exported as PNG
- **Stored at:** `docs/architecture/project_01_factor_research.md`
- **Estimated time:** 2-3 hours

### [ ] P1-Arch-2: Data flow design
- **Deliverable:** Sequence diagram or written walkthrough: "User asks 'test momentum on S&P 500' → system flows through these steps → produces these outputs"
- **Stored at:** `docs/architecture/project_01_factor_research.md` (same doc)
- **Estimated time:** 1-2 hours

### [ ] P1-Arch-3: Module structure and interfaces
- **Deliverable:** A skeleton of Python file/function signatures (no implementation) - what calls what, what returns what
- **Estimated time:** 2-3 hours

**Phase 2 completion criteria:**
- You can draw the architecture on a whiteboard from memory
- A junior developer could read your architecture doc and understand the system without asking you questions
- Your skeleton compiles (even if functions just `pass`)

## Phase 3: Build Sprints (~30-40 hours)

This is where you actually write code. Each build sprint produces a working component.

### [ ] P1-Build-1: Data ingestion module
- **What you build:** A wrapper around yfinance that downloads, caches, and serves clean OHLCV data for a list of tickers
- **Key concerns:** Caching (don't re-download what you have), handling failures, date alignment
- **Carried-forward requirement (from P1-L2):** Parameterize the universe so NASDAQ-100 ↔ S&P 500 switch is a config change, not a refactor. Source constituents from a stable public source (Wikipedia standard); freeze snapshot date for reproducibility.
- **Located in:** `shared/data/`
- **Tests:** Pytest tests that verify caching works and bad inputs fail cleanly
- **Estimated time:** 3-5 hours

### [ ] P1-Build-2: Factor calculation - Momentum
- **What you build:** A function that computes 12-month-minus-1-month momentum (a classic factor) for a universe of stocks at a date
- **Key concerns:** Point-in-time correctness, NaN handling, vectorization
- **Located in:** `modules/01_factor_research/`
- **Tests:** Hand-verify against a known small example
- **Estimated time:** 3-4 hours

### [ ] P1-Build-3: Factor calculation - Other factors
- **What you build:** Volatility factor (rolling std of returns), liquidity factor (dollar volume), simple value factor if data available
- **Estimated time:** 3-4 hours

### [ ] P1-Build-4: Portfolio construction
- **What you build:** Take a factor signal at a date, build long-only decile portfolios and long-short top-vs-bottom decile portfolio
- **Estimated time:** 3-4 hours

### [ ] P1-Build-5: Backtest mechanics
- **What you build:** Walk forward in time, rebalance portfolio monthly, accumulate returns, apply transaction costs
- **Key concerns:** No look-ahead bias (THIS IS WHERE PEOPLE FAIL), realistic costs
- **Estimated time:** 4-6 hours - **the hardest build sprint**

### [ ] P1-Build-6: Metrics calculation
- **What you build:** Compute IC, decile spreads, Sharpe, drawdown, turnover from backtest results
- **Estimated time:** 2-3 hours

### [ ] P1-Build-7: LLM integration - Natural language → factor spec
- **What you build:** Function that takes "test 12-month momentum on the S&P 500" and produces a structured FactorSpec object using Anthropic API + Pydantic structured outputs
- **Key concept:** Structured outputs, schema validation
- **Estimated time:** 3-5 hours

### [ ] P1-Build-8: Methodology validator
- **What you build:** A pre-execution validator that flags suspicious factor specs (look-ahead suspects, unrealistic assumptions, statistical concerns)
- **This is your AI PM differentiator** - shows you understand model risk
- **Estimated time:** 3-4 hours

### [ ] P1-Build-9: Research memo generator
- **What you build:** Function that takes backtest results and generates a 1-page research memo with hypothesis, methodology, results, limitations
- **Uses:** Claude API to write the prose given the numbers
- **Estimated time:** 2-3 hours

### [ ] P1-Build-10: Streamlit UI
- **What you build:** Web interface where user types a question, sees factor running, gets charts + memo
- **Estimated time:** 4-6 hours

**Phase 3 completion criteria:**
- You can run the full pipeline end-to-end: type a question → see factor research → get memo
- All 10 build sprints have working code with at least one test each
- The validator catches at least 5 different methodology mistakes you've intentionally seeded

## Phase 4: Polish & Ship (~10-15 hours)

Building is one thing. Packaging is what makes a portfolio.

### [ ] P1-Eval: Build the eval set
- **What you build:** 25 natural-language prompts, each with an expected factor spec output. Run your LLM extractor, measure accuracy
- **Deliverable:** `docs/eval_reports/project_01_factor_extraction_eval.md`
- **Estimated time:** 3-5 hours

### [ ] P1-Polish-1: Product brief
- **What you write:** 2-page PRD covering problem, user, workflow before/after, solution, success metrics
- **Deliverable:** `docs/product_briefs/project_01_factor_research.md`
- **Estimated time:** 2-3 hours

### [ ] P1-Polish-2: README
- **What you write:** Professional README with problem statement, demo, architecture, how to run, limitations, what you learned
- **Deliverable:** `modules/01_factor_research/README.md`
- **Estimated time:** 1-2 hours

### [ ] P1-Polish-3: Demo video
- **What you record:** 5-7 minute screen recording: state the problem, show the workflow, walk through architecture, highlight one design decision
- **Estimated time:** 1-2 hours (will take multiple takes - that's fine)

### [ ] P1-Polish-4: Methodology risk memo
- **What you write:** Honest accounting of what your project does NOT do (point-in-time data, survivorship bias, no slippage modeling)
- **Why this matters:** Shows hiring managers you understand the limits of your own work
- **Carried-forward requirement (from P1-L2):** Include explicit "Universe choice and survivorship-bias acknowledgment" section. Document expected magnitude (~0.5–1.5%/year inflation on US equity universes; larger for hedge funds and small-caps). Describe production fix path (CRSP / FactSet / S&P Dow Jones Indices point-in-time membership data).
- **Estimated time:** 1 hour

**PROJECT 1 COMPLETION CRITERIA:**
- All lessons + builds + polish items checked off
- Working demo someone else can run from your README
- Demo video recorded
- Product brief, README, eval report, risk memo all in your repo
- Repo pushed to GitHub, ready for portfolio link
- **You can explain the project to a hiring manager in 5 minutes with no notes**

**Resume bullet earned:**
> Built an AI Factor Research Copilot that converts natural-language investment hypotheses into Python-based factor tests with IC analysis, factor decay, decile returns, turnover, transaction-cost sensitivity, and automated research memos with methodology risk caveats.

---

# PROJECT 2: Backtesting Copilot

**Goal:** AI-assisted strategy backtesting where users describe strategies in natural language and get rigorous backtests with realistic frictions, automated quality review, and benchmark comparison.

**Estimated effort:** 50-70 hours (5-8 weeks)

**Status:** Not started

**Prerequisites:** Project 1 complete; understanding of factor research, returns, transaction costs

## Phase 1: Concept Lessons (~10-15 hours)

### [ ] P2-L1: Backtest vs paper trading vs live
- Conceptual differences and what each can tell you

### [ ] P2-L2: Event-driven vs vectorized backtesting
- Architecture choice with major downstream implications

### [ ] P2-L3: Position sizing schemes
- Equal weight, volatility-weighted, signal-weighted, Kelly intuition

### [ ] P2-L4: Rebalancing frequency tradeoffs
- Daily, weekly, monthly - costs vs responsiveness

### [ ] P2-L5: Transaction costs deeper
- Bid-ask, market impact, commission structures, model choices

### [ ] P2-L6: Slippage modeling
- What it is, why it matters, simple vs realistic models

### [ ] P2-L7: Walk-forward validation
- Why it's necessary, how to implement properly

### [ ] P2-L8: Out-of-sample testing
- Train/test discipline for strategy research

### [ ] P2-L9: Multiple testing problem (p-hacking)
- Why testing 100 strategies and picking the best is dishonest

### [ ] P2-L10: Realistic backtest gotchas
- Timezone bugs, data quality, corporate actions, exchange holidays

## Phase 2: Architecture & Design (~5-8 hours)

### [ ] P2-Arch-1: Event-driven engine design
### [ ] P2-Arch-2: Strategy specification schema design
### [ ] P2-Arch-3: Module structure

## Phase 3: Build Sprints (~25-35 hours)

### [ ] P2-Build-1: Event loop and core engine
### [ ] P2-Build-2: Order/fill simulation with costs
### [ ] P2-Build-3: Portfolio accounting
### [ ] P2-Build-4: Multi-asset support
### [ ] P2-Build-5: Risk controls (position limits, exposure caps)
### [ ] P2-Build-6: LLM strategy parser (natural language → strategy YAML)
### [ ] P2-Build-7: Backtest quality reviewer (subagent that critiques the strategy spec)
### [ ] P2-Build-8: Tear sheet / metrics dashboard
### [ ] P2-Build-9: Benchmark comparison
### [ ] P2-Build-10: Streamlit UI

## Phase 4: Polish & Ship (~8-12 hours)

### [ ] P2-Eval: 25 strategy prompts → expected configs eval
### [ ] P2-Polish-1: Product brief
### [ ] P2-Polish-2: README
### [ ] P2-Polish-3: Demo video
### [ ] P2-Polish-4: Robustness memo

**Resume bullet earned:**
> Built an AI Backtesting Copilot that transforms natural-language trading strategy descriptions into executable Python backtests with transaction costs, slippage, turnover analysis, exposure controls, benchmark comparison, and an automated strategy-quality reviewer subagent.

---

# PROJECT 3: Portfolio Construction Copilot

**Goal:** Convert natural-language portfolio constraints into optimized portfolios using multiple optimization approaches, with risk decomposition, scenario analysis, and tradeoff explanation.

**Estimated effort:** 45-60 hours (5-7 weeks)

**Status:** Not started

**Prerequisites:** Projects 1 and 2 complete

## Phase 1: Concept Lessons (~12-18 hours)

### [ ] P3-L1: Portfolio theory basics (return vs risk)
### [ ] P3-L2: Mean-variance optimization (Markowitz)
### [ ] P3-L3: Why max-Sharpe is unstable in practice
### [ ] P3-L4: Covariance estimation problems
### [ ] P3-L5: Covariance shrinkage (Ledoit-Wolf intuition)
### [ ] P3-L6: Risk parity intuition
### [ ] P3-L7: Risk contribution analysis
### [ ] P3-L8: Constrained optimization (caps, exposures)
### [ ] P3-L9: Tracking error and active risk
### [ ] P3-L10: Scenario analysis and stress testing
### [ ] P3-L11: VaR vs CVaR

## Phase 2: Architecture & Design (~5-7 hours)

### [ ] P3-Arch-1: Optimizer abstraction design
### [ ] P3-Arch-2: Constraint specification language
### [ ] P3-Arch-3: Module structure

## Phase 3: Build Sprints (~20-30 hours)

### [ ] P3-Build-1: Equal-weight and minimum-variance optimizers
### [ ] P3-Build-2: Max-Sharpe optimizer
### [ ] P3-Build-3: Risk parity optimizer
### [ ] P3-Build-4: Covariance estimation (sample + shrinkage)
### [ ] P3-Build-5: Constraint engine (caps, sectors, exposures)
### [ ] P3-Build-6: Risk decomposition
### [ ] P3-Build-7: Scenario shock framework
### [ ] P3-Build-8: LLM constraint extractor
### [ ] P3-Build-9: Infeasible-constraint detection
### [ ] P3-Build-10: Comparison/explanation layer
### [ ] P3-Build-11: Streamlit UI

## Phase 4: Polish & Ship (~8-12 hours)

### [ ] P3-Eval: 25 constraint prompts → expected optimizer inputs
### [ ] P3-Polish-1: Product brief
### [ ] P3-Polish-2: README
### [ ] P3-Polish-3: Demo video
### [ ] P3-Polish-4: Governance & risk-controls memo

**Resume bullet earned:**
> Built an AI Portfolio Construction Copilot that converts natural-language investment constraints into optimized portfolios comparing equal-weight, minimum-variance, max-Sharpe, and risk-parity allocations with covariance shrinkage, risk decomposition, scenario shocks, and infeasibility detection.

---

# PROJECT 4: ML Signal Lab

**Goal:** AI-assisted framework for designing, running, evaluating, and governing financial machine learning experiments with rigorous validation and methodology checks.

**Estimated effort:** 50-70 hours (6-8 weeks)

**Status:** Not started

**Prerequisites:** All previous projects complete

## Phase 1: Concept Lessons (~15-20 hours)

### [ ] P4-L1: Why ML for finance is hard (and why most attempts fail)
### [ ] P4-L2: Train/test/validation splits - and why random splits fail for time series
### [ ] P4-L3: Walk-forward validation (deeper)
### [ ] P4-L4: Rolling vs expanding windows
### [ ] P4-L5: Feature engineering for time series
### [ ] P4-L6: Leakage detection (the cardinal ML-in-finance sin)
### [ ] P4-L7: Classification vs regression for return prediction
### [ ] P4-L8: Bias-variance in financial ML
### [ ] P4-L9: Model interpretability (SHAP, feature importance)
### [ ] P4-L10: Model cards and ML documentation
### [ ] P4-L11: Overfitting detection methods
### [ ] P4-L12: Production model monitoring

## Phase 2: Architecture & Design (~6-8 hours)

### [ ] P4-Arch-1: ML pipeline design
### [ ] P4-Arch-2: Experiment tracking schema
### [ ] P4-Arch-3: Model card schema

## Phase 3: Build Sprints (~25-35 hours)

### [ ] P4-Build-1: Feature generation framework
### [ ] P4-Build-2: Walk-forward validation framework
### [ ] P4-Build-3: Model wrappers (linear, tree-based, simple neural)
### [ ] P4-Build-4: Leakage detector (analyzes feature definitions for time travel)
### [ ] P4-Build-5: Hyperparameter search with proper validation
### [ ] P4-Build-6: Model comparison framework
### [ ] P4-Build-7: SHAP/feature importance integration
### [ ] P4-Build-8: LLM-powered experiment design assistant
### [ ] P4-Build-9: Methodology reviewer (catches bad ML-for-finance practices)
### [ ] P4-Build-10: Model card auto-generator
### [ ] P4-Build-11: Streamlit dashboard

## Phase 4: Polish & Ship (~8-12 hours)

### [ ] P4-Eval: Methodology detection eval (seeded bad methodologies)
### [ ] P4-Polish-1: Product brief
### [ ] P4-Polish-2: README
### [ ] P4-Polish-3: Demo video
### [ ] P4-Polish-4: ML model risk and governance memo

**Resume bullet earned:**
> Built an AI ML Signal Lab for financial time-series research with walk-forward validation, leakage detection, SHAP-based interpretability, AI-assisted experiment design, automated methodology review, and model card generation.

---

# MASTERY MARKERS

Things you should be able to do after completing all 4 projects:

## Technical
- [ ] Build a Python project from empty repo to deployable Streamlit demo in under a week
- [ ] Design an LLM-powered system with structured outputs and validation guardrails
- [ ] Write an eval set for any AI feature you build
- [ ] Recognize and avoid look-ahead bias, survivorship bias, leakage, and overfitting in financial ML
- [ ] Implement a non-trivial event-driven simulation correctly
- [ ] Optimize a portfolio under constraints with multiple methods
- [ ] Translate ambiguous user requests into structured specifications

## Domain
- [ ] Explain factor investing to a non-quant
- [ ] Critique a backtest for methodology errors
- [ ] Discuss portfolio optimization tradeoffs intelligently
- [ ] Explain why ML for finance fails most of the time

## Product/Communication
- [ ] Write a clear product brief for an AI-native workflow
- [ ] Draw a system architecture diagram from memory
- [ ] Produce a 5-minute demo video that holds attention
- [ ] Explain any of your 4 projects in 5 minutes with no notes
- [ ] Discuss model risk, governance, and limitations honestly

---

# INTERVIEW PREPARATION PLAN

Once all 4 projects are shipped, before applying:

## Portfolio packaging (1-2 weeks, ~15 hours)
- [ ] Landing page that ties all 4 projects together as a coherent platform
- [ ] LinkedIn featured section showcasing all 4
- [ ] LinkedIn launch post with demo screenshots
- [ ] Resume rewrite with AI PM positioning
- [ ] Public writing: 1 long-form post breaking down a hard lesson from the journey

## Narrative practice (1 week, ~5 hours)
- [ ] 30-second elevator pitch on the pivot
- [ ] 5-minute walkthrough of any single project
- [ ] 10-minute deep-dive on the project most aligned with the role you're interviewing for
- [ ] Behavioral stories: 5 STAR-format stories from your build journey

## Interview practice (2 weeks, ~10 hours)
- [ ] Mock interview with someone in AI PM
- [ ] Practice live-coding small AI/LLM tasks
- [ ] Practice whiteboarding system architecture for AI features
- [ ] Practice product case interviews

---

# COMPLETION TRACKING

## Project status summary

| Project | Concepts | Architecture | Build | Polish | Shipped |
|---------|---------|--------------|-------|--------|---------|
| P1: Factor Research | ☐ 3/10 | ☐ 0/3 | ☐ 0/10 | ☐ 0/5 | ☐ |
| P2: Backtesting | ☐ 0/10 | ☐ 0/3 | ☐ 0/10 | ☐ 0/5 | ☐ |
| P3: Portfolio Construction | ☐ 0/11 | ☐ 0/3 | ☐ 0/11 | ☐ 0/4 | ☐ |
| P4: ML Signal Lab | ☐ 0/12 | ☐ 0/3 | ☐ 0/11 | ☐ 0/4 | ☐ |

## Aggregate metrics (update as you progress)

- Total lessons planned: 43
- Total build sprints planned: 42
- Total polish items planned: 18
- **Total trackable items:** 103

Update this monthly:

| Month | Lessons completed | Builds completed | Polish completed |
|-------|------------------|------------------|------------------|
| 2026-05 | 2 (P1-L1, P1-L2) | 0 | 0 |
| 2026-06 | - | - | - |
| 2026-07 | 1 (P1-L3) | 0 | 0 |

---

# NOTES ON THIS CURRICULUM

- Projects 2-4 lessons are sketched at title level; full content will be developed when you approach each project. Don't try to learn them ahead of time.
- Time estimates are honest based on your stated profile (10 hrs/week realistic, full-time employed, weak quant math foundation, decent Python). Adjust as you discover your actual pace through Project 1.
- After Project 1, the curriculum recalibrates. If P1 takes 4 weeks, P2-4 may compress. If it takes 12 weeks, the total target shifts.
- This curriculum focuses on shippable artifacts, not "I learned X." Hiring managers don't care what you learned; they care what you can do.
