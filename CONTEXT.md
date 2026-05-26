# AI Investment Platform - Context Journal

## Current State
- **Active project:** Project 1 - Factor Research Copilot
- **Active phase:** Phase 1 - Concept Lessons (1 of 10 complete)
- **Last session:** 2026-05-25 - P1-L1 complete (What is a factor and why does anyone care)
- **Next session goal:** P1-L2 - The universe (what stocks am I testing on)
- **Target start of Lesson 2:** Next available session

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
- [date]: Shipped Project 1.
- [date]: Started Project 2.
- [date]: Began external applications.

---

## Project 1: Factor Research Copilot

### Status
- Phase: Phase 1 (Concept Lessons) — 1 of 10 lessons complete
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

### Concepts I'm Still Shaky On
- (none flagged yet from P1-L1)

### Code Written
- (none yet)

### Decisions Made (P1-specific)
- (none yet — first decision comes in P1-L2: which universe to use for the project)

### Open Questions
- (none open from P1-L1)

### Mistakes & Lessons
- (empty — will accumulate)

---

## Project 2: Backtesting Copilot
*Not started. Will populate when Project 1 ships.*

---

## Project 3: Portfolio Construction Copilot
*Not started. Will populate when Project 2 ships.*

---

## Project 4: ML Signal Lab
*Not started. Will populate when Project 3 ships.*
