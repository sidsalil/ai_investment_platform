# P1-Arch-2: Data Flow Design

**Completed:** 2026-07-21
**Phase:** Phase 2 — Architecture & Design (3/5 lessons done: P1-Arch-0, P1-Arch-1, P1-Arch-2)
**Estimated time (curriculum):** 1-2 hours

---

## 1. What this lesson is, and how it differs from P1-Arch-1

P1-Arch-1 (System design) answered "what components exist, and who talks to whom." It named every box in the system — UI, LLM orchestrator, yfinance Model Context Protocol (MCP) data layer, factor calc, portfolio construction, factor metrics, validation subagent, memo subagent, tracing/observability layer, product metrics subsystem — and drew edges between them. But on that diagram, an edge just meant "these two things communicate." It did not say what is actually written on the message that crosses that edge.

P1-Arch-2 (Data flow design) answers the next question: for one concrete request, what is the exact shape of the data at every hop? Not "the orchestrator calls the data layer" but "the orchestrator calls `get_price_history(ticker="AAPL", start_date="2025-06-01", end_date="2026-06-30")` and gets back a table with columns `date`, `adj_close`, `raw_close`."

**Trading-desk analogy:** the architecture diagram from P1-Arch-1 is the desk map — trader, Order Management System (OMS), exchange, clearing house, and the lines connecting them. The data-flow design in this lesson is the actual order ticket as it physically moves through those desks — the exact fields printed on it at each stop (ticker, quantity, limit price, timestamp), and how those fields change as the ticket gets stamped by each system in turn. You cannot actually build the OMS integration from the floor plan alone; you need the ticket's field list. Data flow design is that field list, for this project.

**Why this matters for the build, concretely:** P1-Arch-4 (Module structure and interfaces) will ask you to write real Python function signatures with type annotations — no implementation, just the skeleton. Those signatures are, almost mechanically, the boundaries identified in this lesson with type annotations attached. Doing Arch-2 properly now means Arch-4 is close to a direct transcription exercise, because every input and output shape at every stage boundary will already be known and written down.

---

## 2. Core idea: two parallel flows, not one

It is easy, when drawing a single sequence diagram, to implicitly assume there is one flow of data moving through the system. There are actually **two different channels**, moving at very different scales, carrying different information:

- **The data plane** — real Python objects (pandas DataFrames, floats, lists, Pydantic model instances) living in RAM inside the running process. This can be large: a full price history panel for 100 NASDAQ-100 stocks over roughly 3.5 years of daily data is on the order of 100 tickers × ~880 trading days ≈ 88,000 rows.
- **The context plane** — whatever text actually gets typed into the Large Language Model (LLM)'s prompt for its next turn. This must stay small and cheap: every token in it is billed per-call (see P1-LA13, cost/latency), and every token also competes for the model's attention. This second point is the more important one architecturally — it is the P1-LA7 "context rot" / "lost in the middle" finding: a bloated-but-technically-fitting context does not just cost more, it actively dilutes the signal the model needs to attend to.

This is not a brand-new principle — it was already locked as a general rule in P1-LA7/P1-LA8: **"context window ≠ application memory."** Raw market data lives in Python DataFrames in RAM and never enters the model's context; only small structured summaries of tool-call results do. What P1-Arch-2 does is take that principle, which was previously stated abstractly, and pin it down concretely, boundary by boundary, for this specific pipeline: at every single hop in the "user asks → orchestrator plans → MCP tools → validation subagent → memo subagent → output" flow, this lesson names (a) exactly what data-plane object exists at that boundary, and (b) exactly what — if anything — crosses into the context plane at that same boundary.

**Worked mini-example, before the full walkthrough:** at the "compute the factor" boundary (Stage 2a below), the *data-plane* object is a DataFrame with one row per (date, ticker) and a `raw_momentum` column — real numbers, potentially tens of thousands of rows across the full universe and history. The *context-plane* payload the LLM actually receives for that same step is just a small structured summary, e.g. `{"status": "success", "tickers_processed": 100, "date_range": "2024-01-01 to 2026-06-30"}` — three fields, on the order of 20 tokens. The model never sees a single raw momentum number directly at this stage; it only sees confirmation that the step succeeded, plus a couple of sanity-check counts it could use to catch an obviously wrong run (e.g., `tickers_processed` far below 100 would be a red flag worth reasoning about).

---

## 3. A design decision this lesson forces: where does MCP actually get called from?

P1-Arch-1 said "the orchestrator calls MCP tools" without pinning down *who* — meaning, which piece of code — actually makes each individual MCP call. This ambiguity is comfortable to leave unresolved at the system-design level, but it becomes unavoidable the moment you try to write out a concrete sequence, because there are really two very different designs hiding behind that one sentence:

**Design A (rejected): the LLM orchestrator itself makes one tool-use call per ticker.** The model would call `get_price_history` for AAPL, wait for the result, call it again for MSFT, wait, and so on — up to roughly 100 times for a NASDAQ-100 universe, once for price history and again for sector classification. Two things break under this design: (1) one hundred-plus round-trips of model reasoning is a large amount of latency and dollar cost for something that is, at bottom, just "fetch some data" — no judgment is required to decide to fetch AAPL's price history once the universe is known; and (2) if each `tool_result` for `get_price_history` returns into the model's own context (which is how tool use works — the model receives the result as a message), the raw price panel *would* leak into the context plane, which is precisely the outcome the P1-LA7 "context window ≠ application memory" principle says to avoid.

**Design B (locked this lesson): the LLM orchestrator calls exactly one native tool.** Call it `run_research_pipeline(factor_spec)` — a single tool-use turn from the model's point of view. Internally, that native Python function is itself the MCP *client*: it loops over every ticker in the universe, calling `get_price_history` and `get_sector_classification` against the yfinance MCP server directly (server-to-code, not server-to-model), assembles the full panel DataFrame in RAM, and then runs factor calc → signal construction (winsorize, sector-neutral z-score) → portfolio construction (quintile bucketing) → factor metrics (Information Coefficient (IC), rank IC, t-statistic, hit rate) entirely in deterministic Python. Only after all of that completes does it hand back one small, compact structured result to the LLM. The model's reasoning loop sees "I called the research pipeline, here is the summary," never "I called `get_price_history` one hundred times."

| | Design A: LLM makes each MCP call | Design B: native code makes MCP calls (locked) |
|---|---|---|
| Round-trips of model reasoning | ~100+ (one per ticker per data type) | 1 |
| Does raw price data enter the model's context? | Yes, as each individual `tool_result` | Never |
| Latency | High — many chained, sequential LLM turns | Low — a plain Python loop, no model round-trip per ticker |
| Who handles retries on a bad/missing ticker | The model, at real per-retry dollar cost | Plain Python error handling, effectively free |
| Consistency with P1-LA7's context-window principle | Violates it | Satisfies it |

This is a genuinely new architectural decision surfaced by doing the walkthrough concretely — P1-Arch-1 did not need to resolve it, because a system-design diagram draws boxes and edges, not payload contents. It is recorded as a locked decision in CONTEXT.md as of this session.

---

## 4. The full worked walkthrough — one request, boundary by boundary

Running example, matching the P1-Arch-1 worked example so the two diagrams can be read side by side: the user types **"Test momentum on NASDAQ-100."**

To keep every table in this section readable without re-deriving all of P1-L4's cross-sectional statistics, three illustrative tickers are threaded through every stage: **AAPL** (Technology), **MSFT** (Technology), **NEE** (Utilities). The real pipeline runs all ~100 NASDAQ-100 constituents; these three simply make the worked numbers legible. Numbers below are illustrative, chosen to demonstrate the correct *shape* of each stage's output, not recomputed to match any single earlier lesson's exact worked example.

### Stage 0 — UI → Orchestrator

| Plane | Payload |
|---|---|
| Data plane | Python `str`: `"Test momentum on NASDAQ-100"` |
| Context plane | Same string, becomes the user turn in the orchestrator's conversation, alongside its system prompt (role, available tools, output expectations — per P1-LA8 context engineering) |

### Stage 1 — Orchestrator → Spec extraction (LLM call; small-model candidate per the cost/latency framework in P1-LA13)

The extractor's job is to turn free text into a validated `FactorSpec`. Its context-plane input is: its own system prompt (extraction instructions, plus a small number of few-shot examples per P1-LA17's few-shot pattern), the user's raw sentence, and the target JSON Schema generated automatically from the `FactorSpec` Pydantic model via `model_json_schema()` — so the schema shown in the prompt can never silently drift out of sync with the actual class definition.

| `FactorSpec` field | Value the extractor should produce for this request |
|---|---|
| `hypothesis_text` | `"Test momentum on NASDAQ-100"` |
| `factor_type` | `"momentum"` |
| `universe` | `"NASDAQ100"` |
| `lookback_months` | `12` |
| `exclusion_months` | `1` |
| `rebalance_frequency` | `"monthly"` (default) |
| `long_short` | `true` (default) |

Notice the user's sentence never actually said "12 months" or "skip the most recent month" — inferring the classic "12-1 momentum" convention from the bare word "momentum" is exactly the judgment the extraction step is responsible for.

**Worked retry-with-feedback example.** This is exactly the kind of ambiguity the retry-with-feedback validation pattern (locked as part of the `FactorSpec` design decision) exists to catch. Suppose the extractor instead returns `lookback_months` missing entirely, or returns it as the string `"twelve"` instead of an integer. Pydantic's schema validation raises an error *before* any downstream stage runs — nothing is silently coerced. That error message ("`lookback_months` must be an integer ≥ 1; received the string `'twelve'`") is appended to the extractor's own context, and it is given one further attempt, bounded to a small retry limit rather than looping indefinitely.

The data-plane output of this stage, once validation passes, is a real `FactorSpec` Python object — not a JSON string sitting around waiting to be re-parsed at every later step. Every downstream stage receives the object directly. It is only re-serialized (compactly) at the two points where a *fresh* subagent context needs to be given a self-contained restatement of it (Stage 3 and Stage 4 below).

#### Stage 1, expanded: how different hypothesis phrasings actually extract

The single "Test momentum on NASDAQ-100" example only shows one path through the extractor. The interesting engineering problem is what happens to *different* sentences — some easy, some genuinely ambiguous, some that expose gaps in the schema itself. Seven representative inputs follow.

**A) Fully explicit input — nothing to infer**

> "Test a 6-month momentum factor, skipping the most recent month, on the S&P 500, rebalanced quarterly, long-only."

| Field | Extracted value | Why it's easy |
|---|---|---|
| `factor_type` | `"momentum"` | Stated directly |
| `universe` | `"SP500"` | Stated directly |
| `lookback_months` | `6` | Stated directly |
| `exclusion_months` | `1` | "skipping the most recent month" is explicit, no convention needed |
| `rebalance_frequency` | `"quarterly"` | Stated directly (overrides the `"monthly"` default) |
| `long_short` | `false` | "long-only" stated directly |

No inference, no ambiguity, no retry. This is the case the extractor should get right effectively 100% of the time — it's a pure text-to-field mapping problem.

**B) Underspecified input relying on convention (the original example above)**

> "Test momentum on NASDAQ-100."

`lookback_months=12`, `exclusion_months=1` are *inferred* from the bare word "momentum" via the "12-1 momentum" convention, not read off the sentence. This is the harder case — the extractor has to know finance domain convention, not just parse text. It's exactly the kind of thing few-shot examples (P1-LA17) need to demonstrate explicitly, since a zero-shot prompt has no reason to guess "12" specifically over any other lookback window.

**C) A different factor type, testing whether the extractor generalizes**

> "Check if low-volatility stocks have outperformed in the S&P 500 over the last two years."

| Field | Extracted value | Note |
|---|---|---|
| `factor_type` | `"volatility"` | "low-volatility" must map to the `volatility` `Literal` option, not be dropped as an adjective |
| `universe` | `"SP500"` | Stated directly |
| `lookback_months` | `24` | "last two years" must be converted to months — a unit-conversion inference, not a lookup |
| `exclusion_months` | `0` (default) | No exclusion convention exists for volatility the way it does for momentum — correctly defaults to zero rather than borrowing momentum's "skip 1 month" habit |
| `rebalance_frequency` | `"monthly"` (default) | Not stated |
| `long_short` | `true` (default) | Not stated |

Worth noticing: `exclusion_months=0` is the *correct* answer here specifically because it's the default, not because the extractor reasoned about it — this is a case where a wrong but confident-sounding output (accidentally carrying over momentum's 1-month skip) would be a subtle failure mode, since both `0` and `1` are individually valid values and Pydantic can't catch a wrong-but-plausible number the way it catches a malformed type.

**D) An input that exposes a real schema gap**

> "Test value, but exclude stocks that look cheap only because they're value traps."

| Field | Extracted value | Note |
|---|---|---|
| `factor_type` | `"value"` | Straightforward |
| `universe` | *(unspecified in sentence)* | Extractor must either ask, default, or guess — genuinely ambiguous |
| **"value trap" exclusion** | **no field exists to hold this** | This is the interesting part |

This is the same "value trap" ambiguity flagged in P1-LA16/P1-LA17, seen here from the schema side rather than the prompting side: `FactorSpec` as currently defined has no field for "exclude names that fail an additional screen." The extractor has two bad options — silently drop the exclusion (lossy, the user's actual intent gets thrown away) or try to stuff it into `hypothesis_text` as free text that nothing downstream reads (feels safe, but functionally identical to dropping it, since no pipeline stage parses `hypothesis_text` for content). Neither is a real fix. **This is a genuine open item, not something resolved by better prompting** — the schema itself may need a new optional field (something like `exclusion_criteria: list[str] | None`) before this kind of hypothesis can be honestly represented. Carried forward to P1-Arch-4 (Section 6/8 below).

**E) A universe outside the allowed set — a validation failure worth seeing in full**

> "Test momentum on the Russell 2000."

The extractor, doing its best, might return `universe="Russell2000"`. But `universe` is a `Literal["NASDAQ100", "SP500"]` — Russell 2000 isn't one of the two allowed values, so Pydantic validation fails immediately, the same mechanism as the malformed-`lookback_months` example above, just triggered by a different field:

```
ValidationError: universe
  Input should be 'NASDAQ100' or 'SP500' [input_value='Russell2000']
```

Retry-with-feedback here has a real design choice buried in it: should the retry prompt tell the extractor to (a) pick the closer of the two supported universes, or (b) return a clarifying-question response the orchestrator surfaces back to the user? Right now the pipeline only supports NASDAQ-100 and S&P 500 by design (locked project decision), so there is no "closer" universe to substitute — a small-cap request has no honest mapping onto either supported universe. **The correct behavior is for the retry to fail informatively up to the user** ("this platform currently supports NASDAQ-100 and S&P 500 only"), not to silently substitute a universe the user didn't ask for. This is a different failure mode than the `lookback_months` retry example, where a correction was actually possible.

**Summary comparison across all five extraction cases**

| Input | factor_type | universe | lookback_months | exclusion_months | rebal. freq. | long_short | Outcome |
|---|---|---|---|---|---|---|---|
| A (explicit) | momentum | SP500 | 6 | 1 | quarterly | false | Clean extraction |
| B (convention) | momentum | NASDAQ100 | 12 (inferred) | 1 (inferred) | monthly (default) | true (default) | Clean extraction, relies on domain convention |
| C (unit conversion) | volatility | SP500 | 24 (converted) | 0 (default) | monthly (default) | true (default) | Clean extraction, unit-conversion + correct-default risk |
| D (schema gap) | value | — | — | — | — | — | Cannot be fully represented — exclusion criterion has no field |
| E (out-of-scope universe) | momentum | *(invalid)* | — | — | — | — | Pydantic validation failure → retry-with-feedback → informative failure to user |

The honest takeaway: most hypothesis sentences (A, B, C) extract cleanly once the few-shot examples cover the relevant convention. The two interesting failure classes are a **schema coverage gap** (D — the model can't be blamed for a field that doesn't exist) versus a **validation-catchable input error** (E — the model can be corrected via retry, but only up to the limit of what the schema actually supports).

### Stage 2 — Orchestrator → Research pipeline (single native tool call, per Section 3's locked decision)

Context-plane payload from the model: one `tool_use` block, `run_research_pipeline(factor_spec=<serialized FactorSpec>)`. This is the only context-plane traffic for this entire stage — everything below happens inside deterministic Python code and is never typed into a prompt.

| Sub-step | MCP call made by native code | Data-plane shape produced |
|---|---|---|
| Universe | `get_universe_constituents(universe="NASDAQ100")` | Python `list[str]`, roughly 100 ticker symbols |
| Price history | `get_price_history(ticker, start_date, end_date)`, looped once per ticker | Per-ticker DataFrame: columns `date`, `adj_close`, `raw_close` |
| Sector map | `get_sector_classification(tickers)` | DataFrame: columns `ticker`, `sector` |
| Assembly | (native code, no further MCP call) | One panel DataFrame, indexed by `(date, ticker)`, columns `adj_close`, `raw_close`, `sector` |

Worked shape for the three illustrative tickers, at one rebalance date (2026-06-30):

| date | ticker | adj_close | raw_close | sector |
|---|---|---|---|---|
| 2026-06-30 | AAPL | 214.30 | 214.30 | Technology |
| 2026-06-30 | MSFT | 441.80 | 441.80 | Technology |
| 2026-06-30 | NEE | 78.15 | 78.15 | Utilities |

`raw_close` and `adj_close` coincide here only because this illustrative snapshot has no split or dividend event landing on this exact date. This is exactly why both columns are cached and carried forward as two separate columns rather than one (per the P1-Build-1 design consequence locked in P1-L3): adjusted close is a moving target that gets retroactively rescaled by every future corporate action, while raw close is a frozen historical fact, safe to cache via simple row-append.

**Sub-stage 2a — Factor calc (native, deterministic).** Computes 12-1 log-return momentum per ticker as of the rebalance date.

| ticker | raw_momentum (12-1 log return) |
|---|---|
| AAPL | 0.180 |
| MSFT | 0.220 |
| NEE | 0.090 |

**Sub-stage 2b — Winsorize, then sector-neutral z-score (native, deterministic; order locked in P1-L4 — winsorize first, then z-score, never the reverse).**

| ticker | sector | winsorized raw_momentum | signal_zscore (sector-neutral) |
|---|---|---|---|
| AAPL | Technology | 0.180 | -0.71 |
| MSFT | Technology | 0.220 | 0.71 |
| NEE | Utilities | 0.090 | 0.00 (illustrative; a real Utilities sector group has roughly 15-20 names in the NASDAQ-100/S&P 500 universe, so a single-name z-score is not meaningful on its own — shown here only to preserve the correct column shape) |

**Sub-stage 2c — Portfolio construction (native, deterministic; quintile bucketing, long-short equal-weighted as the research default per the locked portfolio-construction decision).**

| ticker | quintile | weight |
|---|---|---|
| MSFT | Q5 (top) | +1/20 (one of 20 names in the top quintile of a 100-stock universe) |
| AAPL | Q3 (middle) | 0 |
| NEE | Q1 (bottom, illustrative) | -1/20 |

**Sub-stage 2d — Factor metrics (native, deterministic).** Computes IC, rank IC, t-statistic, and hit rate against the 1-month (21 trading day) forward-return window, computed only within the training portion of the chronological three-way holdout split (the holdout period is deliberately not touched here). Output is a compact structured object — provisionally named `FactorMetricsResult`, with fields to be finalized as an actual Pydantic model at P1-Arch-4:

```
FactorMetricsResult(
  ic_mean=0.041, ic_tstat=2.35, rank_ic_mean=0.038, hit_rate=0.54,
  sharpe=1.12, sortino=1.48, max_drawdown=-0.086, calmar=0.71,
  beta_to_market=0.03, beta_long_leg=0.51, beta_short_leg=-0.48,
  turnover_cost_drag_bps=14.2, holdout_split="train"
)
```

Only this small object — never the panel DataFrame, never the per-ticker signal or portfolio-weight tables — is what crosses back into the LLM's context plane as the result of the `run_research_pipeline` tool call. This is the direct, concrete illustration of Section 2's two-plane distinction: everything in sub-stages 2a-2d happened, in full, inside a running Python process, and none of it was ever typed into a prompt.

### Stage 3 — Orchestrator → Validator subagent (fresh, isolated context — per P1-LA7's independence rationale and P1-LA10's "confused deputy" risk)

Handoff object — deliberately minimal, per the merge-back discipline locked in P1-LA7 (carry forward the distilled *result* of a stage, never the *process* that produced it):

```
{ factor_spec: FactorSpec(...), metrics: FactorMetricsResult(...) }
```

The validator's own system prompt uses guided chain-of-thought (per P1-LA17) to walk through its checks in a fixed order before reaching a verdict: single-period IC reported without an accompanying t-statistic or Information Ratio (a p-hacking red flag per P1-L6/CONTEXT.md), exposure to multiple-testing (many factor variants tested without correction, per Harvey/Liu/Zhu 2016), divergence between the sector-neutral and universe-wide z-scores large enough to suggest the naive signal is secretly a sector bet, `|beta_to_market|` exceeding a threshold in either direction (per P1-L10's "deviation from zero, not high-vs-low" framing), and a reported Sharpe ratio without an accompanying max drawdown or Calmar ratio. It scores any concerning finding using the Consequence × Reversibility × Confidence-gap framework (each factor scored 1-3; threshold ≥12 triggers a checkpoint) and returns a structured verdict:

```
ValidationResult(passed=True, flags=["none"], severity="none")
```

**Branch point, worked example.** Suppose instead the validator had found `beta_long_leg` and `beta_short_leg` diverging enough to indicate the long-short book is not actually dollar-neutral — a finding scored, say, Consequence 3 × Reversibility 2 × Confidence-gap 2 = 12, at the escalation threshold. It would instead return:

```
ValidationResult(passed=False, flags=["long_short_beta_divergence"], severity="blocking")
```

The orchestrator's code branches directly on `severity`, per the pattern locked in P1-LA9/P1-LA11:

| `severity` | Orchestrator action |
|---|---|
| `"none"` or `"advisory"` | Proceed to the memo subagent, passing the `ValidationResult` along so any advisory flags can be honestly disclosed in the memo (directly extending the P1-L8 bias-disclosure pattern) |
| `"blocking"` | Trigger a plan revision (a P1-LA6-style response to an observation that invalidates a downstream assumption) — re-run or adjust the relevant stage; do **not** proceed to the memo subagent |

A paired `escalation` `TraceEvent` is emitted whenever `severity="blocking"` fires — see Section 5.

`ValidationResult.passed: true` remains, per the governance framework locked in P1-LA11, a recommendation to the human accountable party (the Owner), never treated by the system itself as a final decision.

### Stage 4 — Orchestrator → Memo subagent (fresh, isolated context; distinct persona/house style)

Handoff object:

```
{ factor_spec: FactorSpec(...), metrics: FactorMetricsResult(...), validation: ValidationResult(...) }
```

The memo subagent's system prompt supplies few-shot house-style examples (resolving the P1-LA16 tone-mismatch scenario) and a structured XML output skeleton (methodology, results, limitations/flags, next steps). It never receives the validator's internal reasoning trail (per the merge-back discipline), and it never receives the raw price panel or any intermediate DataFrame — only the two compact objects shown above, alongside its own `FactorSpec`. Output: memo text with those structured sections, including honest disclosure of any advisory flags carried in `ValidationResult.flags`.

### Stage 5 — Orchestrator → UI

Final memo text, plus (optionally, for the Product Manager-facing dashboard) the `FactorMetricsResult` summary object for direct display alongside the memo.

---

## 5. The tracing overlay — a third, cross-cutting flow

Every stage above also does one more thing in parallel, which is genuinely a *third* flow layered on top of the data plane and context plane: it emits `TraceEvent` objects, all sharing one `trace_id` generated exactly once, at Stage 0, for the entire end-to-end run. Unlike the data plane and context plane, this flow does not carry the request forward — it only observes and records.

Two concrete worked events, using the locked seven-type taxonomy (`perceive`, `reason`, `act`, `observe`, `escalation`, `subagent_invocation`, `subagent_result`) and the full `TraceEvent` Pydantic schema (`trace_id`, `span_id`, `parent_span_id`, `agent`, `iteration`, `event_type`, `timestamp`, `content`, `latency_ms`, `token_count`):

```
TraceEvent(trace_id="run_8842", span_id="s3", parent_span_id="s1",
  agent="orchestrator", iteration=3, event_type="act",
  content={"tool": "run_research_pipeline", "factor_spec": {...}},
  timestamp="2026-07-21T14:02:11Z", latency_ms=1840, token_count=None)

TraceEvent(trace_id="run_8842", span_id="s7", parent_span_id="s1",
  agent="validator_subagent", iteration=1, event_type="subagent_result",
  content={"result": {"passed": true, "severity": "none"}},
  timestamp="2026-07-21T14:02:14Z", latency_ms=920, token_count=410)
```

Had the validator instead returned `severity="blocking"` (the branch-point example in Section 4, Stage 3), that `subagent_result` event would be paired with a separate `escalation`-type `TraceEvent` carrying the Consequence/Reversibility/Confidence-gap scores directly in its `content` field — independently filterable (`event_type == "escalation"`) without reading every ordinary event in the full trace. Tracing then feeds the product-metrics subsystem downstream, asynchronously, exactly as locked in P1-Arch-1's OLTP/OLAP-style separation. This lesson does not change that design; it simply shows precisely where in the sequence each trace event fires and what its `content` looks like for this specific pipeline.

---

## 6. New decisions locked this session

1. **MCP invocation locus.** The LLM orchestrator never calls per-ticker MCP tools directly. It makes exactly one native tool call (`run_research_pipeline`); that native Python function is itself the MCP client for every `get_price_history` and `get_sector_classification` call, looped entirely in code, outside the model's context. Rationale: avoids ~100+ unnecessary model round-trips, and prevents the raw price panel from ever entering the context plane, per P1-LA7's context-window principle. See Section 3 for the full comparison table.
2. **`FactorSpec` object-handling convention.** Once validated, `FactorSpec` is carried forward between pipeline stages as a live Python object, not repeatedly re-parsed from JSON. It is only re-serialized (compactly) at the two points where a fresh subagent's context needs a self-contained restatement of it (validator handoff, memo handoff).
3. **`FactorMetricsResult` provisional schema.** Sketched in Section 4, Sub-stage 2d, with the field list shown there — explicitly flagged as provisional. Exact field names, types, and defaults are to be finalized as a real Pydantic model at P1-Arch-4 (Module structure and interfaces).

---

## 7. Deliverables

- This notes file (`P1_Arch2_Data_Flow_Design.md`)
- Inline sequence diagram (six-stage: user request → spec extraction → research pipeline → validator subagent → memo subagent → UI output), rendered in chat during this session
- Updated `CONTEXT.md` and `curriculum.md` (this session)

## 8. Carried forward to future sessions

- **P1-Arch-4:** finalize `FactorMetricsResult` as an actual Pydantic model — confirm field names/types/defaults against Section 4's provisional sketch, and confirm `run_research_pipeline`'s exact function signature per the MCP-invocation-locus decision (Section 3/6).
- **P1-Arch-4 (new, surfaced by Stage 1's expanded examples):** decide whether `FactorSpec` needs a new optional field to represent exclusion criteria (e.g., `exclusion_criteria: list[str] | None`), surfaced by the "value trap" hypothesis example in Stage 1. Currently, a hypothesis naming an exclusion on top of a base factor cannot be honestly represented by the schema — it is either silently dropped or stuffed into `hypothesis_text` where nothing downstream reads it. This is a schema coverage gap, not a prompting problem, and better few-shot examples cannot fix it on their own.
- **P1-Build-1 (MCP data server):** confirm the native pipeline code (not the LLM) is the component holding the MCP client connection and the per-ticker fetch loop, consistent with the Section 3 decision.
- **P1-Build-7 (orchestrator):** implement the single `run_research_pipeline` tool-use call as the only per-request MCP-triggering step the LLM itself takes; implement the `severity`-based branch (proceed vs. plan-revision) exactly as worked in Section 4, Stage 3.
- Rolling vs. expanding window choice for the walk-forward split (still deferred to P1-Arch-3/P1-Arch-4 — not resolved by this lesson) and the market-benchmark series for `beta_to_market` (still deferred to build time) remain open, unaffected by this session.

---

## Appendix A: `FactorSpec` — detailed object structure

`FactorSpec` is the validated, structured representation of a user's research hypothesis. It is produced once, at Stage 1, by the spec-extraction step, and then carried forward as a live Python object through every later stage — never re-parsed from JSON except when a fresh subagent's context needs a compact restatement of it (Stage 3, Stage 4).

**Field-by-field reference**

| Field | Type | Required? | Default | Constraint | Locked in |
|---|---|---|---|---|---|
| `hypothesis_text` | `str` | Yes | — | none | P1-Arch-4 (to finalize) |
| `factor_type` | `Literal["momentum", "volatility", "liquidity", "value"]` | Yes | — | must be one of the four listed values | P1-LA4 |
| `universe` | `Literal["NASDAQ100", "SP500"]` | Yes | — | must be one of the two supported universes | P1-LA4 |
| `lookback_months` | `int` | Yes | — | `ge=1` (must be at least 1) | P1-LA4 |
| `exclusion_months` | `int` | No | `0` | `ge=0` (cannot be negative) | P1-LA4 |
| `rebalance_frequency` | `Literal["monthly", "quarterly"]` | No | `"monthly"` | must be one of the listed values | P1-LA4 |
| `long_short` | `bool` | No | `true` | none | P1-LA4 |
| `exclusion_criteria` *(proposed, not yet locked)* | `list[str] \| None` | No | `None` | none defined yet | Open — carried forward to P1-Arch-4 (Section 8 above) |

**What each field means, in plain language**

- `hypothesis_text` — the user's original sentence, kept verbatim. Never parsed by any downstream stage; it exists purely as an audit trail so a human reviewing the memo later can see exactly what was asked, in the user's own words.
- `factor_type` — which of the four supported factor families this request is testing. Constrained to a fixed, closed list on purpose: an open-ended string here would let an unsupported factor type silently pass validation and fail much later, deep inside factor calc, where the error would be far more confusing to trace back.
- `universe` — which of the two supported stock universes to run against. Also a closed list, for the same reason, and because the platform's data-quality guarantees (survivorship bias handling, point-in-time limitations documented in P1-L2) are only understood for these two.
- `lookback_months` — how far back, in months, the factor's own calculation window looks. Must be at least 1 month; there's no such thing as a zero- or negative-length lookback.
- `exclusion_months` — how many of the most recent months to skip before the lookback window starts (the "-1" in "12-1 momentum"). Defaults to 0 because most non-momentum factors have no equivalent convention — see Stage 1, Example C, where getting this default right (rather than borrowing momentum's habit of 1) was the whole point of the example.
- `rebalance_frequency` — how often the portfolio is reconstructed. Defaults to the project's locked convention of monthly, but can be overridden (Stage 1, Example A, "rebalanced quarterly").
- `long_short` — whether the portfolio construction step should build a long-short book (top quintile long, bottom quintile short, the research default) or a long-only book (top quintile only, the practitioner-alternative locked decision). Defaults to `true` (long-short) since that's the research default.
- `exclusion_criteria` *(proposed)* — a list of free-text exclusion rules layered on top of the base factor (e.g., "exclude value traps"). Not yet part of the locked schema; included here only to make the open gap concrete, per Stage 1, Example D and the Section 8 carried-forward item.

**Illustrative Pydantic sketch** (for reference — the real class is written by hand at build time, per the project's code-ownership policy):

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class FactorSpec(BaseModel):
    hypothesis_text: str
    factor_type: Literal["momentum", "volatility", "liquidity", "value"]
    universe: Literal["NASDAQ100", "SP500"]
    lookback_months: int = Field(ge=1)
    exclusion_months: int = Field(default=0, ge=0)
    rebalance_frequency: Literal["monthly", "quarterly"] = "monthly"
    long_short: bool = True
    # exclusion_criteria: Optional[list[str]] = None  # proposed, not yet locked
```

**Worked instances, cross-referenced to Stage 1's examples**

| Example | `factor_type` | `universe` | `lookback_months` | `exclusion_months` | `rebalance_frequency` | `long_short` |
|---|---|---|---|---|---|---|
| B ("Test momentum on NASDAQ-100") | `"momentum"` | `"NASDAQ100"` | `12` | `1` | `"monthly"` | `true` |
| A (fully explicit) | `"momentum"` | `"SP500"` | `6` | `1` | `"quarterly"` | `false` |
| C (low-volatility, 2 years) | `"volatility"` | `"SP500"` | `24` | `0` | `"monthly"` | `true` |

---

## Appendix B: `FactorMetricsResult` — detailed object structure

`FactorMetricsResult` is the compact structured summary produced at the end of the native research pipeline (Stage 2, Sub-stage 2d). It is the *only* thing that crosses back into the LLM's context plane from the entire pipeline — the panel DataFrame, the per-ticker signal table, and the portfolio-weight table all stay in the data plane and are never seen by the model. It is also the object handed, largely unchanged, into both the validator subagent (Stage 3) and the memo subagent (Stage 4).

**Status: provisional.** Every field below reflects the sketch introduced in Section 4, Sub-stage 2d of this lesson. None of it is a locked Pydantic model yet — that finalization is explicitly deferred to P1-Arch-4, where exact types, defaults, and any additional fields will be confirmed against this sketch.

**Field-by-field reference**

| Field | Type | Description | Source lesson |
|---|---|---|---|
| `ic_mean` | `float` | Mean Information Coefficient (IC) across all rebalance dates in the training split — the average cross-sectional correlation between the signal and the 1-month forward return | P1-L6 |
| `ic_tstat` | `float` | t-statistic on the mean IC — tests whether the average IC is statistically distinguishable from zero, not just a lucky sample | P1-L6 |
| `rank_ic_mean` | `float` | Mean rank IC (Spearman rank correlation version of IC) — less sensitive to outliers than the raw IC | P1-L6 |
| `hit_rate` | `float` | Fraction of rebalance periods where the signal's cross-sectional rank correctly predicted the direction of relative outperformance | P1-L6 |
| `sharpe` | `float` | Annualized Sharpe ratio of the constructed portfolio's return series (×√12 for monthly rebalancing, per the locked annualization convention) | P1-L10 |
| `sortino` | `float` | Like Sharpe, but penalizes only downside deviation below a configurable Minimum Acceptable Return (MAR), defaulted to 0% | P1-L10 |
| `max_drawdown` | `float` | The single worst peak-to-trough decline over the backtest window, expressed as a negative fraction (e.g., `-0.086` = an 8.6% drawdown) | P1-L10 |
| `calmar` | `float` | Calmar ratio — annualized return divided by the magnitude of `max_drawdown`, a return-per-unit-of-worst-pain metric | P1-L10 |
| `beta_to_market` | `float` | Beta of the overall long-short portfolio against the chosen market benchmark. Should be near zero if dollar-neutral construction is working — this is a "deviation from zero" metric, not a "high vs. low" one; a strongly negative value is just as much a red flag as a strongly positive one | P1-L10 |
| `beta_long_leg` | `float` | Beta of the long leg alone against the market benchmark | P1-L10 |
| `beta_short_leg` | `float` | Beta of the short leg alone against the market benchmark | P1-L10 |
| `turnover_cost_drag_bps` | `float` | Estimated transaction-cost drag, in basis points, from the locked flat-10bps-both-legs convention applied to the long-short book's turnover | P1-L9 |
| `holdout_split` | `Literal["train", "holdout"]` | Which chronological split these metrics were computed on — flags at a glance whether a number is a training-period result or a genuine out-of-sample holdout result | P1-L8 |

**Fields likely missing from the current sketch — flagged, not yet added**

P1-L10 also locked drawdown *duration* (both the single-worst episode and the average across all drawdown cycles in the backtest) as part of the metrics-calculation module's required output — this sketch does not yet include it. Recommend adding at P1-Arch-4:

| Proposed field | Type | Description |
|---|---|---|
| `max_drawdown_duration_days` | `int` | Length, in trading days, of the single worst drawdown episode |
| `avg_drawdown_duration_days` | `float` | Average length, in trading days, across all drawdown cycles in the backtest |

**Illustrative Pydantic sketch** (provisional — for reference only, final version to be confirmed at P1-Arch-4):

```python
from pydantic import BaseModel
from typing import Literal

class FactorMetricsResult(BaseModel):
    ic_mean: float
    ic_tstat: float
    rank_ic_mean: float
    hit_rate: float
    sharpe: float
    sortino: float
    max_drawdown: float
    calmar: float
    beta_to_market: float
    beta_long_leg: float
    beta_short_leg: float
    turnover_cost_drag_bps: float
    holdout_split: Literal["train", "holdout"]
    # max_drawdown_duration_days: int          # proposed, not yet locked
    # avg_drawdown_duration_days: float        # proposed, not yet locked
```

**Worked instance, cross-referenced to Section 4, Sub-stage 2d**

```
FactorMetricsResult(
  ic_mean=0.041, ic_tstat=2.35, rank_ic_mean=0.038, hit_rate=0.54,
  sharpe=1.12, sortino=1.48, max_drawdown=-0.086, calmar=0.71,
  beta_to_market=0.03, beta_long_leg=0.51, beta_short_leg=-0.48,
  turnover_cost_drag_bps=14.2, holdout_split="train"
)
```

Per the validator's methodology checks (Section 4, Stage 3): this instance would pass cleanly — `ic_tstat=2.35` accompanies `ic_mean`, so it isn't a bare single-period IC; `beta_to_market=0.03` is close enough to zero to indicate the dollar-neutral construction is working; `sharpe` is accompanied by `max_drawdown` and `calmar`, so the risk picture isn't incomplete.
