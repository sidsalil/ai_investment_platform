# P1-LA7: Subagents & Multi-Agent Orchestration

**Track:** AI/Agentic (7 of 17)
**Date completed:** 2026-07-15
**Estimated time:** 2 hours

---

## 1. The problem this lesson solves

Every lesson in this track so far has been about making **one agent** better at what it does: giving it tools (LA2), a standard way to reach those tools (LA3, Model Context Protocol (MCP)), a way to produce reliable output (LA4), a way to reason visibly step-by-step (LA5, ReAct), and a way to hold a persistent plan across many steps (LA6). All of that still describes **one Claude conversation, doing one job, with one system prompt.**

Project 1's target architecture — locked back on 2026-07-11 — is not that. It's an orchestrator that delegates to a **validation subagent** and a **memo-writing subagent**. This lesson is about *why* that's the right shape, not just "more AI is more impressive." There are three concrete problems a single, do-everything agent runs into as a task grows, and multi-agent orchestration is the direct answer to each:

| Problem with one big agent | Plain-language version |
|---|---|
| **Context bloat** | Every tool call and every reasoning step from stage 1 is still sitting in the conversation by stage 7, whether or not it's relevant to stage 7's job |
| **Conflict of interest** | The same agent that built the factor and ran the backtest is a biased reviewer of its own work — it already "believes" its conclusions |
| **Persona mismatch** | "Build a momentum factor" and "write a polished client-facing memo" and "aggressively hunt for methodology problems" are three different jobs that want three different instructions, tones, and even different levels of skepticism |

Multi-agent orchestration means: instead of forcing one agent to be a builder, a skeptical auditor, and a writer all at once, you give each job its own agent, with its own system prompt and its own (usually much smaller) context window, and you have one agent — the **orchestrator** — coordinate them.

---

## 2. What a subagent actually is, mechanically

Here's the important thing to get right, because it's easy to think a subagent is some special new kind of object. **It isn't.** A **subagent** is just another Claude conversation — its own sequence of messages, its own system prompt, potentially its own tools, potentially its own internal ReAct or planning loop — that gets started, run to completion, and then handed back a result.

From the **orchestrator's point of view**, invoking a subagent looks exactly like a tool call from LA2: the orchestrator "calls" something, waits, and gets an "Observation" back. The five-step tool-use cycle from LA2 still applies almost unchanged:

| LA2's 5-step tool cycle | Same step, subagent version |
|---|---|
| 1. Model decides to call a tool, with some input | Orchestrator decides to delegate a task, with some input (e.g., the `FactorSpec` + backtest results) |
| 2. Application code executes the tool | Application code starts a **new, separate** Claude conversation — a fresh context window — with its own system prompt, and feeds it the input |
| 3. The tool produces a result | The subagent runs its own internal loop (maybe just one turn, maybe its own ReAct loop with its own tools) until it produces a final answer |
| 4. Result is returned to the model as an Observation | The subagent's final answer is packaged (ideally as a structured object, per LA4) and returned to the orchestrator as an Observation |
| 5. Model continues, having "seen" the result | Orchestrator continues its own plan (per LA6), incorporating the subagent's result |

**The one thing that's genuinely different from a normal tool call:** a normal tool (like "get 12 months of price history") is deterministic-ish and doesn't reason. A subagent is itself an LLM invocation — it can reason, it can call its own tools, it can even fail or hallucinate in its own right. You're not calling a function; you're delegating a piece of judgment to a separate instance of the same kind of intelligence, with a narrower job and a narrower view of the world.

**Analogy from your background:** think of the difference between a trading desk calling a Bloomberg terminal for a price (a deterministic tool — same input always gives the same kind of output) versus a trading desk sending a proposed trade to an independent risk/compliance reviewer before it books (a subagent — a separate person with their own judgment, own mandate, and deliberately incomplete visibility into the trader's internal reasoning, because that incompleteness is the point).

---

## 3. The orchestrator-worker pattern

The specific shape used in Project 1 (and the most common multi-agent shape generally) is called **orchestrator-worker**: one agent (the **orchestrator**) owns the overall plan and goal, and dispatches well-defined sub-tasks to one or more **worker subagents**, each specialized for a narrower job. The orchestrator never hands off "the whole problem" — it hands off a specific, bounded piece of it, waits for a specific, bounded result, and stays in charge of deciding what happens next.

This is directly the multi-agent point on the autonomy spectrum locked in P1-LA1: fixed workflow → single tool-use loop → ReAct loop → planning loop → **multi-agent orchestration**. Notice what's actually changing as you move right along that spectrum — it's *not* "more autonomy in one brain." It's: first, autonomy over *what to do next* (tool-use loop); then, autonomy over *how to decide, visibly, at each step* (ReAct); then, autonomy over *the whole sequence, held as a plan* (planning loop); and now, autonomy over ***who* does each piece of that plan** — a plan can name a subagent as the owner of a step, not just "the orchestrator does it."

That last sentence is the direct bridge from LA6: the plan object you built last lesson (a list of steps, each with an `id`, `description`, `status`) gets one new field this lesson: **`owner`** — is this step executed by the orchestrator itself, or delegated to a named subagent? Nothing else about the plan mechanics changes.

### 3.1 Worked example: the LA6 plan object, extended with `owner`

Here's the actual before/after, so the "one new field" claim above is concrete rather than abstract. First, recall the shape of a plan object from P1-LA6 — nothing about `id`, `description`, or `status` changes here:

```json
{
  "plan": [
    {
      "id": 1,
      "description": "Fetch price, universe, and sector data for the NASDAQ-100",
      "status": "done"
    },
    {
      "id": 2,
      "description": "Compute raw 12-month momentum factor, winsorize, sector-neutral z-score",
      "status": "done"
    },
    {
      "id": 3,
      "description": "Portfolio construction: quintile bucketing, long-short equal-weighted",
      "status": "done"
    },
    {
      "id": 4,
      "description": "Run backtest: returns, turnover, transaction costs",
      "status": "done"
    },
    {
      "id": 5,
      "description": "Compute metrics: rank IC, IR, Sharpe, Sortino, max drawdown, beta-to-market",
      "status": "done"
    },
    {
      "id": 6,
      "description": "Validate methodology: check for look-ahead bias, single-window reporting, incomplete metrics",
      "status": "pending"
    },
    {
      "id": 7,
      "description": "Write research memo summarizing hypothesis, results, and limitations",
      "status": "pending"
    }
  ]
}
```

Now, the **only structural change this lesson makes** — every step gets one new field, `owner`, naming who executes it. Steps 1-5 name `"orchestrator"`; steps 6-7 name a specific subagent:

```json
{
  "plan": [
    {
      "id": 1,
      "description": "Fetch price, universe, and sector data for the NASDAQ-100",
      "owner": "orchestrator",
      "status": "done"
    },
    {
      "id": 2,
      "description": "Compute raw 12-month momentum factor, winsorize, sector-neutral z-score",
      "owner": "orchestrator",
      "status": "done"
    },
    {
      "id": 3,
      "description": "Portfolio construction: quintile bucketing, long-short equal-weighted",
      "owner": "orchestrator",
      "status": "done"
    },
    {
      "id": 4,
      "description": "Run backtest: returns, turnover, transaction costs",
      "owner": "orchestrator",
      "status": "done"
    },
    {
      "id": 5,
      "description": "Compute metrics: rank IC, IR, Sharpe, Sortino, max drawdown, beta-to-market",
      "owner": "orchestrator",
      "status": "done"
    },
    {
      "id": 6,
      "description": "Validate methodology: check for look-ahead bias, single-window reporting, incomplete metrics",
      "owner": "validator_subagent",
      "status": "pending",
      "handoff": {
        "factor_spec": "<FactorSpec object from step 0>",
        "metrics": "<output of step 5>"
      }
    },
    {
      "id": 7,
      "description": "Write research memo summarizing hypothesis, results, and limitations",
      "owner": "memo_subagent",
      "status": "pending",
      "handoff": {
        "factor_spec": "<FactorSpec object from step 0>",
        "metrics": "<output of step 5>",
        "validation_result": "<output of step 6, once done>"
      }
    }
  ]
}
```

Three things worth noticing about this extended version, all direct consequences of earlier sections:

- **`owner` is the only new field on the plan step itself** — exactly as claimed above. `id`, `description`, and `status` are untouched, so the orchestrator's existing plan-tracking logic (marking steps done, checking for revision triggers per LA6) needs no rework to support multi-agent steps.
- **The optional `handoff` field is new, but only appears on subagent-owned steps** — it's the compact, structured payload from Section 5/6 (not the orchestrator's full reasoning trail) that gets passed when that step is actually dispatched. Steps 1-5 don't need a `handoff` field at all, because the orchestrator is simply continuing its own single, continuous context — there's no separate conversation to hand anything to.
- **Step 6's `handoff` deliberately excludes** the orchestrator's stage 1-5 tool-call and reasoning history — only the final `FactorSpec` and `metrics` objects cross the boundary. This is the JSON-level enforcement of the Section 5 independence argument: if `handoff` for step 6 included the orchestrator's reasoning trail, the validator subagent would no longer be a genuinely independent reviewer.

When the orchestrator later reads back step 6's result (a `ValidationResult`, per Section 6), it would typically attach that result to the plan as well — e.g., adding a `result` field to step 6 once it completes — so the plan object doubles as the running record of what each agent (self or subagent) actually produced, not just what was assigned.

---

## 4. When to decompose across agents (and when not to)

This is the actual engineering judgment call this lesson is teaching, and it's easy to over-apply — "everything should be its own agent!" is a real anti-pattern that just adds latency and cost for no benefit. Here's the decision table:

| Signal | Decompose into a separate subagent | Keep inside the orchestrator's own loop |
|---|---|---|
| **Persona / instructions needed** | The job wants a genuinely different stance — e.g., "be skeptical and look for problems" vs. "be a fluent explanatory writer" vs. "be a careful builder" | Same stance/persona as the rest of the work |
| **Independence matters** | The result needs to be trustworthy *because* it wasn't produced by the same reasoning that's being checked (validation, auditing, adversarial review) | No conflict-of-interest concern |
| **Context isolation matters** | The sub-task doesn't need (and would be actively hurt by) the full accumulated history of everything that happened earlier | The sub-task genuinely needs the full running context to do its job well |
| **Task is a substantial, self-contained unit of reasoning** | Worth a full separate LLM round-trip (its own latency and token cost) | It's a small, cheap lookup or check — not worth the overhead of spinning up an entirely new conversation |
| **Parallelizable** | Multiple independent sub-tasks could genuinely run at the same time with no dependency between them | Steps are tightly sequential — step 2 needs step 1's exact output before it can even be defined |

Project 1's two subagents (validator, memo-writer) both clear the bar on the *first three* rows, which is exactly why they were locked as subagents rather than just being more stages inside the orchestrator's own planning loop. Stages 1-5 (data fetch → signal construction → portfolio construction → backtest → metrics) stay inside the orchestrator itself, because they don't clear those bars — they're the same "builder" persona throughout, they don't need independence from each other, and each one genuinely depends on full visibility into what came before.

---

## 5. Context isolation and the "grading your own homework" problem — worked numerically

This is worth making concrete with actual token numbers, because "context bloat" can sound like a vague hand-wave otherwise.

**Setup:** suppose each of the orchestrator's 5 self-executed stages (fetch, signal, portfolio construction, backtest, metrics) generates roughly 2,000 tokens' worth of tool calls, tool results, and reasoning text. If one single agent tried to also do validation and memo-writing itself, every subsequent LLM call has to be billed for (and reasoned over) the *entire accumulated context so far* — that's how a conversation's context window works: nothing already in it goes away.

| Stage | Tokens generated this stage | Cumulative context this stage's LLM call must process |
|---|---|---|
| 1. Fetch data | 2,000 | 2,000 |
| 2. Signal construction | 2,000 | 4,000 |
| 3. Portfolio construction | 2,000 | 6,000 |
| 4. Backtest | 2,000 | 8,000 |
| 5. Metrics | 2,000 | 10,000 |
| 6. Validation (same agent, hypothetically) | 2,000 | 12,000 |
| 7. Memo writing (same agent, hypothetically) | 2,000 | 14,000 |

**Total input tokens billed across the run** (summing the cumulative-context column) ≈ 2k + 4k + 6k + 8k + 10k + 12k + 14k = **56,000 tokens**, and the memo-writing call alone is dragging along 12,000 tokens of price-fetching and backtest-mechanics noise that has nothing to do with writing a clear paragraph for a reader.

**Now the subagent version:** the validator and memo-writer each start a **fresh** conversation. They don't get the orchestrator's blow-by-blow reasoning trail — they get a compact, structured handoff object (the `FactorSpec`, the final metrics, maybe ~500 tokens) plus their own system prompt.

| Agent | Context it actually processes |
|---|---|
| Orchestrator, stages 1-5 | 2k + 4k + 6k + 8k + 10k = 30,000 (same as before — this part is unavoidable and appropriate, it's one continuous job) |
| Validator subagent | ~500 tokens (structured handoff only) |
| Memo subagent | ~500 tokens + validator's result (~200 tokens) ≈ 700 tokens |

**Total ≈ 31,200 tokens** — nearly half the cost of the single-agent version, *and* the validator/writer are reasoning over a small, relevant, uncluttered context instead of wading through unrelated stages.

That's the quantifiable half of the argument. Here's the qualitative half, which matters just as much for Project 1's specific validator: **the orchestrator's reasoning trail is exactly the thing the validator is supposed to be checking for errors in.** If the validator subagent inherited that full trail, it would effectively be reading the orchestrator's own justifications for its choices *before* forming its own opinion — the same failure mode as asking a trader to review their own trade ticket while re-reading their own notes about why the trade was a good idea. Structural independence (a genuinely separate context that only sees the *final, structured result* — not the reasoning that produced it) is what makes "the validator caught something the builder missed" a meaningful sentence rather than a formality. This is the direct mechanical reason the validator gets a fresh subagent context rather than just being "stage 6 of the same conversation."

---

## 6. How results get merged back into the orchestrator's plan

A subagent's result re-enters the orchestrator's own loop as an **Observation** — exactly the same slot in the ReAct cycle (LA5) that a tool result occupies. And per LA4, that result should be a **structured object**, not free text, for the same reasons any handoff in this pipeline should be structured: the orchestrator's code needs to make a decision based on it (proceed? revise the plan?), and code should never be re-parsing prose to find out.

Concretely, for Project 1:

```
ValidationResult:
    passed: bool
    flags: list[str]          # e.g. ["single-window backtest", "IC reported without IR"]
    severity: Literal["none", "advisory", "blocking"]
```

The orchestrator reads `severity`. If `"blocking"`, that's exactly the kind of "an observation invalidates a downstream assumption" trigger from LA6 — the orchestrator revises its own plan (e.g., inserts a step to re-run the backtest across a longer window) rather than blindly proceeding to memo-writing. If `"none"` or `"advisory"`, the orchestrator continues to the memo-writing stage, passing the memo subagent the `FactorSpec`, the metrics, *and* the `ValidationResult` (so the memo can honestly disclose whatever advisory flags exist — directly serving the "own your methodology limitations" value already established in P1-L8's bias-disclosure pattern).

This is the answer to "how do results get merged back": **not** by dumping the subagent's full internal reasoning back into the orchestrator's context (that would recreate the bloat problem from Section 5), but by capturing only its **final, structured verdict**, which becomes one more Observation the orchestrator's own plan-tracking logic already knows how to handle.

---

## 7. Project 1's actual architecture, stage by stage

Putting Sections 3-6 together, here's the full mapping of the LA6 plan object onto "who executes this step" — the direct answer to "P1-LA7 is about who executes each stage of this plan," which was flagged as this lesson's framing back in the LA6 carried-forward notes.

| Plan step | Owner | Why |
|---|---|---|
| 1. Fetch price/universe/sector data | Orchestrator (via MCP tools, LA3) | Builder persona; needs full context of what's been fetched so far |
| 2. Compute raw factor + winsorize + sector-neutral z-score | Orchestrator | Same builder persona; depends directly on step 1's output in-context |
| 3. Portfolio construction (bucket, weight) | Orchestrator | Same reasoning |
| 4. Backtest (returns, turnover, costs) | Orchestrator | Same reasoning |
| 5. Compute metrics (IC, IR, Sharpe, etc.) | Orchestrator | Same reasoning |
| 6. Methodology validation | **Validator subagent** | Needs independence from the builder's reasoning (Section 5); different persona (skeptical reviewer, not builder) |
| 7. Write research memo | **Memo subagent** | Different persona (fluent explanatory writer); doesn't need the builder's blow-by-blow tool-call history, only final results + validator's verdict |

Stages 1-5 are one continuous orchestrator job precisely because none of the five decomposition signals from Section 4 apply between them — same persona, no independence concern, and each stage genuinely needs the previous one's output in its working context. Stages 6 and 7 get their own subagents because they clear multiple signals at once.

---

## 8. Failure modes preview (full depth deferred to P1-LA9 / P1-LA10)

Multi-agent orchestration introduces its own new ways to fail, which will get full treatment once you reach the failure-modes lessons, but worth naming now so you recognize them when they show up in your own build:

- **Accidental context leakage** — passing the validator subagent more than the compact structured handoff (e.g., including the orchestrator's reasoning trail "to be helpful") quietly defeats the entire independence rationale from Section 5.
- **Cost/latency multiplication** — every subagent call is a full separate LLM round-trip. Two sequential subagent calls (validator, then memo) add two full invocations' worth of latency on top of the orchestrator's own five stages; this is a real, additive cost, not free.
- **Subagent hallucination is now "invisible" to the orchestrator** — the orchestrator only sees the subagent's final structured result, not how it got there. If the validator subagent hallucinates a flag, the orchestrator has no ReAct trace to inspect and catch it against, unlike its own stages.

These get their full, dedicated treatment — detection strategies, retry/backoff, escalation — in P1-LA9 (reliability) and P1-LA10 (security/adversarial), alongside the tool-use and ReAct-specific failure modes already logged from earlier lessons.

---

## Summary of what's locked this lesson

- A **subagent** is a separate Claude conversation with its own system prompt and (usually much smaller) context window, invoked and returned to the orchestrator through the same mechanical shape as a tool call (LA2's 5-step cycle).
- **Orchestrator-worker** is the pattern: one agent owns the overall plan and dispatches bounded sub-tasks to specialized workers, staying in control of what happens with each result.
- Multi-agent orchestration is the "who executes each step" layer on top of LA6's "what's the sequence" planning layer — the plan object gains an `owner` field, nothing else changes structurally.
- **Decompose into a subagent when:** a different persona/stance is needed, independence from the producing agent's reasoning matters, context isolation avoids bloat, the task is a substantial enough unit of work to justify a full LLM round-trip, or the work is genuinely parallelizable. **Keep inside one agent when:** none of those apply and the steps are tightly sequential with a shared persona.
- Context isolation is not just a cost optimization — for the validator specifically, it is the mechanism that makes independent review meaningful at all (a subagent that inherited the builder's full reasoning trail could not credibly catch the builder's own mistakes).
- Results merge back as **structured objects** (per LA4), read by the orchestrator's own code to decide whether to proceed or trigger a plan revision (per LA6's revision-trigger logic).
- Project 1's architecture: orchestrator owns stages 1-5 (data fetch through metrics) via its own planning + ReAct loop; a **validator subagent** owns stage 6; a **memo subagent** owns stage 7.
