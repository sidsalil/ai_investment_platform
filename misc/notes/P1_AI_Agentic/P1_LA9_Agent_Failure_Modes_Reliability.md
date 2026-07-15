# P1-LA9: Agent Failure Modes (Reliability)

**Date:** 2026-07-15
**Track:** AI/Agentic (lesson 9 of 17)
**Prerequisite lessons:** P1-LA1 (agent loop, Reason vs. Perceive), P1-LA5 (ReAct, "Thought masquerading as Observation"), P1-LA6 (planning loops), P1-LA7 (subagents), P1-LA8 (context engineering)

## Framing: reliability vs. security

This lesson covers **reliability** failure modes — things that go wrong because the agent is unreliable, not because someone is attacking it. **Reliability failure modes are bugs; security failure modes (P1-LA10, next lesson) assume an adversary.** Same symptoms are sometimes possible from both causes, but the fix is completely different: a bug is fixed with better engineering; an attack is fixed with access controls and least-privilege design. This lesson only covers the bug half.

---

## 1. Infinite loops

**Concept:** the agent keeps taking an action, observing a result, and deciding to take the same (or an equivalent) action again — with no built-in reason to ever stop. An LLM tool-use loop has no natural "I've tried this enough" instinct unless it's built in. Each iteration, the model reasons about the next action based on the current state; if that state doesn't visibly change between iterations, the model has no signal that anything is wrong — it just does what a reasonable agent would do, over and over.

**Analogy:** a trader who keeps re-checking the same quote screen because they can't tell whether they've already acted on it.

**Worked example — Project 1 failure pattern:** stage 1 (data fetch) hits a ticker where yfinance silently returns an *empty* DataFrame (not an error — zero rows) due to a temporary API hiccup.

| Iteration | Thought | Action | Observation | State change? |
|---|---|---|---|---|
| 1 | "I need price data for this ticker" | `fetch_prices(ticker)` | Empty DataFrame | No |
| 2 | "That didn't return data, let me fetch again" | `fetch_prices(ticker)` | Empty DataFrame | No |
| 3 | "Still empty, retrying" | `fetch_prices(ticker)` | Empty DataFrame | No |
| 4 | "Retrying" | `fetch_prices(ticker)` | Empty DataFrame | No |
| ... | ... | ... | ... | No |

Nothing here is wrong reasoning per iteration — "retry a failed fetch" is sensible. The bug is the absence of a mechanism forcing termination, escalation, or a strategy change after N failures. Left alone, this runs until an API rate limit, a token budget, or cost ceiling is hit.

**Mitigation:** a hard iteration cap enforced in application code, never a soft prompted instruction ("don't loop forever" in the system prompt is unenforced hope — same category of unreliable fix that P1-LA10 will flag for security).

```python
MAX_ITERATIONS = 8
for i in range(MAX_ITERATIONS):
    ...
else:
    escalate_to_human("stage 1 exceeded iteration cap")
```

The cap is a judgment call — too low cuts off legitimate multi-step reasoning, too high burns cost/time before giving up. For Project 1's 7-stage pipeline, a **per-stage cap** (not one global cap) is the right granularity, since a legitimate stage might reasonably take 3-4 tool calls.

---

## 2. Hallucinated tool calls

**Concept:** the model states something as a fact — often specific and checkable — that it actually generated from training-data pattern-matching, not from any tool's output. This is the direct payoff of the P1-LA1 Reason/Perceive distinction:
- **Reason step** ("I should check the beta before combining these") = the model's own inference. Expected, fine, not a fact-claim.
- **Perceive step** ("beta = 1.15") = only trustworthy if it came from an actual tool Observation.

Hallucination is a Reason-shaped statement dressed up in Perceive-shaped confidence.

**Detection heuristic — "Thought masquerading as Observation" (from P1-LA5):** for every specific, checkable number or fact the agent states, ask: is there a tool call and Observation immediately preceding it that could have produced this exact value? If not, it's suspect.

**Worked example:**

| Trace line | Type | Trustworthy? |
|---|---|---|
| Thought: "I should check this stock's beta before including it in the long-short book" | Reason | N/A — not a fact claim |
| Action: `get_beta(ticker="XYZ")` | Tool call | — |
| Observation: `{"beta": 1.15}` | Perceive | Yes — real computation |
| Thought: "XYZ has a beta of 1.15, consistent with its history of being a moderately volatile industrial name" | Reason, referencing a real Observation | Yes, correctly grounded |
| *(no tool call in between)* Thought: "XYZ's beta has historically been stable around 1.1-1.2 over the past five years" | Reason **presented as fact** | **No.** No tool ever returned 5 years of beta history. Sounds plausible (betas often are stable) but unverifiable from the trace — this is hallucinated. |

That last line is dangerous specifically because it's unverifiable from the trace itself. A downstream stage or a human reading the final memo has no way to distinguish it from a grounded claim without independently re-checking.

**Mitigation:**
1. **Structural** — the validator subagent (P1-Build-8) should flag any numeric claim in the memo without a corresponding upstream Observation in the trace.
2. **Tool-forcing** — require a tool call for facts that matter rather than trusting the model to choose to call one. If beta matters, `get_beta` must be called before beta is mentioned.
3. **Trace design** (ties to P1-LA12) — separate Reason lines from Perceive lines visually so orphaned fact-claims are easy to scan for.

---

## 3. Malformed outputs

**Concept:** the model produces output that doesn't conform to the structure downstream code expects — wrong types, missing required fields, extra fields, or unparseable output (e.g., prose wrapped around JSON). This is what P1-LA4 previewed as "the validation-failure retry pattern" when `FactorSpec` was built as a Pydantic model.

**Worked example:** `FactorSpec` extraction expects:

```json
{"factor_type": "momentum", "lookback_days": 252, "rebalance_frequency": "monthly"}
```

| Malformed response | What broke |
|---|---|
| `{"factor_type": "momentum", "lookback_days": "252 days"}` | `lookback_days` is a string, not an int — type coercion fails |
| `{"factor_type": "momentum"}` | Missing required `rebalance_frequency` field |
| `"Sure! Here's the spec: {...}"` | Not valid JSON — prose wrapped around it |
| `{"factor_type": "momentom", ...}` | Typo fails a `Literal["momentum","value","quality"]` constraint |

**Mitigation — retry-with-error-feedback:** don't retry blindly (that's the infinite-loop problem in miniature — retrying the identical malformed thing repeatedly won't fix it). Feed the validation error itself back to the model as an Observation so the next attempt has new information to correct against:

```
Attempt 1 → ValidationError: "rebalance_frequency: field required"
Attempt 2 → model receives that error → produces corrected JSON including the field
Attempt 3 → validates successfully → proceed
```

Cap attempts (e.g., 3) — same logic as the iteration cap: if the model can't self-correct after a few tries with explicit error feedback, escalate rather than loop.

---

## 4. Retry/backoff strategy

The general-purpose mitigation mechanism underlying both loop control and malformed-output recovery. **Concept:** don't retry a failed operation instantly and repeatedly — wait progressively longer between attempts, and give up after a capped number of tries.

**Exponential backoff formula:** delay before attempt *n* = base_delay × 2^(n−1), often with random jitter added so parallel agents don't all retry at the same instant and cause a synchronized pile-on.

**Worked example** — base_delay = 1s, max 4 attempts:

| Attempt | Formula | Delay before this attempt |
|---|---|---|
| 1 | 1 × 2⁰ | 0s (immediate) |
| 2 | 1 × 2¹ | 2s |
| 3 | 1 × 2² | 4s |
| 4 | 1 × 2³ | 8s |
| — | exceeded max_attempts | escalate to human / fail the stage explicitly |

**Analogy:** how a trading system handles a rejected order — you don't resubmit identical orders in a tight loop against an exchange; you back off, and after enough rejections you stop and alert a human trader rather than keep hammering the venue.

---

## 5. Timeout handling

**Concept:** a hard ceiling on how long any single operation (a tool call, a subagent invocation, an entire stage) is allowed to run before being forcibly cut off — independent of *why* it's slow. Without this, a single hung network call to yfinance can stall the entire 7-stage pipeline indefinitely, with nothing in the codebase even aware anything is wrong.

**Analogy:** a trading desk's execution-algorithm time limit — "if this order hasn't filled within 10 minutes, cancel and escalate," regardless of the cause. The ceiling is unconditional; you don't wait to diagnose before enforcing it.

```python
response = requests.get(url, timeout=30)  # hard 30s ceiling
```

**Layered timeouts for Project 1:** a single tool call needs a short timeout (seconds); a whole stage (which may involve several tool calls) needs a longer one; the entire 7-stage run needs the longest, outermost one. Each layer tripping is a distinct, loggable event — not silence.

---

## 6. Planning-specific failure modes (revisiting P1-LA6 in full depth)

These only exist because the orchestrator maintains a persistent plan object (P1-LA6), not just reactive tool calls.

**Stale plan / sunk-cost commitment:** the orchestrator keeps executing steps from its original plan even after an Observation invalidates one of the plan's assumptions, because nothing forces a re-check. Worked example: the plan assumed a 100-name NASDAQ-100 universe; stage 1's Observation reveals 6 tickers delisted mid-period. A stale-plan bug proceeds to stage 2 using the original 100-name assumption anyway, because "the plan says 100 names" and nothing prompted a re-check. Analogous to a portfolio manager trading on a three-month-old thesis despite the market having since contradicted it.

**Over-replanning:** the opposite failure — the orchestrator revises its plan on every minor observation, even ones that don't invalidate anything, thrashing between plan versions without ever finishing a stage. Worked example: stage 1 returns 98 of 100 tickers with data (2 had a one-day gap, immaterial). An over-replanning bug treats this as "my universe assumption is wrong" and regenerates an entirely new plan, when the correct response was "note the gap, proceed unchanged."

**Plan-execution mismatch:** the plan states one thing, but the steps actually executed diverge from it — silently, with no logged revision. The most dangerous of the three because it's invisible unless plan-vs-execution alignment is specifically checked: the system looks like it's following its plan (nothing crashed, output arrived) but a human reviewing only the final memo has no way to know the executed path differs from the documented plan.

| Failure mode | Trigger condition it should have had, but didn't | Project 1 example |
|---|---|---|
| Stale plan | Re-check plan assumptions against every stage's Observation | Delisted tickers not re-triggering a universe-size check |
| Over-replanning | Only replan when an Observation *actually* invalidates a downstream assumption | Immaterial 1-day gap triggering a full replan |
| Plan-execution mismatch | Log every deviation from plan as an explicit, structured revision event | Executed steps silently diverge from the plan object with no revision record |

**Mitigation — one structural fix covers all three:** make the "does this Observation conflict with the plan?" check its own explicit code step (per P1-LA6's carried-forward item), output a structured `{"conflict": bool, "revised_plan": [...] or null}` object, and require every executed step to be checked against — and every deviation logged against — the plan object. Stale plan and over-replanning are both about getting that conflict-check's *threshold* right (too insensitive → stale; too sensitive → thrashing); plan-execution mismatch is about making sure the check happens and is *recorded* at all.

---

## 7. Multi-agent-specific failure modes (revisiting P1-LA7)

These only exist once subagents are introduced.

**Context leakage between agents:** a subagent receives more than the compact handoff object it was designed to receive — e.g., the validator subagent accidentally gets the orchestrator's full stage 1-5 reasoning trail instead of just the final `FactorSpec` + metrics. Per P1-LA7, this defeats the independence rationale: the validator's judgment gets anchored by the builder's own justifications instead of checking them fresh. It's easy to introduce by accident in code (e.g., passing the whole conversation-history object instead of the extracted handoff fields), and nothing crashes when it happens — the validator just silently becomes less independent.

**Cost/latency multiplication:** each subagent invocation starts a fresh Claude conversation (per LA7) — a full round-trip, not a cheap function call.

| Pattern | Subagent calls | Sequential total | If parallelized |
|---|---|---|---|
| Validator with 1 retry | 2 calls × 2s | 4s | N/A — retries are inherently sequential, each depends on the last's failure |
| Validator + memo (independent of each other) | 2 calls × 2s | 4s | 2s, if genuinely independent with no data dependency |

Not every multi-agent latency cost is avoidable (retries must be sequential), but some is (independent subagents needlessly run one-after-another when they could run concurrently) — worth checking which case applies before accepting the cost.

**Subagent hallucination invisible to the orchestrator:** the orchestrator has no ReAct trace to check a subagent's internal reasoning against — it only receives the structured result (`ValidationResult`), by design (LA7's merge-back discipline). Correct for isolation, but it means if the subagent hallucinates internally, the orchestrator has no mechanism to catch it — it receives a confident, well-formed, wrong `ValidationResult` and treats it as ground truth. This is a direct cost of the isolation benefit: "orchestrator's judgment can't be anchored by the validator" is traded for "orchestrator can't sanity-check the validator's own internal reasoning."

**Mitigation:** context leakage is caught by a schema check on exactly what fields cross the subagent boundary (enforce the `handoff` field's shape). Cost/latency multiplication is addressed by identifying genuinely-independent subagent calls and parallelizing them. Invisible subagent hallucination has no clean fix within the isolation design itself — it's a residual risk accepted in exchange for independence; the closest mitigation is logging the subagent's own internal reasoning (even though the orchestrator doesn't see it) so a human debugging a bad `ValidationResult` after the fact has something to inspect.

---

## 8. Context rot / "lost in the middle" (revisiting P1-LA8 in full depth)

**Concept:** a model's ability to correctly attend to and use information degrades as the context window fills up — even when total content is well within the token *limit*. Not an overflow problem (that would error out cleanly); a degradation problem — performance quietly gets worse before it becomes obviously broken. The name reflects empirical findings that information placed in the *middle* of a long context is used less reliably than information at the beginning or end.

**Analogy:** a trader skimming a 40-page research report is more likely to miss something buried on page 22 than something in the executive summary or the conclusion.

**Detection — the tricky part:** no exception is thrown. Practical signals:

| Signal | What it suggests |
|---|---|
| Agent re-asks for information already provided earlier in the same run | Not reliably attending to earlier context |
| Agent's stage-7 memo omits or contradicts a decision made and stated back at stage 2 | Mid-run information got "lost" |
| Behavior measurably better with a shorter, curated context vs. the full accumulated history | Confirms a context-length effect, not a task-difficulty effect |

**Mitigation:** not "add a bigger context window" — keeping context small and structured in the first place, which is exactly what LA7's compact subagent handoffs and LA8's "small structured object per stage" convention already enforce. Compaction (summarizing old history mid-run, deferred to build time per LA8) is the other lever — deliberately dropping detail that's no longer needed rather than letting it silently accumulate and degrade attention to what matters.

---

## Master failure-mode cheat sheet

| Failure mode | Core mechanism | Detection signal | Mitigation |
|---|---|---|---|
| Infinite loop | No termination condition when state doesn't change | Iteration count climbing with no state progress | Hard iteration cap (code, not prompt) |
| Hallucinated tool call | Reason-step fact-claim with no backing Observation | "Thought masquerading as Observation" pattern | Trace-based fact-checking; force tool calls for facts that matter |
| Malformed output | Output doesn't satisfy schema | Pydantic `ValidationError` | Retry with the validation error fed back as an Observation, capped attempts |
| Retry storms | Retrying instantly/repeatedly on failure | Rapid-fire identical failed attempts | Exponential backoff with jitter, capped attempts |
| Hung operation | No ceiling on operation duration | Operation running far past expected duration | Layered timeouts (tool → stage → full run) |
| Stale plan | No re-check of plan assumptions against new Observations | Executing steps inconsistent with a since-invalidated assumption | Explicit conflict-check step after every Observation |
| Over-replanning | Replanning on immaterial observations | Plan thrashing, stage never completes | Conflict-check threshold tuned to *material* invalidation only |
| Plan-execution mismatch | Deviation from plan not logged | Final output inconsistent with documented plan | Every deviation recorded as a structured revision event |
| Context leakage (multi-agent) | More than the compact handoff crosses the agent boundary | Subagent behavior anchored to orchestrator's reasoning | Schema-enforced handoff object; code review of what crosses the boundary |
| Cost/latency multiplication | Sequential subagent round-trips | Wall-clock time scaling with subagent count | Parallelize genuinely-independent subagent calls |
| Invisible subagent hallucination | No trace for orchestrator to check subagent against | (no clean detection — residual risk) | Log subagent's internal reasoning even though orchestrator doesn't see it |
| Context rot | Attention degrades as context grows, even within token limit | Re-asking, mid-run inconsistency, better performance on curated context | Keep context small/structured (LA7/LA8 patterns); compaction |

---

## Tie-in to build sprints

Every mitigation above is application code, not a prompt instruction — that's the throughline of this lesson. At P1-Build-7 (orchestrator) and P1-Build-8 (subagents): implement a per-stage iteration cap, a retry-with-error-feedback wrapper around `FactorSpec` extraction, layered timeouts, the explicit plan-conflict-check step, a schema-enforced subagent handoff boundary, and a trace format (feeding directly into P1-LA12) that visually separates Reason from Perceive so hallucination is inspectable after the fact.

## Carried-forward action items surfaced this lesson

- **→ P1-Build-7 (orchestrator):** Implement per-stage `MAX_ITERATIONS` cap (not a global single cap for the whole run) — a legitimate stage may reasonably take 3-4 tool calls.
- **→ P1-Build-7 (orchestrator):** Implement the plan-conflict-check as a structured `{"conflict": bool, "revised_plan": [...] or null}` object per P1-LA6, with the threshold tuned to material (not immaterial) invalidation — directly resolves both stale-plan and over-replanning risk with one mechanism.
- **→ P1-Build-7/P1-Build-8:** Implement layered timeouts — tool-call level (seconds), stage level, and full-run level — each a distinct loggable event.
- **→ P1-Build-7 (FactorSpec extraction):** Implement retry-with-error-feedback (validation error text fed back as the next Observation), capped at ~3 attempts, escalating to a human on exhaustion.
- **→ P1-Build-7/P1-Build-8:** Implement exponential backoff with jitter (base_delay × 2^(n−1)) for any external-API retry (e.g., yfinance calls), capped at ~4 attempts before escalation.
- **→ P1-Build-8 (subagent boundary):** Add a schema check enforcing exactly what fields cross into a subagent call — prevents accidental context leakage of the orchestrator's full reasoning trail into the validator subagent.
- **→ P1-Build-7/P1-Build-8:** Where subagent calls are genuinely independent (e.g., validator and memo subagent, if no data dependency exists between them), parallelize rather than sequence — check this case by case rather than assuming all subagent calls must be sequential.
- **→ P1-LA12 (observability & tracing, upcoming):** Trace format must visually distinguish Reason lines from Perceive lines (direct extension of the P1-LA1/LA5 Reason-vs-Perceive distinction) so hallucination and context-rot symptoms (re-asking, mid-run inconsistency) are inspectable after the fact.
- **→ P1-Build-8 (validator subagent):** Validator's internal reasoning should be logged even though the orchestrator never receives it — the only available mitigation for the "invisible subagent hallucination" residual risk, since the isolation design itself has no clean in-band fix.
- **Open/residual item, not fully resolved:** invisible subagent hallucination has no structural fix within the isolation design — noted as an accepted trade-off, not a solved problem. Revisit only if a specific build-time incident makes it worth a deeper investment (e.g., a lightweight independent spot-check mechanism).
