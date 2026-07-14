# P1-LA5: ReAct-Style Tool-Use Loops

**Completed:** 2026-07-14
**Track:** AI/Agentic (5/17)

## Where this picks up

Quick chain so this lesson slots in cleanly:

- **P1-LA1** gave the generic shape: perceive → reason → act → observe → repeat-or-stop (the agent loop).
- **P1-LA2** gave the mechanical version of one iteration of that loop: the five-step request/response cycle (send message+tools → model returns text or `tool_use` → application executes → application sends `tool_result` → model responds or loops again).
- **P1-LA3** showed MCP doesn't change any of that mechanics — it standardizes where tool definitions live (Step 0, discovery) and where execution happens (Step 3, now in a separate server process).
- **P1-LA4** covered how the loop's final output gets validated into a typed object (`FactorSpec`).

Still missing: LA1 said the model "reasons" at each turn, LA2 said the model returns either text or a `tool_use` block — but *how* does the model decide, and can that reasoning actually be seen, or is it a black box? That's what ReAct answers.

## Part 1: What ReAct actually is

**ReAct** stands for "Reason + Act." It names both a specific prompting technique and, more loosely, the pattern almost every modern tool-using agent follows — including the one built for Project 1.

The term comes from a 2022 research paper (Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models"). At the time, most language models had no built-in tool-calling API the way Claude does today — that came later. The paper's actual technique was a prompting trick: get the model to write its reasoning and its tool calls in the same block of plain text, alternating:

```
Thought: <the model explains what it's thinking>
Action: <the model writes which tool to call and with what input, as text>
Observation: <the actual tool result gets pasted back into the text>
Thought: <the model reacts to what it just observed>
Action: <next tool call>
Observation: <next result>
...
Thought: I now have enough information to answer.
Final Answer: <the answer>
```

This entire block was one long piece of text the model was writing and reading, with application code in the middle that noticed an "Action:" line, actually ran that tool, and spliced the real result in as "Observation:" before letting the model keep writing.

**Analogy:** think of a junior analyst told to "show their work" on a scratchpad while researching a client question, rather than just handing back a final answer. Every time they go check something (pull a filing, call someone, look up a number), they jot down *why* they're checking it, then *what* they found, before deciding what to check next. The reviewer can follow the entire train of thought, not just see the final memo.

### The core insight, stripped of the 2022-specific implementation detail

The specific text-scratchpad mechanics above are largely obsolete now — Claude's native tool-use API (P1-LA2) already handles "Action" and "Observation" structurally, via `tool_use` and `tool_result` blocks, instead of raw text parsing. But the core insight of the paper survived and is now baked into how good agents are built:

> Interleave visible reasoning with each individual action, rather than either (a) reasoning once at the start and then acting blindly, or (b) acting repeatedly with no visible reasoning at all.

This is the actual thing "ReAct-style" means in 2026: not necessarily the literal old text format, but the discipline of having the model state a short reasoning step before each tool call, so a human (or a validator subagent) can see *why* each action was taken, not just *what* was taken.

## Part 2: The three alternatives, compared

| Pattern | What it does | Can look up real facts? | Reasoning visible? | Main failure mode |
|---|---|---|---|---|
| **Reasoning-only (Chain-of-Thought / CoT)** | Model reasons step-by-step in text, but never calls a tool — answers entirely from what it already "knows" | No | Yes, fully | Hallucination — confident, well-reasoned-sounding answers built on made-up facts, because nothing was ever checked |
| **Acting-only** | Model calls tools repeatedly to gather information, but never explains why — just a sequence of tool calls | Yes | No | Opaque and brittle — if the sequence of calls goes wrong (wrong ticker, wrong date range), there's no visible reasoning trail showing why the model thought that was the right next step, making debugging much harder |
| **ReAct (Reason + Act)** | Model states a short reasoning step, takes one action, observes the real result, reasons again in light of what it just learned, and repeats | Yes | Yes | Still possible to fail, but failures are now diagnosable — you can point at the exact Thought that went wrong |

**Why this specific combination beats either alone** (the actual empirical finding in the 2022 paper, and it still holds): reasoning-only fails because the model never checks its assumptions against reality — it just makes up plausible-sounding facts and reasons from those. Acting-only fails less on hallucination (since it's actually looking things up) but is worse at adapting — without a visible reasoning step forcing the model to explicitly digest what it just observed, it's more likely to keep pursuing a plan that the latest observation just invalidated. Interleaving forces the model to explicitly "check in" with new information before deciding what's next.

## Part 3: Worked example — the momentum test, done ReAct-style

Same task as P1-LA1 ("test 12-month momentum on the NASDAQ-100"), now formatted explicitly as Thought → Action → Observation.

| Step | Type | Content |
|---|---|---|
| 1 | Thought | "To test 12-month momentum, I first need price history for every NASDAQ-100 stock, going back at least 13 months (12 months lookback plus 1 extra month to exclude, per the P1-L4/P1-L7 convention). I'll call the price-history tool." |
| 1 | Action | `get_price_history(universe="NASDAQ100", lookback_months=13)` |
| 1 | Observation | Tool returns price data for 97 of 100 tickers; 3 tickers (e.g., a stock that IPO'd 8 months ago) return an error: "insufficient history." |
| 2 | Thought | "3 tickers don't have enough history to compute a 12-month momentum factor. I wasn't told to handle this case explicitly, but computing momentum on partial history would be misleading — I should exclude these 3 from this run and note the exclusion, rather than crash or silently compute a wrong number." |
| 2 | Action | `compute_momentum(tickers=<97 valid tickers>, lookback_months=12, exclusion_months=1)` |
| 2 | Observation | Returns 97 raw momentum values. |
| 3 | Thought | "Per the locked P1-L4 pipeline, raw factor values need winsorization before z-scoring, not after. I'll winsorize first." |
| 3 | Action | `winsorize(values=<97 raw momentum values>, lower_pct=1, upper_pct=99)` |
| 3 | Observation | Returns 97 winsorized values. |
| 4 | Thought | "Now I need sector-neutral z-scoring, the default signal per P1-L4 — not universe-wide, since that would hide sector bets." |
| 4 | Action | `sector_neutral_zscore(values=<97 winsorized values>, sectors=<GICS sector map>)` |
| 4 | Observation | Returns 97 sector-neutral z-scores. |
| 5 | Thought | "I now have a complete, correctly-ordered signal for 97 of 100 stocks, with the 3 exclusions documented. This is enough to hand off to the next stage (portfolio construction). I'll stop here and report the result, flagging the 3 exclusions." |
| 5 | Final Answer | Signal computed for 97/100 tickers; 3 excluded for insufficient history (list attached); pipeline order followed per locked P1-L4 decision. |

**What to notice:** every single tool call (Action) has a Thought directly above it that names *why* that specific call, with that specific input, was the right next step — often citing a specific earlier lesson's locked decision (P1-L4's ordering, P1-L7's exclusion convention). That's the entire value of ReAct in one trace: every action is accompanied by a stated, checkable justification, rather than the model silently doing the right thing (or the wrong thing) with no visible trail.

## Part 4: Where ReAct earns its keep — error recovery

The momentum trace above went smoothly. ReAct's real advantage shows up when something goes wrong mid-loop.

**Scenario:** the user's request contains a typo — "test momentum on NASDQ-100" (missing the second A).

| Step | Type | Content |
|---|---|---|
| 1 | Thought | "The universe field says 'NASDQ-100', which isn't one of the two valid universe values (NASDAQ100, SP500) from the FactorSpec schema. This is very likely a typo for 'NASDAQ-100'. I'll proceed with that assumption rather than fail immediately, but I need to flag it." |
| 1 | Action | `get_universe_constituents(universe="NASDAQ100")` |
| 1 | Observation | Returns the 100 NASDAQ-100 tickers successfully. |
| 2 | Thought | "The corrected universe resolved successfully. I'll proceed with the rest of the pipeline, and I'll include a note in my final answer that I auto-corrected a likely typo, so the user can confirm that was the right call." |
| ... | | (rest of pipeline proceeds as before) |

**Why this matters, concretely:** without the visible Thought at Step 1, only "the model called `get_universe_constituents(universe="NASDAQ100")`" would be visible — with no way to tell whether that was because the model correctly auto-corrected a typo, or because it hallucinated a universe value that wasn't in the original request at all (a real failure mode from P1-LA2/P1-LA9). The Thought step is the only thing that distinguishes "reasonable inference, worth a human double-check" from "silent hallucination." This is exactly why P1-LA1's earlier "Reason vs. Perceive" distinction (Reason-step content is inference, never ground truth) matters here — a good ReAct trace should make it obvious, at every step, whether content came from inference or from an actual tool result.

## Part 5: A necessary nuance for 2026 — native tool use vs. explicit ReAct prompting

Worth being precise about, because this is the kind of nuance that separates "read a blog post about ReAct" from "actually understands how modern agent frameworks work" — directly relevant to AI PM conversations.

- **In 2022 (the ReAct paper's era):** no native tool-calling API. The entire Thought/Action/Observation structure had to be enforced through prompting alone — the developer's prompt literally instructed the model to write text in that exact three-part format, and the application had to parse the model's raw text output to find the "Action:" line and figure out what to execute. Fragile — the model might format things slightly wrong, breaking the parser.
- **Today, with Claude's native tool use (P1-LA2):** the "Action" part is a structured `tool_use` block, and "Observation" is a structured `tool_result` block, both handled by the API directly (no fragile text parsing needed). But the "Thought" part is **not automatically forced** by the API. By default, a model can go straight from receiving a message to emitting a `tool_use` block with no visible reasoning text at all — that would be the "Acting-only" pattern from Part 2's table, not ReAct.

Getting ReAct-style behavior out of a native-tool-use model in 2026 requires one of:

1. **Explicit system-prompt instruction:** tell the model, as part of its instructions, to always write a short reasoning statement in plain text before making each tool call — recreating the "Thought:" discipline on top of the native API, purely through prompting.
2. **Extended thinking / reasoning features:** some Claude configurations can be given a dedicated "thinking" space, separate from the final visible answer, where the model reasons before acting — a more structural version of the same idea, built into the model's output format rather than requested via prompt.

For Project 1, this is a genuinely open build-time decision (not resolved in this lesson — logged as carried-forward below): should P1-Build-7's orchestrator explicitly prompt for visible "Thought:" text before every tool call (cheap, simple, very readable in the tracing layer), or rely on a more structural reasoning mechanism? Either way, the goal is the same: make the orchestrator's reasoning visible and inspectable, not silently baked into an opaque decision to call a tool.

## Part 6: When is a single ReAct loop sufficient?

A single ReAct loop is **reactive** — at every step, it decides the next single action based only on what it currently knows (the original request plus everything observed so far). It does not commit to a multi-step plan in advance.

| Condition | Why a reactive ReAct loop is sufficient |
|---|---|
| The number of steps is small and roughly predictable | Not much to gain from planning ahead if the path is short anyway |
| Each step's outcome doesn't require coordinating far-ahead steps | E.g., "fetch data → compute factor → z-score" — each step just needs the previous step's output, not knowledge of step 5 while doing step 1 |
| Mid-course corrections are naturally local | If something unexpected happens (like the 3-ticker exclusion above), the fix only affects the very next step, not the whole downstream sequence |
| The task doesn't require weighing multiple possible overall strategies before starting | There's one clear path through the pipeline, not several competing approaches to choose between upfront |

A single reactive loop starts to strain when:

- The task genuinely benefits from mapping out several steps before executing any of them (e.g., "decide up front whether to test momentum, volatility, or both, and in what order, based on an estimate of which is more likely to be interesting given current market conditions").
- An early step's design depends on knowing what a much later step will need — planning backward from the goal, not just forward from the current state.
- The task might need to be revised mid-execution based on a change in strategy, not just a local correction.

This is exactly the boundary **P1-LA6 (Planning loops, next lesson)** will formalize. For now: P1-Build-7's orchestrator, as currently scoped, is mostly a ReAct-style reactive loop — the "test a factor" pipeline (fetch → compute → winsorize → z-score → bucket → backtest → metrics) is a fairly linear, predictable sequence where local error recovery (like the exclusion example) is enough. The planning layer, per the 2026-07-11 decision already locked in CONTEXT.md, comes in at the level of the orchestrator's overall delegation to the validator and memo subagents — a coarser, higher-level planning decision, not a fine-grained "figure out the whole tool-call sequence in advance" one.

## Part 7: How does the loop know when to stop?

Connects directly back to `stop_reason` from P1-LA2. In a ReAct-style loop, the termination condition is: the model, at some Thought step, judges that it now has enough information to answer, and instead of emitting another `tool_use` block, emits final text — recognized via `stop_reason: "end_turn"` (as opposed to `stop_reason: "tool_use"`, meaning "wait, I need another tool result first, keep looping").

In the explicit Thought/Action/Observation framing, this is the "Thought: I now have enough information to answer" step (Step 5 in the momentum example) — the model is explicitly reasoning about whether to keep going, not just mechanically producing another action. This self-assessment step is itself part of what makes ReAct different from a rigid, fixed-length loop: the number of iterations is not predetermined — it's decided by the model's own running assessment of task completion, exactly the "autonomy" property named in P1-LA1 (the LLM decides the sequence and length, not a human pre-script).

## Part 8: Direct tie-ins to Project 1

| Where | How this lesson applies |
|---|---|
| **P1-Build-7 (orchestrator)** | The tool-use sequence (fetch data → compute factor → winsorize → z-score → bucket → backtest → metrics) should be implemented as a ReAct-style loop: a short reasoning statement before each tool call, explaining why that call and those inputs were chosen — not a silent chain of tool calls with no visible justification. |
| **P1-Build-10 (tracing/observability layer)** | A good trace log is, in effect, a recorded ReAct transcript — Thought/Action/Observation triplets, in order, for a completed run. Direct conceptual prerequisite for what P1-LA12 (Observability & tracing) will build tooling around. |
| **P1-Build-8 (methodology validator subagent)** | The validator can inspect not just the orchestrator's final FactorSpec and results, but its reasoning trail — e.g., flagging a case where the Thought steps show the model reasoning past a known bias (like using today's sector classification for historical data, per P1-L8) without addressing it. |
| **P1-LA9 (agent failure modes, next-but-one)** | The "Reason vs. Perceive" distinction from P1-LA1, reinforced by this lesson's error-recovery example, is the direct tool for diagnosing hallucination: a Thought step asserting a specific, checkable fact with no corresponding Observation behind it is a hallucination red flag, visible only because the reasoning was made explicit in the first place. |

## Part 9 (follow-up): Mapping Thought/Action/Observation onto P1-LA1's agent loop

Precise correspondence between this lesson's vocabulary and P1-LA1's perceive-reason-act-observe loop:

- **Thought ↔ Reason.** Both are the LLM's generated inference — plausible, usually correct, but never ground truth. A Thought is just a Reason step made visible as text.
- **Action ↔ Act.** Identical — the tool call itself.
- **Observation ↔ Observe (the result of Perceive, applied to a real tool execution).** Both are real facts reported by an actual tool, not generated by the LLM.

Perceive and Observe are basically the same step in P1-LA1, just named for two different moments in the cycle: Perceive is "take in context at the start of a cycle," and Observe is "the tool result becomes new context right after Act." They're the same operation — taking in real information from outside — just labeled differently depending on whether the description is at the beginning or the end of one loop iteration.

**The concrete red flag this mapping produces:** if a "Thought" step asserts something that reads like a checkable, specific fact (e.g., "this ticker IPO'd 8 months ago") but there's no Observation immediately before it that actually supplied that fact — that Thought is functionally masquerading as an Observation. It looks like a grounded fact but is actually unverified inference. This is the concrete, inspectable version of the hallucination risk named at an intuition level back in P1-LA1's follow-up, now expressed as a specific pattern to look for in a real trace: **"Thought masquerading as Observation."**

## Summary table: the whole lesson in one place

| Concept | One-line definition |
|---|---|
| ReAct | "Reason + Act" — interleaving a stated reasoning step before every tool call, rather than reasoning once upfront or acting silently |
| Thought / Action / Observation | The three-part repeating unit of a ReAct trace: why (Thought) → what (Action) → what happened (Observation) |
| Reasoning-only (CoT) | Reasons in text but never checks facts against reality — high hallucination risk |
| Acting-only | Calls tools repeatedly with no visible justification — hard to debug, harder to catch bad reasoning |
| ReAct's advantage | Combines fact-checking (via tools) with visible, checkable justification (via reasoning) for every single action |
| Native tool use vs. classic ReAct prompting | Modern APIs (like Claude's) structurally handle Action/Observation already; visible Thought text must still be explicitly requested (system prompt or reasoning features) if wanted |
| When one reactive loop is sufficient | Short, roughly linear pipelines where corrections are local — as opposed to needing an upfront multi-step plan (P1-LA6) |
| Loop termination | The model itself judges "I have enough information," emitting final text instead of another tool call — surfaced via `stop_reason: "end_turn"` |
| Thought masquerading as Observation | A Thought stating a specific, checkable fact with no corresponding real tool Observation behind it — the concrete, inspectable hallucination red flag |
| Thought ↔ Reason, Observation ↔ Perceive/Observe | Thought is generated inference (never ground truth on its own); Observation is real, externally-verified fact reported by an actual tool execution |

## No new locked pipeline design decisions this lesson

Mechanics/vocabulary lesson. One open item surfaced (see below).

## Carried-forward action items

- **(P1-LA5) → P1-Build-7 (orchestrator):** Implement the tool-use sequence as a ReAct-style loop — require a short visible reasoning statement before every tool call, not a silent chain of tool calls.
- **(P1-LA5) → P1-Build-7 (open question):** Mechanism for producing visible reasoning — explicit "Thought:" system-prompt instruction vs. the API's `thinking`/adaptive-thinking parameter (with interleaved tool-call reasoning). Not resolved; re-verify current API docs at build time before deciding, since thinking-mode mechanics have changed across recent model versions.
- **(P1-LA5) → P1-Build-10 (tracing/observability layer):** Design the trace log format around Thought/Action/Observation triplets — this lesson is the direct conceptual prerequisite for P1-LA12's tracing tooling.
- **(P1-LA5) → P1-Build-8 (methodology validator subagent):** Validator should be able to inspect the orchestrator's reasoning trail (not just final output), flagging cases where a Thought reasons past a known bias (e.g., P1-L8's sector-reclassification look-ahead issue) without addressing it.
- **(P1-LA5, follow-up) → P1-LA9 / P1-LA12:** Use the "Thought masquerading as Observation" pattern (a Thought asserting a specific checkable fact with no backing tool Observation) as a concrete, inspectable hallucination-detection heuristic in both the failure-modes treatment (P1-LA9) and the tracing/observability practice (P1-LA12).
