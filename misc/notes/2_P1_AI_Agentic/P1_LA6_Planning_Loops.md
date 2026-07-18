# P1-LA6: Planning Loops

## 1. The question this lesson answers

Every lesson in this track so far has been building toward one recurring question: **who decides what happens next, and how far ahead do they decide it?**

- P1-LA1 established the agent loop (perceive → reason → act → observe) and the autonomy spectrum.
- P1-LA5 gave you ReAct ("Reason + Act"): reason *immediately before* every single action, one step at a time, with no visible commitment beyond the next step.

This lesson introduces the next rung up: **what happens when reasoning one step at a time isn't enough — when the agent needs to know where it's going before it takes the first step?**

That's a **planning loop**: a loop in which the agent produces an explicit, multi-step plan up front, executes that plan (possibly using ReAct-style reasoning within each step), and revises the plan itself if something it observes along the way contradicts an assumption the plan was built on.

## 2. The analogy: reactive trader vs. portfolio manager with a thesis

You already have the mental model for this from your trading background, even if you haven't named it this way.

| | Reactive trader | Portfolio manager with a quarterly thesis |
|---|---|---|
| **Decision horizon** | One tick, one order at a time | A multi-week plan: build position, monitor catalysts, exit on thesis completion or invalidation |
| **What triggers the next decision** | Whatever the market just did | The plan itself — the next scheduled step, unless something breaks an assumption |
| **What happens when something unexpected occurs** | React to it directly, in isolation | Ask: does this invalidate part of my thesis? If yes, revise the thesis. If no, keep executing the plan |
| **Failure mode** | Loses the forest for the trees — no thesis, so decisions can drift or contradict each other over time | Sticks to a stale thesis too long after it's been invalidated (sunk-cost) |

ReAct-style tool use (P1-LA5) is the reactive trader: reason, act, observe, reason again — every decision made fresh, informed only by what just happened. There's no persistent record of "here's my overall plan and here's how far through it I am."

A planning loop is the portfolio manager: form an explicit thesis (the plan) before acting, execute against it, and only revisit the thesis itself when something observed genuinely contradicts an assumption it was built on — not every single time something happens.

Neither is "better" in the abstract. Which one you need depends on the shape of the task, which is exactly what this lesson exists to teach: when an agent needs to plan ahead vs. react turn-by-turn.

### 2a. A second analogy: Scrum sprint board vs. Kanban board

This maps just as cleanly onto a second pair you already know from working with engineering teams, and it's worth holding both analogies side by side because each sharpens a slightly different part of the concept.

| | Kanban board | Scrum sprint board |
|---|---|---|
| **What exists before work starts** | A prioritized backlog, but no committed batch — work is pulled one card at a time as capacity frees up | A sprint backlog: an explicit, decomposed, ordered set of committed work items, fixed at sprint planning before any work starts |
| **What triggers picking up the next unit of work** | Whatever the highest-priority card is *right now*, decided at the moment a slot opens | The sprint plan itself — the next committed item, unless the sprint plan is formally revised |
| **What happens when priorities shift mid-stream** | The backlog is simply reordered; the next card pulled reflects the new priority — no separate "process" for this | A scope change requires a deliberate conversation (typically with the product owner) — you don't silently swap sprint commitments; you explicitly revise the sprint plan |
| **Failure mode** | Can thrash if priorities change constantly, since there's no stable batch to point to and say "this is what we're doing this cycle" | Can commit to a sprint plan that becomes stale mid-sprint if the team pushes through the original plan despite a signal that should have triggered a scope conversation |

The precise mapping: **Kanban is ReAct** — there's still a prioritization judgment before each pull (exactly like a Thought before each Action), but no persistent, committed plan spanning multiple units of work, and no formal process for revising one. **Scrum's sprint backlog is the plan artifact** from Section 3 — a committed, decomposed batch, formed before execution, that can only be changed through an explicit revision step rather than an ad hoc swap. That last point is the sharpest part of the analogy: Scrum's rule that a mid-sprint scope change needs a real conversation, not a silent substitution, is structurally identical to Section 8's plan-revision trigger condition below — you don't quietly re-decide the plan on every small surprise; you explicitly flag that an assumption broke and revise the plan on purpose.

One place the analogy needs a small correction, since it's worth being precise rather than just reaching for the tidiest comparison: Kanban isn't "zero planning" any more than ReAct is "zero reasoning" — there's still a backlog and still a prioritization judgment behind every pull. The actual distinction in both pairs is the same one: **is there a committed, decomposed batch that persists across multiple units of work and requires a deliberate step to change (plan / sprint backlog), or is each next unit decided fresh with no such persistent, revisable batch (ReAct / Kanban pull)?**

## 3. Defining "planning loop" precisely

**Planning loop**: an agent loop where the model first produces an explicit decomposition of the overall goal into an ordered (or partially ordered) sequence of sub-steps — the **plan** — before executing any of them, then works through that plan step by step, and has a mechanism to revise the plan itself if an observation invalidates one of the plan's assumptions.

Break that down into its four moving parts:

| Term | What it means | Contrast with ReAct |
|---|---|---|
| **Plan** | An explicit, inspectable decomposition of the goal into ordered sub-goals, produced *before* any tool call happens | ReAct has no equivalent artifact — there's a Thought before each action, but no upfront statement of the whole sequence |
| **Task decomposition** | The act of breaking one large, underspecified goal ("build and validate a value factor") into smaller, well-defined sub-goals ("fetch fundamentals," "compute the ratio," "winsorize," ...) | ReAct decomposes implicitly and locally — one step ahead only, re-decided every iteration |
| **Plan execution** | Working through the plan's steps in order; each step can itself be a small ReAct-style loop (reason → act → observe) if it involves tool calls | This is where ReAct and planning loops nest — planning doesn't replace ReAct, it wraps around it |
| **Plan revision (replanning)** | Updating the plan itself — not just the next action — when an observation contradicts an assumption the plan depended on | ReAct has no equivalent concept, because it never had a persistent plan to revise in the first place |

The most important thing to internalize: **a planning loop is not "ReAct, but with more steps."** It's a different loop *shape* — it has a persistent artifact (the plan) that acts as working memory across the whole task, which ReAct never had.

## 4. Why plan at all? The problem planning solves

Think about why a portfolio manager writes down a thesis instead of just reacting to each day's news in isolation. It's not because reacting is inherently wrong — it's because for a multi-week position, purely reactive decision-making has three specific failure modes:

1. **Losing track of the overarching goal.** Ten reactive decisions in a row, each locally sensible, can add up to something that no longer serves the original objective — because nothing is checking each decision against the whole.
2. **Redoing or skipping work.** Without a checklist of what's been done and what's left, a purely reactive process can repeat a step it already did, or skip one it needed.
3. **Being unable to explain the sequence.** If someone asks "why did you do these five things in this order," a reactive process's honest answer is "because that's what seemed right at each moment" — there's no upfront rationale to point to.

A planning loop solves all three by giving the agent (and you, reading its trace) an explicit checklist it can compare its own progress against, and a stated rationale for the ordering.

This maps directly onto why Project 1's orchestrator (P1-Build-7) needs to be a planning loop and not just a longer ReAct loop. "Build and validate a value factor" is not one tool call or even five tightly coupled ones — it's a multi-stage pipeline (data → signal construction → portfolio construction → backtest → validation → memo) where later stages depend on earlier ones being done correctly, and where you (the reader of the trace, or an interviewer) will want to see the stated plan, not just infer it from a long list of tool calls after the fact.

## 5. When ReAct alone is enough, and when you need a planning loop

This is the actual decision this lesson exists to teach. Here's the criterion, and then a table applying it.

**The criterion:** ask whether the task has *few, tightly-coupled steps where each decision only depends on the immediately preceding result* (ReAct is enough), or *many steps with dependencies that span across steps, where getting the overall sequence right matters as much as getting each individual step right* (you need a plan).

| Task characteristic | ReAct-style loop sufficient | Planning loop needed |
|---|---|---|
| Number of steps | Few (1-4) | Many (5+), often with sub-stages |
| Dependency structure | Each step depends only on the step immediately before it | Later steps depend on decisions made several steps earlier (e.g., which factor type was chosen back at step 1 determines what "significance test" means at step 7) |
| Need to explain the sequence upfront | Low — the trace itself is the explanation | High — a stakeholder (or validator subagent) wants to see the intended sequence *before* execution, not just infer it after the fact |
| Risk of a step invalidating an earlier assumption | Low | Real — e.g., discovering 3 tickers lack sufficient history partway through changes what "the universe" means for every downstream step |
| Example from Project 1 | "What was AAPL's average price in the first week of June 2026?" (P1-LA2's worked example — one lookup, format, answer) | "Build a 12-month momentum factor, test it on the NASDAQ-100, and tell me if it's statistically significant" (the full P1 pipeline) |

Notice the second row especially: this is the concrete criterion, not just a vibe. If a mistake or surprise three steps ago should change what you do five steps from now, you need a persistent plan to check that later step's assumptions against. ReAct's one-step-ahead reasoning has literally nowhere to store "the universe changed" once it's five iterations in the past.

## 6. Worked example: the same task, two ways

Let's reuse the task from P1-LA1 and P1-LA5 — "test 12-month momentum on the NASDAQ-100" — and this time extend it to the fuller version that actually matches what P1's orchestrator needs to do: **"Build a 12-month price momentum factor, test it on the NASDAQ-100, and tell me if it's statistically significant."**

### 6a. ReAct-style trace (no upfront plan)

| Iteration | Thought | Action | Observation |
|---|---|---|---|
| 1 | "I need price history for the universe first" | `get_price_history(NASDAQ-100, 13mo)` | Data returned; 3 tickers have <13 months of history |
| 2 | "Those 3 tickers can't compute a 12-month return; I'll exclude them" | (no tool call — internal decision) | 97 tickers remain |
| 3 | "Now compute 12-month log returns for the 97 tickers" | (calculation) | Raw factor values produced |
| 4 | "Winsorize before z-scoring, per P1-L4's locked order" | (calculation) | Extreme values capped at 1st/99th percentile |
| 5 | "Apply sector-neutral z-scoring" | (calculation) | Sector-neutral z-scores produced |
| 6 | "Bucket into quintiles, construct long-short" | (calculation) | Long-short portfolio returns produced |
| 7 | "Compute rank Information Coefficient (IC) and a significance test" | (calculation) | IC = 0.04, t-stat significant |

This works — for this specific task, run once, with nothing going wrong beyond the one hiccup at iteration 1. But notice: **there is no artifact anywhere in this trace that states "here is the full sequence I intend to follow."** Each Thought only ever looks one step ahead. If you asked the agent at iteration 2 "what's your step 6 going to be," it has no answer — it hasn't decided yet.

### 6b. Planning-loop trace (plan formed up front, then executed)

**Step 0 — Plan formation (before any tool call):**

```
Plan for: "12-month momentum factor, NASDAQ-100, test significance"
1. Fetch 13 months of price history for NASDAQ-100 constituents
2. Compute 12-month log returns per ticker; exclude any ticker with insufficient history
3. Winsorize raw factor at 1st/99th percentile
4. Apply sector-neutral z-scoring
5. Bucket into quintiles; construct long-short equal-weighted portfolio
6. Compute rank IC and time-series t-statistic across the backtest window
7. Report result with significance assessment
```

**Execution against the plan:**

| Plan step | Executed as | Result | Plan status after this step |
|---|---|---|---|
| 1 | `get_price_history(...)` (ReAct-style: one Thought, one Action, one Observation) | Data returned; 3 tickers have <13 months of history | **Assumption violated** — step 2 assumed a clean 100-ticker universe. Triggers a plan revision, not just a local fix. |
| — revision — | "Original plan assumed a clean universe of 100. Revising: insert an explicit exclusion sub-step, and note the effective universe is 97 for all downstream steps." | Plan step 2 rewritten in place | Plan updated; steps 3-7 unchanged in substance but now explicitly operate on "97 tickers," not "the universe" |
| 2 (revised) | Compute returns for 97 tickers | Raw factor values produced | On track |
| 3 | Winsorize | Capped values | On track |
| 4 | Sector-neutral z-score | Z-scores produced | On track |
| 5 | Quintile bucket, long-short construction | Portfolio returns produced | On track |
| 6 | Rank IC + t-stat | IC = 0.04, significant | On track |
| 7 | Report | Final answer, referencing the mid-plan revision | Plan complete |

The mechanics of *executing* step 1 are identical to the ReAct trace — same tool call, same Thought-Action-Observation shape. **The difference is entirely in step 0 and the revision row**: there's a persistent plan artifact that step 1's surprising result gets checked against, and the reaction to the surprise is explicitly framed as "this invalidates an assumption in the plan," not just "here's what I'll do differently right now." That framing is what makes it inspectable later — you (or a validator subagent) can look at the plan object and see exactly what was assumed, what broke, and what changed.

For this particular example, both approaches land at the same final answer, because the surprise was minor and locally recoverable. The value of planning shows up more clearly on harder cases — e.g., if step 4's sector-neutral z-scoring later revealed that one whole GICS (Global Industry Classification Standard) sector was massively over-represented in the excluded tickers, a ReAct loop would have no record of "the universe changed at step 1" to connect that observation back to; a planning loop's plan object carries that history forward explicitly.

## 7. How a plan is actually represented

In practice, "the plan" isn't a mysterious internal state — it's usually just a structured object (a numbered list, or JSON — JavaScript Object Notation — exactly like the structured outputs from P1-LA4) that the orchestrator produces via one model call, then reads back at every subsequent iteration to know what's next and what's already done.

A minimal representation, applied to the example above:

```json
{
  "goal": "Build and test 12-month momentum factor on NASDAQ-100",
  "steps": [
    {"id": 1, "description": "Fetch 13mo price history", "status": "done", "note": "3 tickers excluded — insufficient history"},
    {"id": 2, "description": "Compute 12-month log returns for 97 tickers", "status": "done"},
    {"id": 3, "description": "Winsorize at 1st/99th percentile", "status": "done"},
    {"id": 4, "description": "Sector-neutral z-score", "status": "pending"},
    {"id": 5, "description": "Quintile bucket, long-short construction", "status": "pending"},
    {"id": 6, "description": "Compute rank IC + t-stat", "status": "pending"},
    {"id": 7, "description": "Report result", "status": "pending"}
  ]
}
```

This is the same core idea as P1-LA4's `FactorSpec` — a typed, inspectable object — just applied to the *sequence of work* instead of the *input parameters*. That's a useful thing to notice: structured outputs (LA4) aren't only for parsing a final answer; they're also how a plan gets represented so it can be checked and revised programmatically rather than living only as loose text in a conversation.

## 8. Plan revision: what actually triggers it

Not every surprising observation should trigger a full replan — that would just turn a planning loop into an expensive, jumpy ReAct loop with extra overhead. The useful trigger condition is specific:

**Replan when an observation contradicts an assumption a later, not-yet-executed step in the plan depends on.** If the surprise only affects the step currently executing and nothing downstream, it's a local adjustment, not a plan revision.

| Observation | Does it violate a downstream assumption? | Local fix or plan revision? |
|---|---|---|
| 3 tickers lack sufficient history (affects "the universe" used by every step from 2 onward) | Yes — steps 2-7 all implicitly assumed "the 100-ticker universe" | **Plan revision** |
| One API call for price data times out and needs a retry | No — retrying doesn't change what any other step assumes | **Local fix** (handled within that step's own mini-ReAct loop, no plan change) |
| Sector classification data is missing for 2 of the 97 tickers, discovered at step 4 | Yes — step 4 (sector-neutral z-score) and step 5 (bucketing) both depend on having a sector label for every remaining ticker | **Plan revision** |
| A single day's price observation looks like an outlier but doesn't change the count of usable tickers | No | **Local fix** (winsorization at step 3 already exists to handle exactly this) |

This is a genuinely useful filter to apply when you're later reading a trace and deciding whether the orchestrator behaved sensibly: **did it replan when it should have, and did it avoid replanning when it shouldn't have?** Over-replanning (revising the whole plan on every minor hiccup) is its own failure mode — you lose the entire benefit of having a stable plan if it's rewritten every iteration.

### 8a. Follow-up: who actually triggers the check — the model, or the developer?

This is a mechanics question worth being precise about, because it isn't obvious from the outside and it directly shapes how P1-Build-7 gets built.

**The judgment ("does this observation conflict with the plan?") is the model's. The mechanism that forces that judgment to happen at all is the developer's.** Nothing about a planning loop as an architecture makes the model spontaneously notice a conflict — the model only checks the plan against a new observation if the application code puts both the plan and the new observation in front of it and explicitly asks it to check. This is the exact same nuance already locked in P1-LA5 for ReAct's visible Thought: the API doesn't force reasoning text to appear; a system-prompt instruction (or the `thinking` parameter) does. Plan-conflict checking has the identical shape — it is prompted behavior, not a free structural guarantee.

**The concrete mechanism, step by step:**

| Step | Who is responsible | What it involves |
|---|---|---|
| 1. Execute the current plan step (tool call) | Model decides the tool call; application code executes it | Ordinary ReAct-style iteration |
| 2. Get the Observation back | Application code | Runs the real function, returns the real result |
| 3. Feed the model the plan object + the new Observation, and explicitly ask it to check for a conflict | **Application code decides that this check happens, and when**; the model does the actual checking | The step that does not exist for free — requires a turn structured like: "here is the current plan; here is what step N just returned; does this contradict any assumption steps N+1 onward depend on?" |
| 4. Model answers "no conflict, proceed" or "conflict — here is the revised plan" | Model | A judgment call, same category as any other LLM reasoning — plausible, not infallible |
| 5. Parse that answer and either continue or overwrite the plan object | Application code | A structured-output problem (P1-LA4) — the model's answer should come back as a parseable object (e.g., `{"conflict": bool, "revised_plan": [...] or null}`), not free text to be guessed at |

The takeaway: **the model supplies the judgment, the developer supplies the checkpoint.** If the checkpoint (step 3) is never built into the loop, the model will keep executing the original plan indefinitely, because nothing ever asked it to reconsider — this is precisely how the "stale plan" failure mode from Section 10 actually happens in practice: a scaffolding gap, not a model limitation.

**The real design choice this creates — when should step 3 fire:**

| Approach | Mechanism | Tradeoff |
|---|---|---|
| **Check after every step** | Every Observation is run through the conflict-check prompt before moving to the next plan step | Never misses a conflict, but adds a model call and latency/cost to every single iteration, even when nothing unusual happened |
| **Code-triggered scrutiny** | Application code applies a cheap, deterministic heuristic first (e.g., did a count come back different than expected, did an API return an error, did a value fall outside a sane range) and only invokes the full conflict-check prompt when the heuristic fires | Cheaper, but only as good as the heuristics — a conflict the code didn't think to check for can slip through silently |

Tying back to the Kanban/Scrum analogy from Section 2a: "check after every step" is the daily-standup discipline — a structural checkpoint on a fixed cadence, regardless of whether anything looks obviously wrong. "Code-triggered scrutiny" is closer to only calling an ad hoc meeting when something is visibly on fire — legitimate, but it fails silently rather than loudly when the heuristics miss something. Neither is free, and which one P1-Build-7 uses is a genuine build-time decision, not something resolved by this lesson.

## 9. Where this fits in Project 1's architecture

This lesson is the direct conceptual prerequisite for two build sprints down the line:

- **P1-Build-7 (the orchestrator):** this is where the planning loop actually gets implemented. The orchestrator will form a plan from the validated `FactorSpec` (P1-LA4), execute each stage — data fetch, signal construction, portfolio construction, backtest, evaluation — using ReAct-style reasoning within each stage (P1-LA5), and revise the plan if a stage surfaces something that breaks a downstream assumption (like the ticker-exclusion example above).
- **P1-LA7 (subagents & multi-agent orchestration, next lesson):** once you have an explicit plan with discrete stages, the natural next question is "does one agent have to execute every stage itself, or can distinct stages be delegated to separate specialized agents?" That's exactly what P1-LA7 covers — the plan you build here becomes the thing that gets *decomposed across agents* in the next lesson, rather than executed by a single agent end to end. Planning and multi-agent orchestration are closely related but distinct: planning is about *sequencing* work; multi-agent orchestration is about *who* does each piece of the sequence.

## 10. A preview of failure modes (full depth later)

Planning loops introduce failure modes that pure ReAct loops don't have, because now there's a persistent artifact that can itself go wrong:

- **Stale plan / sunk-cost commitment:** continuing to execute a plan after an observation should have triggered a revision, because nothing forced the check. This is the direct agentic-systems analogue of a portfolio manager riding a thesis long after the facts have changed underneath it.
- **Over-replanning:** revising the plan on every minor observation, which erodes the entire benefit of having a stable plan and starts to resemble a slow, expensive version of ReAct.
- **Plan-execution mismatch:** the plan says one thing but the executed steps quietly diverge from it, with no reconciliation — the plan becomes decorative rather than load-bearing.

These get full treatment in **P1-LA9 (agent failure modes — reliability)**, where they'll sit alongside the tool-use failure modes from P1-LA2 and the ReAct-specific "Thought masquerading as Observation" pattern from P1-LA5. For now, just hold onto the fact that a plan is only useful if it's actually checked against — a plan nobody consults again after forming it provides zero benefit over having no plan at all.

## 11. Terminology recap

*(Both analogies from Section 2 — reactive trader vs. portfolio manager, and Kanban vs. Scrum — collapse to the same underlying test: is there a committed, decomposed batch that persists and requires a deliberate step to revise, or is each next unit decided fresh with nothing persistent to revise?)*


| Term | Definition |
|---|---|
| **Planning loop** | An agent loop where an explicit multi-step plan is formed before execution begins, executed step by step, and revised if an observation invalidates a downstream assumption |
| **Plan** | An explicit, inspectable, ordered decomposition of a goal into sub-steps — a persistent artifact, not just a one-step-ahead intention |
| **Task decomposition** | Breaking one large, underspecified goal into smaller, well-defined sub-goals |
| **Plan execution** | Working through the plan's steps in order; each step may itself be a small ReAct-style loop |
| **Plan revision / replanning** | Updating the plan itself (not just the current action) when an observation contradicts an assumption a downstream step depends on |
| **Stale plan** | Continuing to execute a plan after it should have been revised |
| **Over-replanning** | Revising the plan on every minor observation, eroding the benefit of having a stable plan |

## 12. No new locked design decisions this lesson

This is a conceptual-foundations lesson (definitions and mental models for planning vs. reactive execution), not a pipeline design choice. The concrete implementation choice — exactly how P1-Build-7's orchestrator represents and stores its plan object, and what triggers a replan check in code — is deferred to P1-Build-7 itself, informed by this lesson's plan-representation example (Section 7) and revision criterion (Section 8).
