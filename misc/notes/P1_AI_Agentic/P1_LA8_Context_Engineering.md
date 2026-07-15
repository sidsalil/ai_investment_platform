# P1-LA8: Context Engineering

## 1. The problem this lesson solves

Every LLM call — whether it's the orchestrator's own reasoning or a subagent's — happens inside a **context window**: the total amount of text (measured in tokens) the model can "see" at the moment it generates a response. Nothing outside that window exists to the model. Not because it's forgotten somewhere — it's simply not there. There's no background memory the model can quietly check.

Think of it like a **trading desk with a fixed amount of physical desk space**. You can't have every research report, every historical price chart, and every client email spread out in front of you at once — the desk isn't big enough, and even if it were, you'd lose track of what actually matters buried under the pile. You bring the folder relevant to the trade you're making right now, and you swap it out when you move to the next task. **Context engineering** is the discipline of deciding what goes on the desk, in what form, and when it gets swapped out — instead of just dumping every document you own onto the desk and hoping the model finds the right page.

This matters for a very practical reason in our Project 1 architecture: our orchestrator runs a 7-stage pipeline (from P1-LA7: data fetch → signal construction → validation → metrics → ... → memo), and at each stage it's tempting to just keep feeding everything from every prior stage into context "to be safe." That instinct is exactly what this lesson pushes back on.

## 2. Core definitions (in order of first use)

| Term | Plain-language definition | Analogy |
|---|---|---|
| **Context window** | The total slice of text the model can attend to for one call, measured in tokens. Fixed size — once it's full, something has to give. | Physical desk space during one meeting |
| **Token** | A chunk of text (roughly ¾ of a word on average) — the unit the context window is measured in. (First introduced in P1-LA7's token-accounting example.) | A single sheet of paper |
| **Context engineering** | The deliberate design of what information enters the context window, in what form, and at what point in the agent's execution — as opposed to naively concatenating everything available. | Choosing which folder goes on the desk, and when you swap it |
| **System prompt** | The standing instructions given to the model before any task-specific content — persona, rules, constraints, output format. Present in every call to that agent. | An Investment Policy Statement (IPS): the standing mandate that governs every trade, not re-negotiated each time |
| **Just-in-time (JIT) retrieval** | Fetching a piece of information only when a specific step actually needs it, via a tool call, rather than preloading it into context "just in case." | Pulling a specific client file when the call comes in, not keeping every client's file open all day |
| **Compaction** | Periodically condensing accumulated context (e.g., a long tool-call/result history) into a shorter summary, freeing up token budget while keeping the essential state. | At the end of a long trading day, writing a one-page summary of what happened instead of keeping every Bloomberg chat open |
| **Context rot / "lost in the middle"** | An observed tendency for models to attend less reliably to information buried in the middle of a long context, even when it's technically still within the token limit. | A 40-page memo where the reader skims the middle pages and only really absorbs the opening and closing |

## 3. The most important distinction: LLM context vs. application memory

This is the single biggest conceptual trap for someone coming from a non-engineering background, so it's worth being very explicit about it.

**The LLM's context window is not the same thing as your program's memory.**

When our orchestrator (built in Python) fetches 5 years of daily price data for the NASDAQ-100 via yfinance, that data lives in a **pandas DataFrame in Python's memory** — a plain data structure sitting in RAM, completely outside the LLM's context window. The LLM never needs to "see" every row of that DataFrame. What the LLM needs to see is a **summary of what the tool call returned** — shape, date range, any missing tickers — so it can decide what to do next.

| What | Where it lives | Does the LLM need to see all of it? |
|---|---|---|
| Full 5-year OHLCV price history, NASDAQ-100 | Python DataFrame (RAM) | No — never |
| "Fetched 100 tickers, 2021-01-01 to 2026-01-01, 3 tickers had gaps" | LLM context (tool result) | Yes — this is what it reasons over |
| Computed factor scores for 100 stocks (a table of numbers) | Python DataFrame (RAM) | No, not row-by-row |
| "Signal computed, sector-neutral z-scores range -2.1 to 2.4, no nulls" | LLM context (tool result) | Yes |

The tool does the heavy numerical lifting *outside* the model's context; the model only ever sees **results and summaries** of that work, not the raw substrate. This is why an agent can meaningfully "work with" a dataset far larger than its own context window could ever hold — it never actually holds the dataset in context at all.

## 4. Worked numerical example: naive vs. engineered context budget

This extends the token-accounting example from P1-LA7 (single-agent cumulative cost: ~56,000 tokens across 7 stages; subagent-isolated cost: ~31,200 tokens). That example already showed why subagent isolation saves tokens. Now consider what happens *within* a single stage if context engineering is done wrong.

**Stage 1: Data fetch for NASDAQ-100, 5 years, daily OHLCV.**

| Approach | What goes into the LLM's context | Approx. tokens | Verdict |
|---|---|---|---|
| **Naive** — "just paste the data in so the model has everything" | Raw CSV: ~100 tickers × ~1,260 trading days × 6 fields (open/high/low/close/adj close/volume) | Several million characters → **far beyond any current context window** | Fails outright — this alone would blow the entire budget before the agent does anything |
| **Engineered** — tool call, structured summary only | `{"tickers_fetched": 100, "date_range": "2021-01-02 to 2026-01-02", "missing_tickers": ["ABC"], "gap_days_flagged": 3}` | ~150-250 tokens | Fits easily, gives the model exactly what it needs to decide the next action |

The naive approach isn't just wasteful — it's **not viable at all** for anything beyond toy data sizes. This is the practical reason JIT retrieval isn't optional once working with real market data: there's no context window big enough to hold raw price history for a real universe across years of daily bars.

**Stage 7 (memo generation) — a different failure mode: accumulated history, not raw data.**

By the time the orchestrator reaches the memo stage, if it has been passing forward the *entire* tool-call/result transcript from stages 1-6 (every intermediate query, every partial result, every retry) rather than just the final structured objects, that transcript itself can balloon:

| Point in pipeline | Naive: full transcript carried forward | Engineered: only structured handoff objects (P1-LA6/LA7 pattern) |
|---|---|---|
| After stage 1 | ~500 tokens | ~200 tokens |
| After stage 4 (with a retry logged) | ~4,000 tokens | ~800 tokens |
| After stage 6 (validator subagent's full reasoning included) | ~12,000+ tokens, validator's reasoning buried in the middle | ~600 tokens (just the `ValidationResult` object — `severity`, flagged issues) |

The engineered column is the **same discipline from P1-LA7** (passing the compact `ValidationResult` object rather than the validator's full reasoning trace) applied one level up: it's not just about subagent isolation, it's a *general rule* — carry forward the **distilled result of a stage**, not the **process by which that stage arrived at it**, unless the process itself is what the next stage needs to reason about.

## 5. Why "just include everything to be safe" backfires — even when it technically fits

Suppose the transcript in the naive column above technically fits — say the context window is large enough to hold 12,000 tokens without hitting a hard limit. The intuition might be: no harm in including it, more information can only help.

This is where **context rot** matters. Empirically, models don't attend uniformly across a long context — information buried in the middle (like the validator's step-by-step reasoning from three stages ago) is less reliably used than information at the start (system prompt) or the very recent end (the current task). So a bloated context isn't just expensive in tokens — it can actively make the model *worse* at the current task, because the signal (the one flagged issue that matters) is diluted by noise (five paragraphs of validator reasoning that reached the same conclusion a shorter object would have stated directly).

This is the direct throughline to why P1-LA7's structured handoff pattern (`ValidationResult` with a `severity` field) isn't just a cost optimization — it's also a **reliability** choice: a short, structured object is something the orchestrator's next stage can reason over cleanly, where a long freeform trace is something it might partially ignore or misread.

## 6. The core design question: what belongs in context vs. what gets fetched on demand

Here's the decision framework, built from everything above:

| Category | Include upfront (every call)? | Or fetch/generate on demand? | Why |
|---|---|---|---|
| System prompt (persona, rules, output format) | **Always upfront** | — | It's the standing mandate — needed for every decision, small and fixed cost |
| Tool definitions (what tools exist, their schemas) | **Always upfront** | — | The model needs to know what's available to even consider calling it (P1-LA2 concept) |
| Current task instruction / user request | **Always upfront** | — | The immediate thing being worked on |
| Structured handoff object from the previous stage | **Upfront for that stage's call** | — | Small, distilled, directly needed |
| Raw market data (prices, fundamentals) | — | **Fetched on demand** via tool call, held in Python memory, never dumped into context | Too large, and the model never needs row-level access — only summaries |
| Full reasoning trace of a completed prior stage | — | **Compacted/discarded**, replaced by its structured result | Prevents context rot; the *conclusion* is what matters downstream, not the path |
| Long conversation history (many iterations back) | — | **Compacted** into a running summary periodically | Keeps the transcript from growing unbounded across a long agent loop |
| Long-term project knowledge (e.g., our CONTEXT.md) | — | **Fetched on demand** via a project-knowledge search, not preloaded whole | Exactly the same principle, one level up — see next section |

## 7. A meta-example you're already living: how CONTEXT.md and project knowledge work

This is worth pointing out explicitly because it's a live example, not a hypothetical one. Claude does not hold your entire multi-month curriculum history in context by default. Instead:

- A **memory summary** (a compact profile derived from past conversations) is the "compaction" pattern — a distilled, standing summary rather than every past conversation transcript.
- When specifics are needed — exactly which lessons are done, exact wording of a locked decision — a project-knowledge search fetches just the relevant chunk of CONTEXT.md/curriculum.md for *that* lesson, not the entire file history every time. This is **just-in-time retrieval**.

That's context engineering, applied to this working relationship. The same reasoning that says "don't preload 5 years of raw OHLCV data into the orchestrator's context" says "don't preload every past lesson's full transcript into every new conversation." Same principle, different domain.

## 8. System prompt design: what actually belongs in the standing mandate

Since "system prompt design" is explicitly one of this lesson's concepts, here's what should live there versus what shouldn't, using the IPS (Investment Policy Statement) analogy: an IPS states the mandate, risk limits, and constraints that govern *every* trade — it doesn't restate the details of today's specific trade.

| Belongs in the system prompt (standing, rarely changes) | Does NOT belong in the system prompt (task-specific, changes per call) |
|---|---|
| Agent's role/persona ("You are a factor research orchestrator...") | The specific hypothesis being tested this run |
| Output format rules (e.g., "always return valid JSON matching schema X") | The actual data returned by this run's tool calls |
| Standing constraints (e.g., "never fabricate a ticker that wasn't in the fetched universe") | The plan object for this specific run (that's per-call state, from P1-LA6) |
| Tool-use policy (e.g., "always validate before generating the memo") | Retry counts or errors specific to this run |

A bloated system prompt is its own version of the same mistake — if run-specific details get stuffed into the "standing mandate" part, that content's token cost is paid on *every single call* in the pipeline, not just the one that needs it. The IPS doesn't get rewritten every time a trade is placed; only the trade ticket does.

## 9. Direct tie-in to Project 1's architecture

Mapping this lesson onto the 7-stage pipeline from P1-LA7 (orchestrator: stages 1-5, validator subagent: stage 6, memo subagent: stage 7):

| Stage | What's in context for that call | What's explicitly kept OUT and fetched/computed elsewhere |
|---|---|---|
| 1. Data fetch | System prompt, task instruction, tool schema for the yfinance MCP tool | Raw price data itself — lives in a DataFrame, only a fetch summary returns to context |
| 2-4. Signal construction, neutralization, bucketing | System prompt, structured summary from stage 1, tool schemas for pandas-based compute tools | Row-level intermediate calculations — done in Python, only summary stats surface |
| 5. Metrics (Information Coefficient, decile returns) | System prompt, structured summaries from prior stages | Full per-stock, per-day return series |
| 6. Validator subagent | **Fresh, isolated context** (P1-LA7): the validator's own system prompt + only the specific outputs it needs to check | The orchestrator's stages 1-5 reasoning trace — deliberately not passed in, to preserve independence *and* avoid context rot |
| 7. Memo subagent | Its own system prompt + the `ValidationResult` object + final metrics summary | The validator's full reasoning, any retry history, raw data |

**Carried-forward design note for P1-Build-7/P1-Build-8:** when the orchestrator's stage-passing logic is actually implemented, each stage's tool/function should be written to **return a small structured object**, not a dump of whatever it computed — this lesson is the justification for that discipline, so it's not just an unexplained convention when the build phase arrives.

## 10. What's still open (deferred, not covered here)

- **Formal treatment of context rot as a reliability failure mode** (e.g., how to detect it happening in practice) — deferred to P1-LA9 (Agent failure modes — reliability), since that lesson covers failure modes in depth.
- **Compaction implementation mechanics** (exactly how/when an agent decides to summarize its own history mid-run) — touched on conceptually here, but the engineering specifics belong more naturally once actually building the Agent SDK orchestrator (P1-Build phase), not this concept lesson.

## Concepts Learned Summary (for CONTEXT.md cross-reference)

Context window defined as the model's fixed-size working memory (analogy: physical desk space during a meeting) — nothing outside it exists to the model at call time. Context engineering defined as the deliberate design of what enters the context window, in what form, and when, contrasted with naive "include everything" concatenation. Critical distinction established between LLM context (what the model sees) and application/program memory (Python DataFrames, RAM) — tools compute on data that never enters context; only results/summaries do. Worked numerical example extending P1-LA7's token accounting showed a naive raw-data-in-context approach for NASDAQ-100 OHLCV data blowing past any viable context budget (millions of characters) versus an engineered structured-summary approach (~150-250 tokens), and a second example showing accumulated full-transcript history ballooning to ~12,000+ tokens by stage 7 versus ~600 tokens when only structured handoff objects (the P1-LA6/LA7 pattern) are carried forward. Context rot / "lost in the middle" introduced as the reason bloated-but-technically-fitting context is still harmful — models attend less reliably to buried mid-context information, meaning the P1-LA7 structured handoff pattern is a reliability choice, not just a cost optimization. Decision framework built for what belongs upfront (system prompt, tool schemas, current task, immediate handoff object) versus what's fetched/compacted on demand (raw market data, full reasoning traces, long conversation history, long-term project knowledge). System prompt design principles established via Investment Policy Statement (IPS) analogy — standing mandate (persona, output rules, constraints) belongs in the system prompt; per-run specifics (this run's hypothesis, this run's plan object, retry counts) do not. Full stage-by-stage mapping produced for Project 1's 7-stage architecture showing what's in/out of context at each stage. Carried-forward requirement: each pipeline stage's tool/function should return a small structured object rather than a raw computation dump, to be enforced at P1-Build-7/P1-Build-8.
