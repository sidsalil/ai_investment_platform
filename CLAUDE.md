# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Code Ownership Policy (effective 2026-07-20)

**Default mode: the user writes code first; Claude's role is to review, diff, and suggest refactors — not to generate implementation code unprompted.** Full code generation only happens when explicitly requested (e.g., "generate this function," "write this for me"). This is an opt-in exception per instance, not a standing permission — do not infer permission to generate code from context alone; ask if unsure.

- **Permission mode: require approval on every file write.** Do not enable an "accept all" / auto-accept mode for this project — the comprehension gate below is only enforceable if every write is actually stopped and shown as a diff first.
- Claude Code generates on a branch, never directly to `main`.
- The gate before anything merges is **comprehension, not authorship**: every non-trivial decision in the diff must be explainable without prompting, regardless of whether the code was hand-written or AI-generated on request.
- Do NOT install the VS Code Claude Code extension — the CLI in an integrated terminal is the deliberate tool (its higher-friction UX supports the comprehension gate; the extension's one-click accept-all UX works against it).
- Diff review happens with explanation in chat/terminal, not just inline tool rationale — if asked "why," give the real reasoning behind a suggested change, not a restatement of the diff.

Track which components were hand-written vs. AI-generated-and-reviewed in CONTEXT.md.

## Development Environment

- OS: Windows 11 with WSL2 (Ubuntu 26.04 LTS) — all dev work runs inside WSL, not native Windows
- Python: 3.11.9 via pyenv (`~/.pyenv/`)
- Node: v24.16.0 via nvm (required for Claude Code CLI)
- Editor: VS Code on Windows, connected to WSL via Remote-WSL extension (this is separate from, and does not conflict with, the "no Claude Code VS Code extension" rule above)
- Project location: `~/projects/ai_investment_platform` (Linux filesystem)

## Claude Memory

Persistent, file-based memory for this project lives at `/home/sidsa/.claude/projects/-home-sidsa-projects-ai-investment-platform/memory/`, indexed by `MEMORY.md` in that directory.

## Commands

```bash
# Activate virtual environment (required every new terminal)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run a single test
pytest tests/<file>.py::test_function_name

# Lint
ruff check .

# Format
ruff format .

# Quick Anthropic API sanity check
python test_api.py

# Start Jupyter Lab
jupyter lab

# Start Streamlit UI (once built)
streamlit run <file>.py
```

## Project Architecture

Two-project portfolio for career transition to AI PM / Financial Services PM roles. **Project 3 and 4 are deprioritized — reference only.**

### Current State

Phase 1 (Concept Lessons) for Project 1 is **complete (32/32)**. Phase 2 (Architecture & Design) is **in progress**: P1-Arch-0 (Claude Code configuration and initial test) is complete. Next: P1-Arch-1 (system architecture diagram).

See `CONTEXT.md` for the authoritative state tracker, all design decisions, and carried-forward action items. See `curriculum.md` for the full lesson/build/polish checklist.

### Project 1: Factor Research Copilot (`modules/01_factor_research/`)

Planned 7-stage pipeline:

1. **Orchestrator** (stages 1–5): takes natural-language hypothesis → produces `FactorSpec` (Pydantic) → plans tool calls → runs factor calc + backtest pipeline
2. **Methodology validator subagent** (stage 6): independent review for look-ahead bias, survivorship bias, multiple-testing concerns, sector-bet contamination
3. **Research memo subagent** (stage 7): generates 1-page research memo with hypothesis, methodology, results, limitations

Data layer: MCP server wrapping yfinance (`shared/data/`) — serves OHLCV data as MCP tools.

Key locked design decisions:
- **Returns:** log returns for internal math; simple returns for cross-asset combination and reporting language
- **Price series:** always use adjusted close (not raw close) for return calculations
- **Signal pipeline order:** raw factor → winsorize (1st/99th percentile) → sector-neutral z-score (default); universe-wide z-score retained as diagnostic
- **Bucketing:** quintiles (5 buckets) default, deciles configurable
- **Portfolio:** long-short equal-weighted (research default); long-only top-quintile for practitioner-facing view
- **Rebalancing:** monthly (21 trading days); forward-return window is also 1-month
- **Primary eval metric:** rank IC (Spearman), robust to fat-tailed return outliers; Pearson IC as diagnostic
- **Transaction costs:** flat 10 bps one-way configurable parameter, applied to both legs of the long-short book (yfinance has no bid/ask data, so this is an assumed parameter, not computed from market data)
- **Beta neutrality:** explicitly out of scope — dollar-neutral only, disclosed limitation
- **Deployment:** direct Anthropic API call (no AWS Bedrock for P1)
- **Model selection:** `claude-sonnet-5` as the default/primary model project-wide; validator subagent stays on the stronger model (Sonnet 5); factor-spec extractor and memo-writer are candidates for a smaller/cheaper model (Haiku 4.5) pending evals

Pydantic schemas already designed (implement during Phase 3):
- `FactorSpec`: hypothesis_text, factor_type, universe, lookback_months, exclusion_months, rebalance_frequency, long_short
- `TraceEvent`: 7-type taxonomy — `perceive`, `reason`, `act`, `observe`, `escalation`, `subagent_invocation`, `subagent_result`
- `ValidationResult`: `passed` (bool), `flags` (list[str]), `severity` (Literal["none","advisory","blocking"]), used by methodology validator subagent — `passed: true` is a recommendation to a human accountable party, never a final decision

### Project 2: Backtesting Copilot (`modules/02_backtester/`)

Not started. Event-driven backtest engine + AI strategy parser. Builds on P1's patterns at production simulation scale. Adds model-routing layer (multi-model orchestration) in P2-Build-11.

## Directory Structure

```
modules/
  p1_factor_research/    # Project 1 code (build sprints P1-Build-1 through P1-Build-13)
  p2_backtester/         # Project 2 code (not started)
shared/
  data/                  # MCP server for yfinance data ingestion (P1-Build-1)
  llm/                   # Shared LLM utilities
  utils/                 # Shared Python utilities
notebooks/               # Jupyter notebooks for exploration/prototyping
tests/                   # Pytest test suite
docs/
  architecture/          # Architecture diagrams (P1-Arch-1 deliverable)
  product_briefs/        # PRDs (P1-Polish-1 deliverable)
  eval_reports/          # Eval reports (P1-Eval deliverable)
misc/
  notes/                 # Lesson notes (.md files) — read-only reference
  environment_setup.md   # Full WSL2/Python setup guide
```

## Stack

```
anthropic==0.97.0        # Claude API SDK — target model: claude-sonnet-5
pandas==2.2.3
numpy==2.1.3
scipy==1.14.1
jupyter==1.1.1
yfinance==1.3.0          # Market data; no bid/ask, no point-in-time index membership
fastapi==0.115.5
streamlit==1.40.2
pytest==8.3.4
ruff==0.8.2
```

API key lives in `.env` (gitignored), loaded via `python-dotenv`. Never hardcode.
