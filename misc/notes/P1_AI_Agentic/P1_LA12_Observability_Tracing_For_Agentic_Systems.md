# P1-LA12: Observability & Tracing for Agentic Systems

**Completed:** 2026-07-15
**Track:** AI/Agentic (12 of 17)

---

## 1. The problem this solves — intuition first

Think about your trading systems background for a second. When a trade breaks — wrong price, wrong quantity, wrong counterparty — you don't just shrug. You pull the **order audit trail**: every order state change, every fill, every amendment, timestamped, in sequence. That trail lets you answer "what actually happened, in what order, and why" without asking anyone to remember.

An agent has the exact same problem, except worse: the "trader" making decisions is a language model whose reasoning happens inside a black box. When your Project 1 orchestrator produces a wrong factor spec, or gets stuck in a loop, or the validator subagent passes something it shouldn't have — you need the equivalent of an order audit trail for *agent decisions*, not just trade decisions.

**Observability** is the general capability of being able to understand what's happening inside a running system from the outside, without having to stop and inspect it manually. **Tracing** is the specific technique for agentic systems: recording every step of an agent's perceive-reason-act-observe loop (P1-LA1) as a structured, timestamped sequence you can replay after the fact.

Without tracing, debugging an agent looks like: "it gave a wrong answer, I have no idea which of the 7 steps went wrong, let me re-run it and hope I can spot the bug this time." With tracing, it looks like: "step 4's Reason event claims a fact that no preceding Perceive event actually supplied — that's the hallucination, right there."

---

## 2. Three related-but-distinct terms

These get used loosely in casual conversation, so pin them down:

| Term | What it answers | Analogy |
|---|---|---|
| **Logging** | "What happened?" — a flat stream of events, usually unstructured text (`print` statements, log lines) | A trader's scratch notes jotted during the day |
| **Tracing** | "What happened, in what order, as part of *which run*?" — structured, causally-linked events grouped into one coherent record of a single execution | The full order audit trail for one specific trade ticket, start to finish |
| **Monitoring** | "Is the system healthy *in aggregate*, across many runs, right now?" — dashboards, alerts, aggregate metrics (error rate, latency p99) | The trading desk's end-of-day risk dashboard across all trades, not any one trade in particular |

Project 1 mainly needs **tracing** — you're debugging individual agent runs. Monitoring becomes relevant once something is deployed and running unattended (touched on in P1-LA13/LA14), and is a *rollup* over many traces, not a replacement for them.

---

## 3. Anatomy of a trace: trace vs. span

Borrowing standard vocabulary from **OpenTelemetry** (the industry-standard open-source observability framework — you don't need to use it for P1, but the vocabulary is now universal enough that using it correctly is itself a signal in an interview):

- A **trace** is the full record of one complete execution — in P1's case, one full run of "user asks a factor research question" → memo produced.
- A **span** is one individual unit of work within that trace — one Reason step, one tool call, one subagent invocation. A trace is a tree of spans (some spans are children of others).

**Worked example, mapped to P1-LA1's 7-iteration momentum trace:**

| Concept | P1-LA1's momentum example, re-expressed |
|---|---|
| Trace | The entire "test 12-month momentum on the NASDAQ-100" run, iterations 1-7 |
| Span | Iteration 3's tool call to `get_price_history` is one span |
| Parent/child span | If iteration 6 hands off to the validator subagent (P1-LA7), the validator's own internal reasoning steps are child spans nested under the "invoke validator subagent" span |

This parent/child structure is exactly why a trace stays coherent even when P1-LA7's subagents spin up their own separate Claude conversations — the parent-child link is what lets you view the validator's internal reasoning *and* see how it fits into the orchestrator's overall run, without them being one undifferentiated blob.

---

## 4. The event taxonomy — the design decision that matters most for P1

A trace is only useful if its events are typed distinctly enough that you can scan it fast. Three earlier lessons already put load-bearing distinctions on the table, and this lesson's job is to make each one a **first-class, visually distinct event type** in the trace schema — not just a mental note.

| Event type | What it records | Where it came from |
|---|---|---|
| `perceive` | Context taken in at the start of a cycle — the goal, prior tool results, current state | P1-LA1's loop |
| `reason` | The model's generated inference — "I need price data first," "gaps could break this" | P1-LA1's loop |
| `act` | A tool call request (which tool, what inputs) | P1-LA2 |
| `observe` | A tool's actual result coming back | P1-LA2/P1-LA1 |
| `escalation` | A blocking/advisory checkpoint firing — human review triggered | P1-LA11 |
| `subagent_invocation` | Orchestrator handing off to validator or memo subagent, including the compact handoff payload | P1-LA7 |
| `subagent_result` | The structured result (e.g. `ValidationResult`) coming back from a subagent | P1-LA7 |

**Why `reason` and `perceive` must never be merged into one generic "thinking" event type:** P1-LA1's follow-up already locked this — Reason content is the model's *inference*, plausible but unverified; Perceive content is a *fact a tool actually reported*. If your trace collapses both into one undifferentiated "agent thought" event, you lose the single most useful signal for catching hallucination: **a Reason event asserting a specific, checkable fact with no preceding Perceive event that supplied it.** That mismatch is the hallucination, visible directly in the trace, without needing to re-run anything.

**Why `escalation` must be its own event type, not just an `act` with a note attached:** P1-LA11 established that blocking severities are a governance checkpoint, not just another pipeline step. If escalation events look identical to ordinary tool calls in the trace, a human reviewing the trace after the fact has to read every single event to find out whether the run paused for approval — which defeats the entire purpose of having a governance mechanism in the first place. It needs to jump out visually.

**Why `subagent_invocation`/`subagent_result` are distinct from `act`/`observe`:** P1-LA7 locked that a subagent call starts a *fresh Claude conversation*, not another MCP tool call. Logging it identically to a tool call would misrepresent what actually happened architecturally, and would hide the context-isolation boundary (P1-LA7's whole point) from anyone reading the trace.

---

## 5. What fields go on every event — structured logging, not free text

Same underlying principle as P1-LA4's structured outputs: a trace event should be a Pydantic model, not a formatted string, because downstream code (and you, six weeks from now) needs to query it — "show me every `reason` event across all seven iterations," not grep through prose.

**Worked schema, directly usable in P1-Build-7/P1-Build-8:**

```python
class TraceEvent(BaseModel):
    trace_id: str          # one per full end-to-end run
    span_id: str           # unique per event
    parent_span_id: str | None   # links subagent spans back to their invocation
    agent: Literal["orchestrator", "validator_subagent", "memo_subagent"]
    iteration: int         # which loop cycle within this agent's own run
    event_type: Literal["perceive","reason","act","observe",
                         "escalation","subagent_invocation","subagent_result"]
    timestamp: datetime
    content: dict          # payload shape depends on event_type
    latency_ms: int | None
    token_count: int | None
```

| Field | Why it exists | Worked value (iteration 3, momentum example) |
|---|---|---|
| `trace_id` | Groups every event — including subagent-internal events — under one run | `"run_2026-07-15T14:32:01_a8f2"` |
| `span_id` / `parent_span_id` | Reconstructs the tree structure (which event caused which) | `span_id="s07"`, `parent_span_id="s06"` |
| `agent` | Distinguishes orchestrator events from subagent-internal events sharing the same trace_id | `"orchestrator"` |
| `iteration` | Which cycle of *that agent's own* loop this belongs to | `3` |
| `event_type` | The taxonomy from Section 4 | `"act"` |
| `content` | The actual payload — tool name + inputs for an `act`, the fact reported for an `observe`, the inference text for a `reason` | `{"tool":"get_price_history","inputs":{"tickers":[...125 tickers...]}}` |
| `latency_ms` | How long this step took — needed for P1-LA13's cost/latency lesson | `840` |
| `token_count` | Tokens consumed by this step — same reason | `212` |

---

## 6. Correlation IDs — threading one trace across the orchestrator + two subagents

This is the piece that makes P1-LA7's multi-agent architecture traceable at all. Without a shared identifier, the orchestrator's trace and the validator subagent's trace would just be two unrelated logs sitting in two files, and you'd have no way to answer "what did the orchestrator hand the validator, right before it produced this verdict?"

**The fix: every event in a single end-to-end run — orchestrator events *and* every subagent's internal events — carries the *same* `trace_id`.** The `agent` field (Section 5) is what then lets you filter down to just the orchestrator's view, or just the validator's internal reasoning, while `parent_span_id` reconstructs exactly which orchestrator step triggered which subagent call.

This is the same underlying pattern as a trade's **order ID** persisting across every downstream system it touches — order management, execution venue, clearing, settlement — even though each system logs independently. Nobody re-derives which order a settlement fail belongs to; the ID is carried through by convention. Same idea here, applied to agent spans instead of trade lifecycle events.

**Direct payoff for the P1-LA9 residual risk (invisible subagent hallucination):** P1-LA9 flagged that a subagent's internal hallucination is invisible to the orchestrator by design (that's the whole point of context isolation) — the *only* available mitigation logged was "log the validator's internal reasoning even though the orchestrator never receives it." Correlation IDs are the mechanism that makes that logged mitigation actually usable: you can now open the trace file, filter to `agent == "validator_subagent"`, and inspect its reasoning independently, even though the orchestrator itself never saw it and never will.

---

## 7. Worked example: debugging a hallucination using a trace

Take P1-LA1's 7-iteration momentum trace and imagine one thing has gone subtly wrong: iteration 4 claims a stock was excluded because it "IPO'd 8 months ago," but the actual tool result only reported a data gap, not an IPO date.

| Span | event_type | content (abbreviated) | Diagnostic read |
|---|---|---|---|
| s08 | `act` | `get_price_history(ticker="XYZ", ...)` | Tool called, fine |
| s09 | `observe` | `{"XYZ": "insufficient history — only 45 days available"}` | Real fact from the tool: a *data gap*, not an IPO date |
| s10 | `reason` | `"XYZ IPO'd 8 months ago, excluding from universe"` | **Bug found here.** This Reason event asserts a specific fact (an IPO date) that no preceding Perceive/Observe event supplied. It's a plausible-sounding inference, not a verified fact — exactly the P1-LA1 Reason-vs-Perceive distinction this whole trace design exists to catch. |

Without event-type separation, this would just read as "agent noticed a problem and handled it" — looks fine at a glance. **With** `reason` and `observe` as visually distinct event types, the mismatch is inspectable in about five seconds: scan the `observe` events for what was actually reported, scan the adjacent `reason` event for what was claimed, and check whether the claim is a strict subset of the reported fact. This is the concrete, mechanical version of "debugging why an agent did what it did" — you're not re-running anything or guessing; you're reading the trace.

---

## 8. Escalation events — worked example tying back to P1-LA11

Recall P1-LA11's `ValidationResult.severity: "blocking"` checkpoint. Here's how it must appear in the trace, distinctly from an ordinary tool call:

| Span | event_type | content (abbreviated) |
|---|---|---|
| s24 | `subagent_result` | `ValidationResult(passed=False, flags=["look-ahead bias: fundamentals not lagged"], severity="blocking")` |
| s25 | `escalation` | `{"reason": "severity=blocking", "action": "pipeline halted, human review required", "consequence_score": 8, "reversibility_score": 3, "confidence_gap_score": 6}` |

Note `s25` is not just "another act" — it carries the P1-LA11 escalation-scoring fields directly, so a human scanning the trace file can filter to `event_type == "escalation"` and see *only* the moments the system stopped for human judgment, without wading through every ordinary tool call to find them.

---

## 9. Practical logging discipline: verbosity and what to keep

At Project 1's scale (single-user, dev-time debugging, not a production trading desk with millions of runs/day), the right default is simple: **log every event, for every run, in full — no sampling.** This is a deliberate contrast with real production observability at scale, where you'd sample (log 1% of runs in full detail, or drop low-information event types) purely because storage/query cost becomes real money. That tradeoff is worth naming in an interview ("here's what I'd change at production scale") but is not something to implement for a portfolio project — implementing sampling here would add complexity with zero real benefit, since you have no volume problem to solve.

**One practical detail worth locking now:** the `content` field's shape necessarily differs per `event_type` (an `act` event's content is a tool call; an `escalation` event's content is a scoring breakdown). Keep it a loosely-typed `dict` rather than trying to force one rigid sub-schema across all seven event types — over-engineering the schema here would fight the fact that these event types are genuinely heterogeneous.

---

## 10. Tooling landscape (brief — not building any of this for P1)

Worth being able to name in an interview, without needing depth:

| Tool | What it is |
|---|---|
| **OpenTelemetry** | Vendor-neutral, open-source standard for traces/spans/metrics — the vocabulary this lesson borrows from |
| **LangSmith** (LangChain's observability product) | A hosted tracing UI purpose-built for LLM/agent applications — visualizes exactly this kind of trace tree |
| **Anthropic Console** | Anthropic's own dashboard shows request-level logs for API calls made under your key — a coarser, request-level view rather than an application-level agent trace |

**Decision for P1:** hand-roll the `TraceEvent` Pydantic model and write events to a local JSON-lines file (one JSON object per line) at build time — no external tracing service needed for a personal project. This keeps the artifact fully self-contained and demonstrable without any account/API dependency, and the schema itself (Section 5) is the interview-ready artifact, regardless of what UI eventually renders it.

---

## Locked decisions from this lesson

1. Trace event taxonomy is exactly the seven types in Section 4 — `perceive`, `reason`, `act`, `observe`, `escalation`, `subagent_invocation`, `subagent_result` — each must render as a visually distinct type, not collapsed into fewer generic categories.
2. `TraceEvent` implemented as a Pydantic model (Section 5 schema) — structured, not free-text logging.
3. A single `trace_id` threads through the orchestrator's own events *and* every subagent's internal events (correlation ID pattern); `agent` + `parent_span_id` fields disambiguate whose events are whose and how they nest.
4. No sampling — every event, every run, logged in full, to a local JSON-lines file. Sampling explicitly named as a "what I'd do differently at production scale" talking point, not implemented.
5. `escalation` events carry the P1-LA11 scoring fields (consequence/reversibility/confidence-gap) directly in `content`, so blocking checkpoints are independently filterable and inspectable without reading every ordinary event.

---

## Carried-forward action items surfaced by this lesson

- **(P1-LA12) → P1-Build-7 (orchestrator):** Implement `TraceEvent` exactly per the Section 5 Pydantic schema. Every stage of the 7-stage pipeline emits `perceive`/`reason`/`act`/`observe` events; no stage may log a collapsed generic "thought" event.
- **(P1-LA12) → P1-Build-7/P1-Build-8 (orchestrator + subagents):** A single `trace_id` must be generated once per end-to-end run and passed into every subagent invocation so subagent-internal events share it — implement this as a required argument to the subagent-invocation function, not an optional one, so it can't be silently omitted.
- **(P1-LA12) → P1-Build-8 (validator subagent):** Log the validator's full internal reasoning trail as `perceive`/`reason`/`act`/`observe` events tagged `agent="validator_subagent"`, even though the orchestrator's own context never receives them — this is the concrete implementation of the P1-LA9 residual-risk mitigation ("log the validator's internal reasoning") using the correlation-ID mechanism from Section 6.
- **(P1-LA12) → P1-Build-7/P1-Build-8:** Every `ValidationResult.severity: "blocking"` event must emit a paired `escalation` TraceEvent carrying the P1-LA11 Consequence/Reversibility/Confidence-gap scores in `content` — not just a log line noting the pipeline halted.
- **(P1-LA12) → P1-Polish (risk memo / README):** The trace schema itself (Section 5) is strong differentiated interview material — cite it directly when discussing "how would you debug this agent" or "how do you know the system did the right thing" questions.
- **(P1-LA12, open/residual item):** No tracing UI/viewer is being built for P1 — trace files are inspected directly (JSON-lines, filtered by `event_type`/`agent`) rather than through a rendered dashboard. Revisit only if a specific interview or demo need makes a lightweight viewer concretely worthwhile; not required for the trace schema itself to be a legitimate, discussable artifact.
