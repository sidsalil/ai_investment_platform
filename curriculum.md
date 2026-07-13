# AI Investment Platform - Curriculum

> Living curriculum for the (now 2-project) journey to AI Product Manager /
> Financial Services PM / Forward Deployed Engineer conversations.
> Last updated: 2026-07-13 (P1-L6 complete)
>
> **Superseded a 4-project plan.** Old versions preserved as
> `curriculum_OLD_2026-05-25.md` (pre-restructure) and
> `curriculum_OLD_2026-07-12.md` (progress through P1-L5, old single-track
> structure — this file merges that progress into the new structure).
> Projects 3-4 kept below as reference only — not in active scope.
>
> **Scope change rationale:** collapsed from 4 projects to 2 to trade
> breadth-across-projects for depth-within-projects, and to make room for an
> AI/agentic concept track, backtesting rigor, and evals/model-evals — none
> of which existed as explicit lessons in the original plan.
>
> **Target roles (as of 2026-07-11):** AI Product Manager, Product Manager —
> Financial Services, Forward Deployed Engineer. Standing caveat on FDE: this
> portfolio strengthens FDE *conversations* (systems design, agent debugging,
> model evals) but does not substitute for professional software engineering
> experience, which is what frontier-lab FDE hiring bars actually screen for.
> AI PM and Financial Services PM remain the primary near-term targets.

---

## How to use this document

- **Check off lessons as you complete them.** "Complete" means: concepts understood AND deliverables produced AND completion criteria met. Not "I read about it."
- **Lessons within a phase should generally be done in order.** The Finance track and AI/Agentic track within Phase 1 are designed to interleave — do the AI/agentic lesson that unlocks a given finance concept's implementation around the same time. They're tracked separately so existing progress isn't disrupted; as of this update the Finance track is 6 lessons ahead of the AI/Agentic track, so consider doing P1-LA1 next alongside P1-L7 to bring them closer together.
- **Time estimates assume focused work, not calendar time.**
- **Update CONTEXT.md after every lesson.** This curriculum tracks what's done; CONTEXT.md tracks where you are now.
- **One lesson ≈ one Claude conversation, typically.**
- **Don't skip the "Explain it back" checkpoints.**
- **Log hours in CONTEXT.md's Hours-Logged Tracker.** The estimate below is largely untested against your actual pace — recalibrate using real data as you go.

---

## Cross-Project Meta-Skills

| Skill | After P1 | After P2 |
|-------|----------|----------|
| Python (pandas, numpy) | Strong | Production |
| Quant finance vocabulary | Factor research + backtesting rigor | + event-driven backtesting mechanics |
| Agentic AI (tool use → orchestration) | Tool use, MCP, planning loops, subagent orchestration | Planning loop via Agent SDK, applied at production scale |
| Evaluation discipline | Model evals + system evals, regression eval suite | Strategy-quality reviewer subagent, iterating evals |
| Product thinking | Product brief, case study, systems-design writeup | Architecture maturity, robustness memo |
| Financial data handling | Time series, walk-forward, out-of-sample discipline | Multi-asset, event simulation |
| Methodology rigor | Look-ahead, survivorship, multiple-testing awareness | Full walk-forward validation, slippage/cost realism |

---

# PROJECT 1: Factor Research Copilot

**Goal:** Build an AI agent system that converts natural-language investment hypotheses into Python-based factor research with statistical validation, methodology checks, and auto-generated research memos — architected to demonstrate the full agentic pattern range (tool use, planning, multi-agent orchestration) in one system, with rigorous backtesting and both model- and system-level evals.

**Estimated effort:** ~100-140 hours

**Status:** In progress — Phase 1 (Concept Lessons), Finance track 6/10 complete

## Phase 1: Concept Lessons — Finance Track (~15-25 hours)

### [x] P1-L1: What is a factor and why does anyone care? — **completed 2026-05-25**
- **Concepts:** What a factor is, why factor investing exists, the major historical factors (value, momentum, size), CAPM → Fama-French history
- **Deliverable:** Notes in CONTEXT.md under "Concepts Learned — Finance Track"
- **Estimated time:** 1-2 hours

### [x] P1-L2: The universe - what stocks am I testing on? — **completed 2026-05-25**
- **Concepts:** Why we restrict the universe, survivorship bias intro, the S&P 500 as a starting universe, point-in-time universe problem
- **Decision logged:** NASDAQ-100 for development → S&P 500 for final eval/demo. Survivorship bias acknowledged in P1-Polish-4.
- **Estimated time:** 1 hour

### [x] P1-L3: Returns - the foundation everything builds on — **completed 2026-07-12**
- **Concepts:** Simple vs log returns, when each is appropriate, adjusted vs raw prices (dividends, splits), total return vs price return
- **Deliverable:** Notes (P1_L3_Returns.md); a small Jupyter notebook computing both return types on AAPL data (hand-written per coding-ownership rule)
- **Decision logged:** Log returns for internal factor/backtest math; simple returns for cross-asset combination and reporting language. Adjusted close is the required default price series for all return calculations.
- **Estimated time:** 1-2 hours

### [x] P1-L4: Signal construction - turning data into predictions — **completed 2026-07-12**
- **Concepts:** Raw factors vs normalized factors, z-scoring, winsorization, sector neutralization (intuition)
- **Deliverable:** Notes (P1_L4_Signal_Construction.md); worked 8-stock numerical example covering z-scoring, winsorization, and sector-neutral z-scoring
- **Decision logged:** Signal construction pipeline order is raw factor → winsorize (1st/99th percentile default, configurable) → sector-neutral z-score. Sector-neutral z-scoring is the default signal for portfolio construction; universe-wide z-scoring retained as an optional diagnostic to detect sector-bet contamination.
- **Estimated time:** 2 hours

### [x] P1-L5: Portfolio construction from signals — **completed 2026-07-12**
- **Concepts:** Decile/quintile portfolios, long-only vs long-short, equal weighting vs signal weighting
- **Deliverable:** Notes (P1_L5_Portfolio_Construction.md); hand-computed quintile example for 20 stocks with equal-weight and signal-weight long-short portfolios
- **Decision logged:** Quintile bucketing (5 buckets) as default, deciles configurable for the S&P 500 final run. Long-short equal-weighted is the research/IC default from P1-L6 onward; long-only equal-weighted top-quintile retained as a practitioner-facing alternative for the memo. Signal-weighting retained as a configurable diagnostic.
- **Estimated time:** 1-2 hours

### [x] P1-L6: Information Coefficient and statistical evaluation — **completed 2026-07-13**
- **Concepts:** IC, rank IC, Information Ratio, hit rate, t-statistics for IC, what "predictive" actually means statistically
- **Deliverable:** Notes (P1_L6_Information_Coefficient.md); worked 10-stock example covering Pearson IC, rank IC (Spearman), hit rate, single-period and time-series t-statistics, and a 6-month IR calculation
- **Decision logged:** Rank IC (Spearman) is the primary headline metric for Project 1 reporting (robust to fat-tailed return outliers); Pearson IC retained as diagnostic. IR and time-series t-statistic (t = IR × √T) must be computed across the full backtest window rather than reported for a single period, to avoid cherry-picking.
- **Estimated time:** 2 hours

### [ ] P1-L7: Factor decay and turnover
- **Concepts:** How long signals predict (1-day, 1-week, 1-month forward returns), decay curves, turnover, the turnover-cost relationship
- **Deliverable:** Notes
- **Estimated time:** 1-2 hours

### [ ] P1-L8: The biases that kill backtests
- **Concepts:** Look-ahead bias (deep), survivorship bias (deep), selection bias, data snooping
- **Deliverable:** Notes; a "methodology gotchas" cheat sheet for your repo
- **Estimated time:** 2-3 hours - **this lesson matters more than most**

### [ ] P1-L9: Transaction costs and real-world frictions
- **Concepts:** Bid-ask spread, market impact, commissions, the gap between backtest and live performance
- **Deliverable:** Notes; cost assumptions to use in Project 1
- **Estimated time:** 1-2 hours

### [ ] P1-L10: Risk and performance metrics
- **Concepts:** Sharpe ratio, Sortino, max drawdown, drawdown duration, Calmar, beta-to-market
- **Deliverable:** Notes; a "metrics glossary" for your repo
- **Estimated time:** 1-2 hours

## Phase 1: Concept Lessons — AI/Agentic Track (~20-25 hours)

### [ ] P1-LA1: What is an LLM agent
- **Concepts:** Agent vs. chatbot vs. fixed workflow; the perceive-reason-act loop
- **Estimated time:** 1 hour

### [ ] P1-LA2: Tool use / function calling fundamentals
- **Concepts:** How a model decides to call a tool, tool schemas, the request/response cycle
- **Estimated time:** 1-2 hours

### [ ] P1-LA3: MCP (Model Context Protocol)
- **Concepts:** Client/server architecture, why MCP exists vs. bespoke API integration per tool, how it applies to the data ingestion layer
- **Estimated time:** 2 hours

### [ ] P1-LA4: Structured outputs & schema validation
- **Concepts:** Pydantic models, why structured outputs matter for reliability, schema validation as a guardrail
- **Estimated time:** 1-2 hours

### [ ] P1-LA5: ReAct-style tool-use loops
- **Concepts:** Reason-then-act pattern, when a single tool-use loop is sufficient
- **Estimated time:** 1-2 hours

### [ ] P1-LA6: Planning loops
- **Concepts:** Multi-step planning vs. reactive tool use, when an agent needs to plan ahead vs. react turn-by-turn
- **Estimated time:** 1-2 hours

### [ ] P1-LA7: Subagents & multi-agent orchestration
- **Concepts:** Orchestrator-worker pattern, when to decompose a task across agents, how results get merged back
- **Estimated time:** 2 hours

### [ ] P1-LA8: Context engineering
- **Concepts:** Context window management, system prompt design, what belongs in context vs. what gets fetched on demand
- **Estimated time:** 1-2 hours

### [ ] P1-LA9: Agent failure modes
- **Concepts:** Infinite loops, hallucinated tool calls, malformed outputs, retry/backoff strategy, timeout handling
- **Estimated time:** 1-2 hours

### [ ] P1-LA10: Observability & tracing for agentic systems
- **Concepts:** Logging tool calls and agent decisions, debugging *why* an agent did what it did
- **Estimated time:** 1-2 hours

### [ ] P1-LA11: Latency & cost tradeoffs
- **Concepts:** Token economics, model selection tradeoffs, when a smaller/cheaper model is the right call
- **Estimated time:** 1 hour

### [ ] P1-LA12: Deployment basics
- **Concepts:** Containerization intuition, environment config, basic AWS Bedrock deployment
- **Estimated time:** 2 hours

### [ ] P1-LA13: RAG fundamentals
- **Concepts:** Retrieval-augmented generation, when it's relevant to a research-copilot document-lookup use case
- **Estimated time:** 1-2 hours

### [ ] P1-LA14: Prompt engineering fundamentals
- **Concepts:** Few-shot examples, chain-of-thought prompting, structured prompting patterns
- **Estimated time:** 1 hour

## Phase 1: Concept Lessons — Backtesting Rigor Track (~4-6 hours)

### [ ] P1-LB1: Walk-forward validation done properly
- **Concepts:** Rolling vs. expanding windows, train/test discipline over time, why naive monthly rebalancing isn't the same as proper walk-forward validation
- **Estimated time:** 1-2 hours

### [ ] P1-LB2: Out-of-sample vs. in-sample discipline
- **Concepts:** What "out-of-sample" actually means in a backtest context, how to structure a test split for time series
- **Deliverable:** In-sample vs. out-of-sample comparison built into P1-Build-5
- **Estimated time:** 1-2 hours

### [ ] P1-LB3: The multiple-testing problem (p-hacking)
- **Concepts:** Why testing many factor variants and reporting only the best one is dishonest, correction approaches (intuition level)
- **Explain back:** "I tested momentum, volatility, and value — why can't I just report whichever had the best backtest?"
- **Estimated time:** 1-2 hours

## Phase 1: Concept Lessons — Evals & Model Evals Track (~1-2 hours)

### [ ] P1-LE1: Model evals vs. system evals
- **Concepts:** Model evals test the underlying LLM's raw capability (benchmark-style); system evals test your specific pipeline end-to-end. Why interviewers care about the distinction.
- **Sub-concepts:** LLM-as-judge methodology (and its failure modes — verbosity bias, self-preference bias); golden dataset and rubric design; eval metrics for structured/agentic output (task success rate, schema-validity rate, groundedness/faithfulness)
- **Estimated time:** 1-2 hours

**Phase 1 completion criteria:**
- All Finance, AI/Agentic, Backtesting Rigor, and Evals lessons checked off
- You can explain factor research AND the agent architecture end-to-end to a non-technical friend in 10 minutes
- CONTEXT.md "Concepts Learned" sections are populated with your own-words summaries across all four tracks

## Phase 2: Architecture & Design (~7-11 hours)

### [ ] P1-Arch-1: System design
- **Deliverable:** Architecture diagram showing the major components (data layer via MCP, factor calc, portfolio construction, metrics, LLM orchestrator, validation subagent, memo subagent, tracing, UI)
- **Stored at:** `docs/architecture/project_01_factor_research.md`
- **Estimated time:** 2-3 hours

### [ ] P1-Arch-2: Data flow design
- **Deliverable:** Sequence diagram or written walkthrough: "User asks 'test momentum on S&P 500' → orchestrator plans → calls MCP tools → delegates to validation subagent → delegates to memo subagent → produces output"
- **Estimated time:** 1-2 hours

### [ ] P1-Arch-3: Orchestrator + subagent design
- **Concepts applied:** How the main agent's planning loop delegates to the validation subagent and memo-writing subagent, what gets passed between them, how failures propagate
- **Estimated time:** 2-3 hours

### [ ] P1-Arch-4: Module structure and interfaces
- **Deliverable:** A skeleton of Python file/function signatures (no implementation)
- **Estimated time:** 2-3 hours

**Phase 2 completion criteria:**
- You can draw the full architecture (including orchestrator/subagent/MCP layers) on a whiteboard from memory
- A junior developer could read your architecture doc and understand the system without asking you questions
- Your skeleton compiles (even if functions just `pass`)

## Phase 3: Build Sprints (~44-61 hours)

### [ ] P1-Build-1: Data ingestion module (MCP server)
- **What you build:** An MCP server wrapping yfinance that downloads, caches, and serves clean OHLCV data for a list of tickers — replaces a bespoke wrapper with a proper MCP tool interface
- **Key concerns:** Caching, handling failures, date alignment
- **Carried-forward requirement (from P1-L2, P1-L3):** Parameterize the universe so NASDAQ-100 ↔ S&P 500 switch is a config change. Source constituents from a stable public source (Wikipedia standard); freeze snapshot date for reproducibility. Confirm exact yfinance adjusted-close column name/behavior at implementation time. Cache invalidation must treat a new dividend/split as invalidating the entire cached adjusted-close series for that ticker.
- **Located in:** `shared/data/`
- **Tests:** Pytest tests that verify caching works and bad inputs fail cleanly
- **Estimated time:** 5-7 hours

### [ ] P1-Build-2: Factor calculation - Momentum
- **What you build:** A function that computes 12-month-minus-1-month momentum for a universe of stocks at a date
- **Key concerns:** Point-in-time correctness, NaN handling, vectorization
- **Carried-forward requirement (from P1-L4):** Winsorization (1st/99th percentile default, configurable) applied before z-scoring; sector-neutral z-scoring as the default signal path, universe-wide as diagnostic flag.
- **Located in:** `modules/01_factor_research/`
- **Estimated time:** 3-4 hours

### [ ] P1-Build-3: Factor calculation - Other factors
- **What you build:** Volatility factor (rolling std of returns), liquidity factor (dollar volume), simple value factor if data available
- **Carried-forward requirement (from P1-L4):** Same winsorization + sector-neutral z-scoring pipeline as P1-Build-2. Requires a sector classification data source (GICS sector via yfinance `.info`, or a static mapping) — confirm reliability at build time.
- **Estimated time:** 3-4 hours

### [ ] P1-Build-4: Portfolio construction
- **What you build:** Take a factor signal at a date, build long-only quintile portfolios and long-short top-vs-bottom quintile portfolio
- **Carried-forward requirement (from P1-L5):** Default to quintile bucketing (5 buckets), configurable to deciles. Implement both long-short equal-weighted (research/IC default) and long-only equal-weighted top-quintile (practitioner-facing alternative), plus a signal-weighted option. Deterministic tie-breaking rule for stocks straddling bucket boundaries (e.g., secondary sort by ticker or market cap).
- **Estimated time:** 3-4 hours

### [ ] P1-Build-5: Backtest mechanics (+ in-sample/out-of-sample)
- **What you build:** Walk forward in time, rebalance portfolio monthly, accumulate returns, apply transaction costs, and explicitly surface in-sample vs. out-of-sample performance side by side
- **Key concerns:** No look-ahead bias, realistic costs, proper walk-forward structure (per P1-LB1/LB2)
- **Estimated time:** 5-7 hours - **the hardest build sprint**

### [ ] P1-Build-6: Metrics calculation
- **What you build:** Compute IC, decile spreads, Sharpe, drawdown, turnover from backtest results
- **Estimated time:** 2-3 hours

### [ ] P1-Build-7: LLM integration - Natural language → factor spec (orchestrator)
- **What you build:** The main orchestrator agent's planning loop: takes "test 12-month momentum on the S&P 500," produces a structured FactorSpec object, plans the sequence of tool calls needed
- **Key concept:** Structured outputs, schema validation, planning loop (per P1-LA6)
- **Estimated time:** 4-6 hours

### [ ] P1-Build-8: Methodology validator (subagent)
- **What you build:** A validation subagent, delegated to by the orchestrator, that flags suspicious factor specs (look-ahead suspects, unrealistic assumptions, statistical/multiple-testing concerns)
- **This is your AI PM/FDE differentiator** — shows you understand model risk and multi-agent delegation
- **Carried-forward requirement (from P1-L4):** Flag signals where the universe-wide z-score and sector-neutral z-score diverge sharply for many stocks in the same direction — a diagnostic for a signal that's really a disguised sector bet.
- **Estimated time:** 5-6 hours

### [ ] P1-Build-9: Research memo generator (subagent)
- **What you build:** A memo-writing subagent, delegated to by the orchestrator, that takes backtest results and generates a 1-page research memo with hypothesis, methodology, results, limitations
- **Estimated time:** 4-5 hours

### [ ] P1-Build-10: Tracing / observability layer
- **What you build:** Logging for every tool call and agent decision, so you can debug and explain *why* the agent did what it did
- **Estimated time:** 2-3 hours

### [ ] P1-Build-11: Model comparison eval
- **What you build:** Run the extractor/validator/memo-writer subagents on two different models (e.g., larger vs. smaller Claude model), compare cost, latency, and quality — your model-evals artifact in practice
- **Estimated time:** 2-3 hours

### [ ] P1-Build-12: Deployment
- **What you build:** Containerize the system and deploy to a hosted endpoint (AWS Bedrock), not just local
- **Estimated time:** 3-5 hours

### [ ] P1-Build-13: Streamlit UI
- **What you build:** Web interface where user types a question, sees factor running, gets charts + memo
- **Estimated time:** 4-6 hours

**Phase 3 completion criteria:**
- You can run the full pipeline end-to-end: type a question → orchestrator plans → MCP tools execute → validator subagent runs → memo subagent runs → get charts + memo
- All build sprints have working code with at least one test each
- The validator catches at least 5 different methodology mistakes you've intentionally seeded
- The system is reachable via a live hosted endpoint, not just local code

## Phase 4: Polish & Ship (~13-20 hours)

### [ ] P1-Eval: Build the regression eval set
- **What you build:** 25 natural-language prompts, each with an expected factor spec output, re-runnable as a regression suite whenever prompts/models change. Includes the model-comparison results from P1-Build-11 and a paragraph on what production eval/monitoring would look like.
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
- **Estimated time:** 1-2 hours

### [ ] P1-Polish-4: Methodology risk memo
- **What you write:** Honest accounting of what your project does NOT do (point-in-time data, survivorship bias, no slippage modeling)
- **Carried-forward requirement (from P1-L2, P1-L3, P1-L5):** Include explicit "Universe choice and survivorship-bias acknowledgment" section, expected magnitude, production fix path. Note yfinance's unreliable delisting-return capture. Note the long-only vs long-short distinction and why long-short is used for research validity.
- **Estimated time:** 1 hour

### [ ] P1-Polish-5: Case-study one-pager
- **What you write:** One page: problem → user → key tradeoff decisions (universe choice, subagent orchestration vs. single loop, model selection for cost/latency) → what you'd build next. This is the artifact you actually walk an interviewer through.
- **Estimated time:** 1-2 hours

### [ ] P1-Polish-6: Systems-design writeup
- **What you write:** The kind of doc you'd whiteboard through in an interview — agent architecture, MCP layer, subagent delegation, and the failure modes you handled.
- **Estimated time:** 2-3 hours

**PROJECT 1 COMPLETION CRITERIA:**
- All lessons (four Phase-1 tracks) + builds + polish items checked off
- Working demo someone else can run from your README, plus a live hosted endpoint
- Demo video recorded
- Product brief, README, eval report, risk memo, case study, systems-design writeup all in your repo
- Repo pushed to GitHub, ready for portfolio link
- You can explain the project — including the agent architecture and eval methodology — to a hiring manager in 5 minutes with no notes

**Resume bullet earned:**
> Built an agentic AI Factor Research system (planning-loop orchestrator + subagent delegation via MCP) that converts natural-language investment hypotheses into Python-based factor tests with IC analysis, walk-forward validation, decile returns, transaction-cost sensitivity, model-comparison evals, and automated research memos with methodology risk caveats.

---

# PROJECT 2: Backtesting Copilot

**Goal:** AI-assisted strategy backtesting where users describe strategies in natural language and get rigorous, event-driven backtests with realistic frictions, automated quality review, and benchmark comparison — the systems-engineering complement to Project 1.

**Estimated effort:** ~50-70 hours

**Status:** Not started

**Prerequisites:** Project 1 complete (or Phase 3 substantially complete); understanding of factor research, returns, transaction costs, walk-forward validation

## Phase 1: Concept Lessons (~10-15 hours)

### [ ] P2-L1: Backtest vs paper trading vs live
### [ ] P2-L2: Event-driven vs vectorized backtesting
- Architecture choice with major downstream implications
### [ ] P2-L3: Position sizing schemes
- Equal weight, volatility-weighted, signal-weighted, Kelly intuition
### [ ] P2-L4: Rebalancing frequency tradeoffs
### [ ] P2-L5: Transaction costs deeper
- Bid-ask, market impact, commission structures, model choices
### [ ] P2-L6: Slippage modeling
### [ ] P2-L7: Walk-forward validation (applied at engine level)
- Builds directly on P1-LB1/LB2 — now implemented inside an event-driven engine
### [ ] P2-L8: Out-of-sample testing
### [ ] P2-L9: Multiple testing problem (p-hacking) — applied
- Builds directly on P1-LB3
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
- Uses Claude Agent SDK planning loop — applied version of P1-LA6
### [ ] P2-Build-7: Backtest quality reviewer (subagent)
- Applied version of P1-LA7 subagent orchestration, at production-simulation scale
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
> Built an AI Backtesting Copilot (event-driven simulation engine, Claude Agent SDK planning loop) that transforms natural-language trading strategy descriptions into executable Python backtests with transaction costs, slippage, turnover analysis, exposure controls, benchmark comparison, and an automated strategy-quality reviewer subagent.

---

# PROJECT 3: Portfolio Construction Copilot *(deprioritized 2026-07-11 — reference only)*

**Goal:** Convert natural-language portfolio constraints into optimized portfolios using multiple optimization approaches, with risk decomposition, scenario analysis, and tradeoff explanation.

**Estimated effort:** 45-60 hours | **Status:** Not started, not in active scope

<details>
<summary>Original scope (collapsed)</summary>

## Phase 1: Concept Lessons (~12-18 hours)
P3-L1 Portfolio theory basics · P3-L2 Mean-variance optimization (Markowitz) · P3-L3 Why max-Sharpe is unstable · P3-L4 Covariance estimation problems · P3-L5 Covariance shrinkage (Ledoit-Wolf) · P3-L6 Risk parity intuition · P3-L7 Risk contribution analysis · P3-L8 Constrained optimization · P3-L9 Tracking error and active risk · P3-L10 Scenario analysis and stress testing · P3-L11 VaR vs CVaR

## Phase 2: Architecture & Design (~5-7 hours)
P3-Arch-1 Optimizer abstraction · P3-Arch-2 Constraint specification language · P3-Arch-3 Module structure

## Phase 3: Build Sprints (~20-30 hours)
P3-Build-1 Equal-weight/min-variance optimizers · P3-Build-2 Max-Sharpe optimizer · P3-Build-3 Risk parity optimizer · P3-Build-4 Covariance estimation · P3-Build-5 Constraint engine · P3-Build-6 Risk decomposition · P3-Build-7 Scenario shock framework · P3-Build-8 LLM constraint extractor · P3-Build-9 Infeasible-constraint detection · P3-Build-10 Comparison/explanation layer · P3-Build-11 Streamlit UI

## Phase 4: Polish & Ship (~8-12 hours)
P3-Eval · P3-Polish-1 Product brief · P3-Polish-2 README · P3-Polish-3 Demo video · P3-Polish-4 Governance & risk-controls memo

**Resume bullet:**
> Built an AI Portfolio Construction Copilot that converts natural-language investment constraints into optimized portfolios comparing equal-weight, minimum-variance, max-Sharpe, and risk-parity allocations with covariance shrinkage, risk decomposition, scenario shocks, and infeasibility detection.

</details>

---

# PROJECT 4: ML Signal Lab *(deprioritized 2026-07-11 — reference only)*

**Goal:** AI-assisted framework for designing, running, evaluating, and governing financial machine learning experiments with rigorous validation and methodology checks.

**Estimated effort:** 50-70 hours | **Status:** Not started, not in active scope

<details>
<summary>Original scope (collapsed)</summary>

## Phase 1: Concept Lessons (~15-20 hours)
P4-L1 Why ML for finance is hard · P4-L2 Train/test/validation splits for time series · P4-L3 Walk-forward validation (deeper) · P4-L4 Rolling vs expanding windows · P4-L5 Feature engineering for time series · P4-L6 Leakage detection · P4-L7 Classification vs regression · P4-L8 Bias-variance · P4-L9 Model interpretability (SHAP) · P4-L10 Model cards · P4-L11 Overfitting detection · P4-L12 Production model monitoring

## Phase 2: Architecture & Design (~6-8 hours)
P4-Arch-1 ML pipeline design · P4-Arch-2 Experiment tracking schema · P4-Arch-3 Model card schema

## Phase 3: Build Sprints (~25-35 hours)
P4-Build-1 Feature generation · P4-Build-2 Walk-forward validation framework · P4-Build-3 Model wrappers · P4-Build-4 Leakage detector · P4-Build-5 Hyperparameter search · P4-Build-6 Model comparison framework · P4-Build-7 SHAP integration · P4-Build-8 LLM experiment design assistant · P4-Build-9 Methodology reviewer · P4-Build-10 Model card auto-generator · P4-Build-11 Streamlit dashboard

## Phase 4: Polish & Ship (~8-12 hours)
P4-Eval · P4-Polish-1 Product brief · P4-Polish-2 README · P4-Polish-3 Demo video · P4-Polish-4 ML model risk and governance memo

**Resume bullet:**
> Built an AI ML Signal Lab for financial time-series research with walk-forward validation, leakage detection, SHAP-based interpretability, AI-assisted experiment design, automated methodology review, and model card generation.

</details>

---

# MASTERY MARKERS

## Technical
- [ ] Build a Python project from empty repo to deployable, hosted demo
- [ ] Design an LLM-powered agentic system: tool use, planning loop, and multi-agent orchestration
- [ ] Design and implement an MCP server as a tool/data layer
- [ ] Write both a model eval and a system eval for an AI feature you build
- [ ] Recognize and avoid look-ahead bias, survivorship bias, multiple-testing bias, and overfitting in financial research
- [ ] Implement a non-trivial event-driven simulation correctly
- [ ] Debug an agent failure mode (loop, hallucinated call) using a tracing/observability layer
- [ ] Translate ambiguous user requests into structured specifications

## Domain
- [ ] Explain factor investing to a non-quant
- [ ] Critique a backtest for methodology errors, including multiple-testing/p-hacking
- [ ] Explain the tradeoffs between model evals and system evals
- [ ] Discuss agent architecture (tool use vs. planning vs. orchestration) intelligently

## Product/Communication
- [ ] Write a clear product brief and a one-page case study for an AI-native workflow
- [ ] Draw a full system architecture diagram (including agent/MCP layers) from memory
- [ ] Produce a 5-minute demo video that holds attention
- [ ] Explain either project in 5 minutes with no notes
- [ ] Discuss model risk, governance, evals, and limitations honestly

---

# PORTFOLIO COMPLETION & APPLICATION READINESS

Applies once Project 1 (and ideally Project 2) are substantially built. Do not wait for 100% polish across both projects before starting to apply — start once P1's build sprints are substantially done and a rough demo exists; finish polish in parallel with early-stage interview pipeline.

### [ ] Resume rewrite
- Both existing tailored resumes (AI PM version, Applied AI/Solutions Engineer version) were written assuming four shipped projects. Rewrite for the real 2-project scope with the depth this scope actually earned — one deep agentic system beats four described in a sentence each, but bullet language needs to reflect that, not just get trimmed.
- Add a third resume variant or section addressing Forward Deployed Engineer conversations specifically, leaning on systems-design writeup, agent debugging, and model-evals artifacts — without overclaiming production SWE experience.

### [ ] Live, hosted demo
- Not just local code or a video. A link an interviewer can click during the conversation. Covered by P1-Build-12 (deployment).

### [ ] STAR-format interview stories (3-5)
- Pulled from the actual build as you hit them, not written retroactively. Strong candidates: debugging an agent infinite loop, a methodology mistake the validator caught, the model-comparison tradeoff decision, a walk-forward/OOS surprise.

### [ ] One piece of public writing
- LinkedIn post or short article on one hard decision from the build (subagent design, or eval methodology). Signals communication ability for PM roles specifically.

### [ ] Fidelity-workflow translation paragraph
- For Financial Services PM roles: one paragraph connecting the copilot's design choices to a real asset-management research desk problem — domain fluency layered on top of the technical build.

### [ ] LinkedIn updates
- GitHub links, project descriptions, Featured section content — low-risk, can do now. Headline changes and Open to Work badge remain deferred per existing discreet-search preference.

### [ ] Decision point: when to start applying
- Recommended: once P1 Phase 3 (Build Sprints) is substantially complete and a rough demo exists — do not wait for full Phase 4 polish across both projects. Polish finishes in parallel with early pipeline activity.

---

# COMPLETION TRACKING

## Project status summary

| Project | Concepts | Architecture | Build | Polish | Shipped |
|---------|---------|--------------|-------|--------|---------|
| P1: Factor Research (Finance) | ☐ 6/10 | ☐ 0/4 | ☐ 0/13 | ☐ 0/6 | ☐ |
| P1: Factor Research (AI/Agentic) | ☐ 0/14 | — | — | — | — |
| P1: Factor Research (Backtesting Rigor) | ☐ 0/3 | — | — | — | — |
| P1: Factor Research (Evals) | ☐ 0/1 | — | — | — | — |
| P2: Backtesting Copilot | ☐ 0/10 | ☐ 0/3 | ☐ 0/10 | ☐ 0/5 | ☐ |
| ~~P3: Portfolio Construction~~ | deprioritized | — | — | — | — |
| ~~P4: ML Signal Lab~~ | deprioritized | — | — | — | — |

## Aggregate metrics (2-project scope)

- Total P1 lessons planned: 10 (finance) + 14 (AI/agentic) + 3 (backtesting rigor) + 1 (evals) = 28
- Total P1 build sprints planned: 13
- Total P1 polish items planned: 6
- Total P2 lessons planned: 10
- Total P2 build sprints planned: 10
- Total P2 polish items planned: 5
- **Total trackable items (active scope):** 72
- **Total estimated hours (active scope):** ~150-210 hours (~100-140 for P1, ~50-70 for P2)

Update monthly:

| Month | Lessons completed | Builds completed | Polish completed |
|-------|------------------|------------------|------------------|
| 2026-05 | 2 (P1-L1, P1-L2) | 0 | 0 |
| 2026-07 | 4 (P1-L3, P1-L4, P1-L5, P1-L6) | 0 | 0 |

---

# NOTES ON THIS CURRICULUM

- Project 2 lessons are sketched at title level for now (per original plan); full content develops when you approach it. Don't try to learn it ahead of time.
- Time estimates are a first-pass estimate, not a commitment — you have zero hours logged against the new AI/agentic, backtesting-rigor, or evals tracks yet. Recalibrate using CONTEXT.md's Hours-Logged Tracker.
- This curriculum focuses on shippable, interview-ready artifacts, not "I learned X." Hiring managers care what you can do and explain, not what you read about.
- Projects 3 and 4 remain fully scoped below (collapsed) in case priorities shift again later — no work needed to revive them, just uncollapse and resume.
