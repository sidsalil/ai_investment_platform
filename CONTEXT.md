# AI Investment Platform - Context Journal

> Superseded a 4-project plan on 2026-07-11. Old files preserved as
> `CONTEXT_OLD_2026-05-25.md` and `curriculum_OLD_2026-05-25.md` for reference.
> Scope is now 2 projects (Factor Research Copilot, Backtesting Copilot),
> each expanded with an AI/agentic concept track, backtesting rigor, and
> evals/model-evals. Projects 3-4 (Portfolio Construction, ML Signal Lab)
> deprioritized, kept as reference only.

## Current State
- **Active project:** Project 1 - Factor Research Copilot
- **Active phase:** Phase 1 - Concept Lessons (2 of 10 finance lessons complete; AI/agentic + backtesting-rigor + evals tracks not started)
- **Last session:** 2026-05-25 - P1-L2 complete (universe definition, survivorship bias, point-in-time problem)
- **Next session goal:** P1-L3 - Returns (simple vs log, adjusted vs raw, total return vs price return)
- **Target start of Lesson 3:** Next available session
- **Note:** All progress logged before 2026-07-11 carries forward unchanged. Lesson numbering for the finance track (L1-L10) is untouched by this restructure.

## Career Pivot Decisions (cross-project)
- 2026-04-26 - Pivoting from quant research path to hands-on AI Product Manager
  roles in finance and AI-native firms
- 2026-04-26 - Confirmed I will not pursue WQU MScFE or pure quant researcher
  path; weak quant math foundation makes that low-EV given my profile of an established senior product manager
- 2026-04-26 - Stack decisions: Python 3.11, VS Code (not PyCharm), FastAPI,
  Streamlit, pandas/numpy/scipy, Anthropic API (claude-sonnet-4-6), Claude Code, Claude Agent SDK, MCP
- 2026-04-26 - Data source: yfinance to start, will upgrade to Polygon.io in Project 2
- 2026-04-26 - Working approach with Claude: 4 phases per project (Concept
  lessons → Architecture → Build sprints → Polish), intuition first then math,
  teach finance from scratch as if MS Financial Engineering student
- 2026-04-26 - Hard commitment: I write code with my own hands. No copy-paste
  of generated code without understanding and modifying it.
- 2026-04-26 - Conversation naming convention: P[#]-[Type]: [Topic] (e.g.,
  P1-L1, P1-LA1, P1-Arch, P1-Build, P1-Debug, P1-Eval, P1-Polish)
- 2026-04-26 - Will probe internal Fidelity AI roles in parallel with external
  applications - higher EV than initially assumed
- **2026-07-11 - Scope change: 4-project plan collapsed to 2 projects (Factor Research Copilot, Backtesting Copilot). Portfolio Construction and ML Signal Lab deprioritized. Trade-off is intentional: depth + AI/ML breadth per project over four shallower projects.**
- **2026-07-11 - Target roles expanded/shifted: AI Product Manager, Product Manager in Financial Services, and Forward Deployed Engineer. FDE assessment on record: frontier-lab FDE roles require professional SWE experience that a self-taught portfolio does not substitute for. This project portfolio strengthens FDE *conversations* (systems design, agent debugging, model evals) but is not treated as sufficient on its own for FDE hiring bars. AI PM and Financial Services PM remain the primary near-term targets.**
- **2026-07-11 - Backtesting rigor added to Project 1 (walk-forward validation, multiple-testing/p-hacking) since Project 2 no longer automatically covers this ground before P1 ships.**
- **2026-07-11 - Evals split into two explicit concepts across the curriculum: model evals (raw LLM capability/comparison) vs. system evals (does my specific pipeline work). Both get concept lessons; both get build artifacts.**

## Hours-Logged Tracker (new — start populating from PTO week, 2026-07-13)
Purpose: recalibrate the ~150-210 hour / 30-40 week estimate against real pace.

| Week of | Phase/Lesson worked | Hours logged | Notes |
|---------|---------------------|---------------|-------|
| 2026-07-13 | | | PTO block — target max P1 progress |

## Anthropic Courses Plan (mapped to monthly timeline)
- Month 1: Claude 101, AI Fluency: Framework & Foundations, Claude Code 101
- Month 2: Claude Code in Action, Building with Claude API (start)
- Month 3: Building with Claude API (finish), Intro to MCP
- Month 4: Intro to Agent Skills, Intro to Subagents
- Month 5: Intro to Claude Cowork, MCP Advanced Topics
- Month 6: AI Capabilities and Limitations, one cloud course (Bedrock or Vertex)
- Month 7: Other cloud course, revisit API course evals sections
- Months 8+: Stop course-taking, focus on interviewing (timeline now recalibrates against Hours-Logged Tracker rather than a fixed 9-month assumption)

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
- 2026-07-11: Scope restructured from 4 projects to 2, with AI/agentic, backtesting-rigor, and evals tracks added to Project 1. Target roles expanded to include FDE alongside AI PM and Financial Services PM.
- [date]: Shipped Project 1.
- [date]: Started Project 2.
- [date]: Shipped Project 2.
- [date]: Began external applications (can start once P1 build sprints are substantially complete — do not wait for 100% polish).

---

## Project 1: Factor Research Copilot

### Status
- Phase: Phase 1 (Concept Lessons) — Finance track 2/10 complete; AI/Agentic, Backtesting Rigor, and Evals tracks not started
- Started: 2026-05-25
- Target ship date: TBD — recalibrate after PTO week using Hours-Logged Tracker

### Concepts Learned — Finance Track

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

**P1-L3 through P1-L10:** Not yet started. See curriculum.md for lesson-by-lesson scope (returns, signal construction, portfolio construction, IC, factor decay/turnover, biases deep-dive, transaction costs, risk metrics).

### Concepts Learned — AI/Agentic Track
- Not yet started. See curriculum.md Phase 1 (AI/Agentic Track) for the full 14-lesson scope: agent fundamentals, tool use/function calling, MCP, structured outputs, ReAct-style loops, planning loops, subagent orchestration, context engineering, agent failure modes, observability/tracing, latency/cost tradeoffs, deployment basics, RAG fundamentals.

### Concepts Learned — Backtesting Rigor Track
- Not yet started. Added 2026-07-11 to close the gap left by deprioritizing Backtesting Copilot as project #1's dependency. Covers: walk-forward validation done properly, out-of-sample vs. in-sample discipline, multiple-testing/p-hacking problem.

### Concepts Learned — Evals & Model Evals Track
- Not yet started. Added 2026-07-11. Covers: model evals vs. system evals distinction, LLM-as-judge methodology, golden dataset/rubric design, eval metrics for structured/agentic output (task success rate, schema-validity rate, groundedness/faithfulness).

### Concepts I'm Still Shaky On
- (from P1-L2) Exact mechanics of constructing a survivorship-bias-free universe in practice — combining current tickers with delisted ones via a paid source. Revisit in P1-L8.
- (from P1-L2) Statistical machinery for quantifying survivorship bias's effect on a specific backtest (not just the qualitative direction). Revisit in P1-L8.
- (from P1-L2) Interaction of point-in-time universe with point-in-time fundamentals — restated earnings, late filings, accounting revisions. Revisit when fundamentals enter the picture in P1-Build-3 (value factor).

### Code Written
- (none yet)

### Decisions Made (P1-specific)
- 2026-05-25 — **Universe for Project 1: NASDAQ-100 during build sprints (fast iteration loops while learning the pipeline); switch to S&P 500 for the final eval and demo (the standard learner deliverable, deeper liquidity universe).** Survivorship bias acknowledged explicitly in P1-Polish-4 (methodology risk memo). The data ingestion module (P1-Build-1) must parameterize the universe so the NASDAQ-100 ↔ S&P 500 switch is a config change, not a refactor.
- **2026-07-11 — MCP and Claude Agent SDK timing resolved: both are in scope for Project 1 (not deferred to Project 2 as originally noted). P1-Build-1's data/tool layer will be exposed via an MCP server rather than a bespoke wrapper. This corrects an earlier contradiction between the custom-instructions file and this journal.**
- **2026-07-11 — Architecture will demonstrate the full agentic pattern range within this one project: main orchestrator agent (planning loop) delegates to a validation subagent and a memo-writing subagent (multi-agent orchestration), with tools exposed via MCP (tool-use loop). This is necessary because Project 1 is now the primary — not sole-early — demonstration vehicle.**
- **2026-07-11 — Model evals will include a concrete model-comparison build (e.g., larger vs. smaller Claude model) evaluating cost/latency/quality tradeoffs across the extractor, validator, and memo-writer subagents.**

### Open Questions
- (none open)

### Mistakes & Lessons
- (empty — will accumulate)

### Carried-Forward Action Items
Format: `(source lesson) → target phase: action`.

- **(P1-L2) → P1-Build-1 (data ingestion module):** Parameterize the universe so NASDAQ-100 ↔ S&P 500 switch is a config change. Universe constituents sourced from a stable public source (Wikipedia is the standard); freeze the snapshot date for reproducibility. Now also: expose via MCP server, not a bespoke wrapper.
- **(P1-L2) → P1-Polish-4 (methodology risk memo):** Include explicit "Universe choice and survivorship-bias acknowledgment" section. Document expected magnitude (~0.5–1.5%/year inflation on US equity universes; larger for hedge funds and small-caps). Describe the production fix path (CRSP / FactSet / S&P Dow Jones Indices point-in-time membership data) and why it was out of scope for the learning project.
- **(2026-07-11 planning) → P1-Build-5:** Add explicit in-sample vs. out-of-sample comparison to backtest mechanics, surfaced in the eval/demo output.
- **(2026-07-11 planning) → P1-Polish:** Add case-study one-pager (problem → user → key tradeoffs → what's next) and a systems-design writeup (architecture + failure modes handled), separate from the README.

---

## Project 2: Backtesting Copilot

### Status
- Phase: Not started
- Prerequisite: Project 1 shipped (or Phase 3 substantially complete)
- Purpose in portfolio: demonstrates event-driven systems architecture, planning + tool-use loop via Claude Agent SDK, and production-grade simulation mechanics — the "can you build a real system" complement to P1's "can you design a thoughtful AI product" story.

### Concepts Learned
- Not yet started. See curriculum.md for full scope.

### Code Written
- (none yet)

### Decisions Made (P2-specific)
- **2026-07-11 — Reinstated as project #2 after being briefly deprioritized in favor of ML Signal Lab. Chosen over ML Signal Lab and Portfolio Construction Copilot because it adds systems-engineering breadth (event-driven simulation, order/fill mechanics) that P1's expanded scope does not already cover, and is more directly relevant to FDE-flavored conversations than portfolio-optimization math.**
- Data source: Polygon.io (per original plan — first project to move off yfinance).

### Open Questions
- (none open)

---

## Project 3: Portfolio Construction Copilot
*Deprioritized 2026-07-11. Kept as reference only — not in active scope. See curriculum.md for original scope if revisited later.*

---

## Project 4: ML Signal Lab
*Deprioritized 2026-07-11. Kept as reference only — not in active scope. See curriculum.md for original scope if revisited later.*
