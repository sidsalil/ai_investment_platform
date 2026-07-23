# P1-Arch-3: Orchestrator + Subagent Design

**Completed:** 2026-07-22
**Phase:** 2 — Architecture & Design (4/5 after this lesson)

## Where this lesson sits

P1-Arch-1 gave you the floor plan — which boxes exist, who's allowed to talk to whom. P1-Arch-2 gave you the order ticket — the exact fields that move through those boxes for one request. Neither one actually specified the **contract** between the orchestrator and its two subagents in enough detail to code against. "The orchestrator delegates to the validator" is a sentence a diagram can show with one arrow. It hides at least five separate design questions:

1. Exactly what goes into the subagent's fresh context (not just "a compact handoff" — the literal field list)
2. Exactly what comes back, and in what shape
3. What happens when the subagent's own output fails validation internally
4. What happens when the subagent *succeeds* but reports something the orchestrator has to act on
5. What data access or outbound capability, if any, does each subagent actually have

This lesson answers all five, for both subagents, and closes two carried-forward items from P1-Arch-1 and P1-Arch-2 about annotating data-access/egress on the architecture diagram.

**Trading-desk framing for the whole lesson:** P1-Arch-1 was the desk map. P1-Arch-2 was the order ticket. P1-Arch-3 is the **compliance sign-off procedure** — exactly what a compliance reviewer is handed, exactly what form their sign-off takes, and exactly what happens on the trading desk if compliance says "no."

---

## 1. The delegation contract, as three questions

Every subagent invocation in this system needs an unambiguous answer to three questions. This triplet is the actual deliverable of this lesson — everything else is working out the triplet for each of the two subagents.

| Question | What it fixes |
|---|---|
| **Invocation payload** | What fields cross into the subagent's fresh, isolated context |
| **Return contract** | What structured object comes back, and what each field means |
| **Failure propagation** | What the orchestrator does in each of the distinct ways a subagent call can end |

You already have half the ingredients locked from Phase 1. This lesson's job is assembling them into something you could hand to a developer (or Claude Code) and have them implement without guessing.

---

## 2. Recap: the plan object gains no new mechanics, just concrete values

P1-LA6 locked the plan object shape (`id`, `description`, `status`, `note`). P1-LA7 added exactly one field: `owner`. Nothing new happens here — this lesson just fills in real values for Project 1's actual 7-step run.

**Worked plan object for "Test 12-month momentum on NASDAQ-100":**

| step id | description | owner | status (mid-run) |
|---|---|---|---|
| 1 | Extract & validate `FactorSpec` from user hypothesis | orchestrator | done |
| 2 | Run research pipeline (`run_research_pipeline` native call: fetch → factor calc → winsorize/z-score → bucket → backtest → metrics) | orchestrator | done |
| 3 | Methodology validation | **validator_subagent** | in_progress |
| 4 | Memo generation | **memo_subagent** | pending |

Notice the plan collapsed P1-Arch-2's five internal pipeline stages (fetch, factor calc, portfolio construction, backtest, metrics) into a single step 2, because P1-Arch-2 already locked that they're all one native tool call (`run_research_pipeline`) from the model's point of view — the plan object tracks what the *model* has discretion over, not every line of Python underneath it.

This is the concrete instance of P1-LA7's ownership-mapping decision: steps 1-2 stay with the orchestrator (no independence concern, same builder persona, tightly sequential); steps 3-4 are subagents (independence, persona mismatch, self-contained units — all three of P1-LA7's first three decision signals apply).

---

## 3. Validator subagent — full contract

**Intuition first.** Think of the validator as a compliance officer who is handed a *finished trade ticket and its P&L*, not a transcript of the trader's internal thought process while building the position. They don't re-derive the P&L from scratch (that's the back office's job, already done and audited); they check whether the trade was booked using an approach that would survive an audit. That's exactly what this subagent does to a factor-research run.

### 3a. Invocation payload — locked field list

| Field | Source | Why the validator needs it |
|---|---|---|
| `factor_spec` | P1-LA4 `FactorSpec`, re-serialized (per P1-Arch-2's object-handling convention) | What was actually tested — universe, lookback, exclusions |
| `factor_metrics_result` | P1-Arch-2's provisional `FactorMetricsResult` | IC, rank IC, t-stat, hit rate, Sharpe, etc. — the numbers to sanity-check |
| `run_metadata` | New this lesson — see below | Backtesting-rigor context the raw metrics alone can't reveal |

**`run_metadata` is a new object this lesson has to introduce**, because without it the validator literally cannot do the one job the entire Backtesting Rigor track (P1-LB1-LB3) exists to support. A number like `rank_ic_mean: 0.041` tells the validator nothing about *how many other configurations were tried before this one was reported* — and P1-LB3 established that exact fact is what separates an honest result from a p-hacked one. Locked fields:

```
RunMetadata:
  variants_tested: int            # how many factor/lookback combos were tried this session
  holdout_touched: bool           # was the untouched holdout evaluated, per P1-LB2 discipline
  universe_wide_zscore_diff: float | None   # magnitude of divergence from sector-neutral (P1-L4 diagnostic)
  walk_forward_window_type: Literal["rolling","expanding"]
```

This is a genuine new decision, not a restatement: **the orchestrator's native pipeline code must track `variants_tested` and `holdout_touched` as it runs**, because these are facts about the *research process*, not facts computable from a single `FactorMetricsResult`. Carried forward to P1-Build-5/6 below.

### 3b. What the validator does NOT get, and why that's the point

No raw price DataFrame. No orchestrator reasoning trail (steps 1-2's `reason`/`act`/`observe` events). No memory of prior runs. This is P1-LA7's independence rationale, restated with the actual field list now nailed down instead of "a compact handoff."

### 3c. Does the validator get tool access?

**Locked decision (new this lesson): no.** The validator has zero tools — no MCP access, no native tool-use surface, nothing. It reasons entirely over what's in the invocation payload above.

This deserves the explain-back test, because the tempting wrong answer is "shouldn't the validator be able to double-check the numbers itself, maybe re-pull five years of prices and recompute the IC?" Here's why that's wrong for this system specifically:

- P1-Arch-1 already classified `factor_metrics_result`'s computation as **deterministic** (unit-tested Python, same input → same output every time). Re-deriving arithmetic that a unit-tested function already produces correctly adds cost and latency for zero marginal reliability gain — you'd be asking an LLM to re-check a calculator's addition.
- Giving the validator its own data access would violate P1-Arch-2's MCP-invocation-locus decision (raw price data must never enter any model's context) and reopen the exact ~100-round-trip problem that decision was designed to prevent.
- The validator's actual value-add is **methodology judgment** — was the process honest — which is a reasoning task over already-computed facts, not a re-computation task. "Was multiple testing disclosed" isn't something a tool call answers; it's something you check by reading `run_metadata.variants_tested` and reasoning about whether the reported significance accounts for it.

Deterministic-vs-agentic (P1-Arch-1's organizing lens) resurfaces here in a sharper form: **give an agentic component tools only for the kind of work tools are good at (fetching, computing); give it nothing but reasoning for the kind of work reasoning is good at (judging).** A validator with tool access to redo already-correct arithmetic is solving a problem that doesn't exist while leaving its actual job (methodology judgment) no better served.

### 3d. Return contract

`ValidationResult` was already locked in P1-LA7/LA9 (`passed: bool`, `flags: list[str]`, `severity: Literal["none","advisory","blocking"]`). This lesson adds nothing to the schema — it locks *which checks populate it*, pulling directly from the carried-forward items already sitting in CONTEXT.md:

| Check | Source lesson | Populates |
|---|---|---|
| Single best-period IC reported without IR/t-stat | P1-L6/P1-LB3 | flag, severity≥advisory |
| `variants_tested` > 1 with no correction applied | P1-LB3 | flag, severity=blocking |
| `holdout_touched` more than once, or touched then strategy changed | P1-LB2 | flag, severity=blocking |
| `universe_wide_zscore_diff` sharply divergent from sector-neutral | P1-L4 | flag, severity=advisory |
| Novel-factor framing without Harvey-Liu-Zhu t>3.0 acknowledgment | P1-LB3 | flag, severity=advisory |

This table is the actual system-prompt content for the validator subagent at build time — a direct, load-bearing artifact of this lesson.

---

## 4. Memo subagent — full contract

**Intuition.** The memo writer is a different kind of specialist entirely — not a reviewer, a communicator. It's handed the finished, signed-off trade file (including whatever compliance flagged) and asked to write the client-facing summary. It doesn't re-litigate whether the trade was sound; it has to represent, honestly, what was found — including the flags.

### 4a. Invocation payload

| Field | Source |
|---|---|
| `factor_spec` | Same object, re-serialized fresh for this subagent per P1-Arch-2 |
| `factor_metrics_result` | Same object |
| `validation_result` | The validator's own output — **this is the new cross-subagent dependency this lesson makes explicit** |

That third row is worth pausing on. The memo subagent's invocation payload includes another subagent's *output*, not the orchestrator's own reasoning about that output. This is a subtle but real distinction: the orchestrator is a pass-through for `validation_result` here, not a re-interpreter of it. If the orchestrator silently summarized or softened the validator's flags before handing them to the memo writer, that would defeat P1-L8's bias-disclosure pattern (honest disclosure of limitations) just as surely as omitting the flags entirely. **Locked: `validation_result` is passed to the memo subagent verbatim, never paraphrased by orchestrator code.**

### 4b. Tool access

**Locked: also none.** Same reasoning as the validator — the memo subagent's job is prose generation from already-final structured facts, not fact-gathering.

### 4c. Return contract — new schema this lesson

Unlike the validator, nothing existing locked a structured return type for the memo. Free text alone would violate the standing structured-outputs boundary principle ("every pipeline stage's tool or function should return a small structured object, not a raw computation dump"). New schema:

```
MemoResult:
  memo_markdown: str          # the actual memo content
  disclosed_flags: list[str]  # which of validation_result.flags actually appear in the memo text
  word_count: int             # feeds P1-LE1's future anti-verbosity-bias eval directly
```

`disclosed_flags` is the load-bearing new field. It gives you a **mechanical, code-checkable audit**: does `disclosed_flags` actually cover every entry in the `validation_result.flags` list it was handed? If the memo subagent quietly drops a flag the validator raised, that's now a detectable schema-level mismatch (`set(disclosed_flags) ⊇ set(validation_result.flags)`), not something you'd only catch by reading the memo carefully. This is the same instinct as P1-LA9's "Thought masquerading as Observation" pattern, applied one level up: don't rely on trusting the model told the truth — build a structural check that would catch it if it didn't.

---

## 5. Failure propagation — the three-way distinction

This is the core new concept of the lesson. A subagent call can end in exactly three distinguishable ways, and conflating any two of them is a real design bug, not a stylistic choice.

| Outcome | What actually happened | Who/what decided this | Orchestrator's response |
|---|---|---|---|
| **A — Internal retry succeeds** | Subagent's own final answer failed Pydantic validation once or twice; retry-with-feedback (P1-LA9) fixed it *inside that same subagent conversation* | Handled entirely inside the subagent's own loop, invisible to the orchestrator | Proceed normally — orchestrator never even sees that a retry happened (though it's logged, see §7 of the chat lesson / trace design in P1-LA12) |
| **B — Terminal failure** | Subagent exhausted its retry cap (3 attempts, P1-LA9) and still can't produce schema-valid output | A reliability failure — nobody's fault, nothing to escalate a judgment about, the pipeline simply couldn't complete the step | **Halt, unconditionally.** No score computed. This is not what P1-LA11's escalation framework is for. |
| **C — Successful call, bad-news payload** | Subagent produced a perfectly valid, schema-conforming result — and that result happens to be `severity="blocking"` | The subagent did its job correctly; the *content* of a correct answer is the problem | **Halt, conditionally** — gated on the pre-assigned score for that severity level clearing the ≥12 threshold (P1-LA11) |

**Why B and C must never be merged into one generic "something went wrong, stop" bucket:** B is a statement about the *system's ability to execute*; C is a statement about the *quality of the research being reviewed*. A postmortem on a B-type halt asks "why can't our validator reliably produce valid JSON" (a P1-LA9 reliability question, fixed by improving prompts/schemas/retry logic). A postmortem on a C-type halt asks "what did the validator correctly catch, and was the researcher's process actually sound" (a P1-LA11 governance question, and arguably a *success* of the system, not a failure of it). Interview-worthy distinction: **a system that halts on B is broken; a system that halts on C is working exactly as designed.** Collapsing them into one "escalation" bucket would make a healthy governance stop look identical to a bug, which is exactly the kind of ambiguity a trace should never have (P1-LA12's whole reason for existing).

### 5a. New wrapper type this decision requires: `SubagentCallResult`

To let orchestrator code actually branch on A/B/C cleanly, it needs a wrapper around whatever the subagent itself returns:

```
SubagentCallResult:
  agent: Literal["validator_subagent", "memo_subagent"]
  status: Literal["ok", "failed"]
  retries_used: int
  result: ValidationResult | MemoResult | None   # populated only if status == "ok"
  error_summary: str | None                       # populated only if status == "failed"
```

`status="failed"` is outcome B. `status="ok"` with `result.severity=="blocking"` (for the validator) is outcome C. `status="ok"` with everything else is the happy path. One wrapper, one clean `if/elif` in the orchestrator's own code — no ambiguity about which of the three outcomes occurred.

### 5b. What happens on each branch, concretely

- **Validator, status="failed" (outcome B):** Orchestrator halts the run. No escalation score computed (per the table in §6 — this isn't a governance judgment, it's an inability to complete step 3). UI shows: "Validation could not be completed after 3 attempts — please retry or review manually." Logged as a distinct trace event.
- **Validator, status="ok", severity="blocking" (outcome C):** Plan step 4 (memo) is marked `status="blocked"`, never invoked. This *is* the P1-LA6-style plan revision, in its simplest possible form for this project — there's no further downstream step to rewrite, so "revision" collapses to "don't execute the one remaining step." Orchestrator emits a paired `escalation` TraceEvent (P1-LA12) and returns the `ValidationResult` itself to the UI as the run's final output, with an explicit "escalated for human review" framing.
- **Validator, status="ok", severity ∈ {"none","advisory"}:** Proceed to step 4, passing `validation_result` verbatim into the memo subagent's invocation payload.
- **Memo, status="failed" (outcome B):** **Locked decision, new this lesson:** the orchestrator does *not* silently return the metrics without a memo as a "partial success." A factor-research request without its memo is an incomplete deliverable — this is escalated via the same P1-LA11 human-in-the-loop framing as any other unresolvable failure, not quietly downgraded. (You could imagine a system where a missing memo is treated as "good enough, just show the raw numbers" — explicitly rejected here, because it would make silent degradation the default behavior, which is exactly the kind of thing P1-L2/L8's "disclose limitations, don't paper over them" instinct argues against.)

---

## 6. Escalation scoring made concrete: a pre-assigned lookup, not a live computation

CONTEXT.md's locked decision says the Consequence × Reversibility × Confidence-gap score is "pre-assigned by designer at design time, not computed live." Up to now that was a principle. Here's the actual table this design requires — this *is* what "pre-assigned" cashes out to in code:

| Event | Consequence | Reversibility | Confidence-gap | Score | ≥12? | Checkpoint? |
|---|---|---|---|---|---|---|
| Validator `severity="none"` | 1 | 1 | 1 | 1 | No | No — proceed |
| Validator `severity="advisory"` | 1 | 1 | 1 | 1 | No | No — proceed, but flags carried into memo |
| Validator `severity="blocking"` | 3 | 2 | 2 | 12 | Yes | **Yes — halt** |
| Any subagent `status="failed"` (outcome B) | — | — | — | — | n/a | **Halt unconditionally — not scored** |

The crucial mechanical point: this table lives in **application code as a static dict** (`SEVERITY_SCORE = {"none": 1, "advisory": 1, "blocking": 12}`), keyed off the validator's `severity` field. The LLM never computes a score itself — it only ever produces `severity`, a closed three-value `Literal`, and deterministic code looks up the pre-assigned number. This is precisely what "pre-assigned, not computed live" was pointing at, now given an actual implementation shape you can code directly.

---

## 7. Data-access and network-egress table — closing the two carried-forward items

This resolves the two open items from P1-Arch-1 and P1-Arch-2 about annotating per-agent access scope on the diagram.

| Component | Reads price/market data? | Own MCP/tool access? | Network egress of its own? |
|---|---|---|---|
| Orchestrator | Indirectly — via the single `run_research_pipeline` native call (P1-Arch-2's invocation-locus decision) | Yes — `run_research_pipeline`, `validator_subagent` invoke, `memo_subagent` invoke | Only through that one native call's internal MCP client |
| **Validator subagent** | **No** | **No** | **No** |
| **Memo subagent** | **No** | **No** | **No** |

That last two rows are the point, and they're worth stating in the strong form: it's not merely that the two subagents are *scoped down* to reduce risk (a P1-LA10 mitigation) — it's that **the exfiltration chain P1-LA10 described (read access + outbound capability in the same agent) is architecturally impossible for either subagent, because neither condition is true for either one.** This isn't a policy the model has to honor; there's no function to call that would let it happen. That's the deterministic-access-control principle from P1-LA10 ("prefer a function that simply doesn't exist over a prompted instruction not to call it"), now demonstrated concretely rather than stated abstractly.

**Action item:** this table needs to be reflected as an annotation on the actual `project_01_factor_research.drawio` file by hand in the draw.io app, using this table as the source content — Claude cannot edit that binary/XML diagram file directly since it isn't in project knowledge in this conversation.

---

## 8. Full worked trace — both branches

Reusing the "Test 12-month momentum on NASDAQ-100" example one more time, now zoomed into steps 3-4 with two concrete forks.

**Setup (shared):** `factor_spec` = 12-month momentum, NASDAQ-100, monthly rebalance. `factor_metrics_result` = rank_ic_mean 0.041, sharpe 0.62. `run_metadata` = `variants_tested: 3` (the researcher quietly also tried 9-month and 6-month lookbacks before landing on 12-month), `holdout_touched: false`, `universe_wide_zscore_diff: 0.04` (small, unremarkable).

### Branch 1 — undisclosed multiple testing (severity="blocking")

| Step | Event |
|---|---|
| Orchestrator invokes validator | Payload: `factor_spec`, `factor_metrics_result`, `run_metadata{variants_tested: 3, ...}` |
| Validator reasons | "`variants_tested=3` but no correction (Bonferroni/FDR) applied anywhere in the metrics; per P1-LB3, this alone doesn't invalidate the finding but it must be disclosed and adjusted for" |
| Validator returns | `ValidationResult(passed=False, flags=["3 variants tested, no multiple-testing correction applied"], severity="blocking")` |
| `SubagentCallResult` | `status="ok"`, `result=<above>` — this is outcome **C**, not B |
| Escalation lookup | `severity="blocking"` → score 12 → ≥12 → checkpoint required |
| Orchestrator | Step 4 (memo) marked `blocked`; escalation `TraceEvent` emitted; run returns the `ValidationResult` to the UI, memo never generated |

### Branch 2 — advisory only (proceeds to memo)

Same setup but `variants_tested: 1` (only 12-month was ever tried), `universe_wide_zscore_diff: 0.31` (larger — flagged as a possible sector-bet contamination).

| Step | Event |
|---|---|
| Validator returns | `ValidationResult(passed=True, flags=["Sector-neutral vs. universe-wide z-score diverges materially — possible sector concentration"], severity="advisory")` |
| Escalation lookup | `severity="advisory"` → score 1 → no checkpoint |
| Orchestrator | Step 4 proceeds; memo subagent invoked with `validation_result` passed through verbatim |
| Memo subagent returns | `MemoResult(memo_markdown="...", disclosed_flags=["Sector-neutral vs. universe-wide z-score diverges materially..."], word_count=340)` |
| Audit check | `set(disclosed_flags) ⊇ set(validation_result.flags)` → True, passes |
| Orchestrator | Returns memo + metrics to UI |

---

## 9. Sequence diagram (steps 3-4 only — zooms into what P1-Arch-2's Stage 3/4 left compact)

```
Orchestrator                Validator subagent            Memo subagent
    |                              |                              |
    |--(1) invoke, payload:------->|                              |
    |   factor_spec,               |                              |
    |   factor_metrics_result,     |                              |
    |   run_metadata               |                              |
    |                              |--(internal loop, own         |
    |                              |   retry-with-feedback,       |
    |                              |   no tools, isolated ctx)    |
    |<--(2) SubagentCallResult-----|                              |
    |   status=ok/failed           |                              |
    |                              |                              |
    |--[branch: status=failed]---> HALT (outcome B, unconditional, no score)
    |                              |                              |
    |--[branch: severity=blocking]-> HALT (outcome C, score=12, escalation TraceEvent)
    |                              |                              |
    |--[branch: severity=none/advisory]--------------------------|
    |                                                             |
    |--(3) invoke, payload:------------------------------------->|
    |   factor_spec, factor_metrics_result,                      |
    |   validation_result (verbatim)                             |
    |                                                             |--(internal loop,
    |                                                             |   no tools, isolated ctx)
    |<--(4) SubagentCallResult------------------------------------|
    |   result: MemoResult{memo_markdown, disclosed_flags, wc}   |
    |                                                             |
    |--(5) audit: disclosed_flags ⊇ validation_result.flags ------|
    |--(6) return memo + metrics to UI                            |
```

---

## 10. Explicit new locked decisions from this lesson

1. `RunMetadata` object introduced (`variants_tested`, `holdout_touched`, `universe_wide_zscore_diff`, `walk_forward_window_type`) — orchestrator's native pipeline must track and populate it.
2. Neither subagent gets tool access — locked with rationale (deterministic work is already done; agentic work here is judgment, not fetching).
3. `validation_result` passed to memo subagent verbatim, never paraphrased by orchestrator code.
4. New `MemoResult` schema, with `disclosed_flags` as a mechanically auditable field.
5. `SubagentCallResult` wrapper formalizes the three-way outcome distinction (A/B/C).
6. **B vs. C is a hard conceptual split**: terminal subagent failure halts unconditionally with no escalation score; a successful-but-blocking result halts conditionally, gated by the pre-assigned score table.
7. Escalation score table is a static code-side dict keyed on `severity`, confirming "pre-assigned, not computed live" in implementable form.
8. Memo-subagent terminal failure (outcome B) is treated as a full escalation, not silently downgraded to "return metrics without a memo."
9. Data-access/egress table: both subagents have zero data access and zero egress — architecturally, not just by convention.
10. Confirmed (not new, restated with the concrete objects now in hand): validator and memo subagent calls cannot be parallelized here, since the memo subagent's invocation payload has a hard data dependency on the validator's `ValidationResult` (P1-LA9's general point about sequential-dependency subagent calls, now shown concretely for this pair).

---

## Carried-forward action items

- **→ P1-Arch-4:** `RunMetadata` needs to become an actual Pydantic model alongside the `FactorMetricsResult` finalization already scheduled there. Also finalize `SubagentCallResult` and `MemoResult` as real Pydantic models (with `result` as a proper discriminated union rather than the loose `ValidationResult | MemoResult | None` sketched here).
- **→ P1-Build-1/5/6:** native pipeline code must track `variants_tested` (increment on every distinct factor/lookback configuration run in a session) and `holdout_touched` (boolean flag, set once the holdout function/flag from P1-LB2 is invoked) — these are process facts, not derivable after the fact from a single run's metrics.
- **→ P1-Build-7 (orchestrator):** implement the `SubagentCallResult` A/B/C branching exactly as specified in §5b; implement the static `SEVERITY_SCORE` lookup dict from §6, not a live model-computed score.
- **→ P1-Build-8 (validator/memo subagents):** validator system prompt should encode the five-row check table from §3d directly; memo subagent must be prompted to populate `disclosed_flags`, and the orchestrator (or memo subagent itself) should assert the `disclosed_flags ⊇ validation_result.flags` audit check before returning to the UI.
- **→ P1-Build-7/12 (UI/orchestrator):** open item, not resolved this lesson — should a human be able to override a `severity="blocking"` halt and force memo generation anyway from the Streamlit UI? Flagged as a design question for the build phase, not decided here.
- **→ diagram maintenance (manual, outside chat):** add the §7 data-access/egress table as an annotation to `project_01_factor_research.drawio` by hand in the draw.io app, using that table as the source content. This closes the P1-Arch-1 and P1-Arch-2 carried-forward items in substance (the design decision is locked here) but the physical diagram file itself still needs the manual update.

---

## 11. Follow-up (2026-07-22, same session): full end-to-end validator invocation simulation

Simulated a complete validator call against the locked contract, to check it actually runs cleanly end to end. Scenario: "Test 12-month momentum on NASDAQ-100, excluding the most recent month," with `rank_ic_mean=0.041`, `ic_tstat=2.14`, and `run_metadata` set to `variants_tested=1`, `holdout_touched=false`, `universe_wide_zscore_diff=0.31` (materially larger than the earlier 0.04 benchmark example).

### 11a. Invocation payload

```json
{
  "factor_spec": {
    "hypothesis_text": "Test 12-month momentum on NASDAQ-100, excluding the most recent month",
    "factor_type": "momentum",
    "universe": "NASDAQ100",
    "lookback_months": 12,
    "exclusion_months": 1,
    "rebalance_frequency": "monthly",
    "long_short": true
  },
  "factor_metrics_result": {
    "ic_mean": 0.037, "ic_tstat": 2.14, "rank_ic_mean": 0.041, "hit_rate": 0.54,
    "sharpe": 0.62, "sortino": 0.79, "max_drawdown": -0.183, "calmar": 0.41,
    "beta_to_market": 0.06, "beta_long_leg": 1.14, "beta_short_leg": 1.08,
    "turnover_cost_drag_bps": 30, "holdout_split": "2022-01–2024-12"
  },
  "run_metadata": {
    "variants_tested": 1,
    "holdout_touched": false,
    "universe_wide_zscore_diff": 0.31,
    "walk_forward_window_type": "rolling"
  }
}
```

### 11b. Validator's internal processing, walked check-by-check against the §3d table

| Trace event | event_type | Reasoning |
|---|---|---|
| 1 | `perceive` | Received invocation payload |
| 2 | `reason` | Check 1 (best-period IC w/o IR) — `ic_tstat=2.14` present alongside `rank_ic_mean` → pass |
| 3 | `reason` | Check 2 (variants tested, no correction) — `variants_tested=1`, nothing to correct → pass |
| 4 | `reason` | Check 3 (holdout discipline) — `holdout_touched=false` → pass |
| 5 | `reason` | Check 4 (sector-neutral vs. universe-wide divergence) — `universe_wide_zscore_diff=0.31`, materially larger than the ~0.04 unremarkable benchmark used elsewhere → **FLAG, advisory** |
| 6 | `reason` | Check 5 (novel-factor framing) — hypothesis is standard, well-replicated momentum, not framed as novel → n/a, pass |
| 7 | `act` | Emit final `ValidationResult` |

### 11c. Return value

```json
{
  "passed": true,
  "flags": ["Sector-neutral z-score diverges materially from universe-wide z-score (0.31) — signal may reflect sector concentration rather than a clean momentum effect"],
  "severity": "advisory"
}
```

Wrapped by orchestrator code: `SubagentCallResult(agent="validator_subagent", status="ok", retries_used=0, result=<above>, error_summary=None)`. `SEVERITY_SCORE["advisory"]=1` → below threshold → proceeds to memo subagent with this `ValidationResult` passed through verbatim.

### 11d. New design insight surfaced by running the simulation, not previously stated

**A tool-less subagent's trace profile is structurally narrower than the orchestrator's.** The orchestrator's own steps emit the full `perceive`/`reason`/`act`/`observe` cycle (P1-LA1/LA2) because it actually calls tools. The validator and memo subagents — zero tool access, per §3c/4b's locked decision — can only ever emit `perceive` (once, on receiving the payload), `reason` (once per judgment step), and `act` (once, on final structured output). **`observe` is structurally impossible for either subagent**, since `observe` is defined (P1-LA1/LA12) as a real fact returned by a tool call, and neither subagent has any tools to call.

This becomes a free, code-checkable trace invariant for P1-Build-7/8: **if a `TraceEvent` tagged `agent="validator_subagent"` or `agent="memo_subagent"` ever has `event_type="observe"`, that alone indicates the isolation boundary has been violated** — the subagent somehow gained tool access it shouldn't have by design. Worth building as an automated trace-linter check at build time, not just a documented expectation.

**Carried forward → P1-Build-7/8:** add a trace-validation check (unit test or lightweight linter over a completed run's `TraceEvent` log) asserting zero `observe`-type events for any `agent` value other than `"orchestrator"`.

---

## 12. Follow-up (2026-07-22, same session): full end-to-end memo subagent invocation simulation

Continued directly from the §11 validator simulation — this is plan step 4, invoked because the validator returned `severity="advisory"` (below the escalation threshold). The memo subagent receives the validator's own `ValidationResult` verbatim, per the §4a locked decision.

### 12a. Invocation payload

```json
{
  "factor_spec": { "...same FactorSpec as §11a..." },
  "factor_metrics_result": { "...same FactorMetricsResult as §11a..." },
  "validation_result": {
    "passed": true,
    "flags": ["Sector-neutral z-score diverges materially from universe-wide z-score (0.31) — signal may reflect sector concentration rather than a clean momentum effect"],
    "severity": "advisory"
  }
}
```

This is a *different* fresh context from the validator's own — no memory of the validator's five-check internal reasoning trail, only its final structured verdict, passed through unedited.

### 12b. Memo subagent's internal processing

| Trace event | event_type | Reasoning |
|---|---|---|
| 1 | `perceive` | Received invocation payload |
| 2 | `reason` | Draft structure per house style: hypothesis → key metrics → risk/limitations → conclusion |
| 3 | `reason` | `validation_result.flags` has one entry (sector-concentration flag) which must appear in the memo body, not summarized away — per the §4a verbatim-disclosure lock |
| 4 | `reason` | Metrics framing: `rank_ic_mean=0.041` / `ic_tstat=2.14` is modest-but-statistically-present — state plainly, avoid oversized "strong signal" language (P1-LA16 tone-mismatch lesson) |
| 5 | `act` | Emit final `MemoResult` |

Same tool-less-subagent invariant as §11 (zero `observe` events). But note the *shape* differs from the validator's loop: the validator's reasoning is a fixed, enumerable five-row checklist; the memo subagent's reasoning is open-ended drafting judgment. Both loops are tool-less, but "no `observe` events" is a shared structural constraint, not evidence the two loops work the same way — worth stating explicitly rather than leaving implicit.

### 12c. Structured return

```json
{
  "memo_markdown": "## Factor Research Memo — 12-Month Momentum, NASDAQ-100\n\n**Hypothesis:** 12-month price momentum, excluding the most recent month, tested on the NASDAQ-100 universe with monthly rebalancing and an equal-weighted long-short construction.\n\n**Results:** The signal shows a modest but statistically present effect — mean rank IC of 0.041 (t-stat 2.14), a 54% hit rate, and an annualized Sharpe ratio of 0.62. Maximum drawdown over the holdout period (2022–2024) was -18.3%, with a Calmar ratio of 0.41. Net market beta was near zero (0.06), consistent with the dollar-neutral long-short construction. Estimated transaction cost drag was 30 bps.\n\n**Methodology flag:** The sector-neutral and universe-wide versions of this signal diverge materially (z-score difference of 0.31), which may indicate the signal is partly capturing sector concentration rather than a clean cross-sectional momentum effect. This should be investigated before sizing this signal aggressively.\n\n**Conclusion:** A modest, statistically supported momentum effect, with an open methodology question about sector contamination that a portfolio manager should weigh before acting on this in isolation.",
  "disclosed_flags": ["Sector-neutral z-score diverges materially from universe-wide z-score (0.31) — signal may reflect sector concentration rather than a clean momentum effect"],
  "word_count": 148
}
```

Wrapped: `SubagentCallResult(agent="memo_subagent", status="ok", retries_used=0, result=<above>, error_summary=None)`.

### 12d. Orchestrator audit check

```
set(disclosed_flags) ⊇ set(validation_result.flags) → True, audit passes
```

Run completes; memo + metrics returned to UI.

### 12e. Two new open design gaps surfaced by running this simulation

1. **The memo subagent's internal loop is a different shape from the validator's**, even though both share the tool-less "no `observe` events" constraint from §11d — the validator's reasoning is a fixed, enumerable checklist; the memo subagent's is open-ended drafting judgment. Worth stating as a contrast, not treating the shared constraint as evidence the two loops are equivalent.

2. **What the orchestrator does when the §12d audit check actually *fails*** (`disclosed_flags` doesn't cover `validation_result.flags`) was never decided — the lesson only asserted the check exists. Two live options, not resolved here: (a) treat it as a malformed-output retry, feeding the mismatch back into the memo subagent's own conversation as corrective feedback, capped at the standard 3 attempts (the P1-LA9 pattern); or (b) treat it as its own outcome type, distinct from the A/B/C taxonomy in §5 — a swallowed flag is neither a reliability failure (B, the subagent *did* produce valid-shaped output) nor bad-news content (C, the subagent is actively *failing* to report bad news rather than reporting it) — genuinely doesn't fit either bucket cleanly.

**Carried forward → P1-Arch-4 or P1-Build-8:** decide what the orchestrator does when the `disclosed_flags ⊇ validation_result.flags` audit check fails — retry-with-feedback (option a) vs. a new fourth outcome type alongside A/B/C (option b). Not resolved this session.

---

**Deliverable:** This notes file, plus the inline sequence diagram above (steps 3-4 zoom), plus the §11 worked validator simulation and §12 worked memo subagent simulation.
**Estimated time:** 2-3 hours
