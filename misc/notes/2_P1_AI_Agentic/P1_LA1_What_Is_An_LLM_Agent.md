# P1-LA1: What is an LLM Agent

**Track:** AI/Agentic (lesson 1 of 17)
**Completed:** 2026-07-14
**Estimated time:** 1 hour

First lesson of the AI/Agentic track. This is a foundational lesson — everything else in this track (tool use, MCP, ReAct loops, planning loops, subagents, governance) is a refinement of the ideas here.

---

## 1. The core question: what makes something an "agent"?

You've used ChatGPT or Claude in a chat window. You type a question, it answers. That's useful, but it's not what people mean when they say "AI agent" in a 2026 job posting or hiring conversation.

**Plain-language definition:** An **LLM agent** is a system where a Large Language Model (LLM) doesn't just generate text — it can *look at its surroundings, decide what to do next, take an action that changes something in the world (or fetches new information), see what happened, and decide again.* It repeats this cycle until it's done, and *it* is the one deciding what "done" looks like and how to get there — not a human-written script deciding for it.

The best analogy from your world: think about the difference between three ways you could delegate a piece of research to someone on your team.

| Delegation style | Analogy |
|---|---|
| **Fixed workflow** | You hand a junior analyst a rigid checklist: "Step 1: pull this exact spreadsheet. Step 2: filter these exact rows. Step 3: paste into this exact template." They execute the steps in order, no matter what they find along the way. If step 2 turns up something weird, they don't deviate — the checklist doesn't have a branch for that. |
| **Chatbot** | You ask a colleague a question over Slack: "What's a reasonable way to think about momentum factors?" They type back a thoughtful answer. They don't go pull any data, don't touch any system, don't come back later with results. The interaction starts and ends with words. |
| **Agent** | You tell a capable junior analyst: "Go figure out whether 12-month momentum works on the NASDAQ-100." They decide for themselves what data to pull, notice if something looks off and go investigate it, adjust their approach based on what they find, and come back once *they've* decided the task is actually done. You gave them a goal, not a script. |

That third one — someone who perceives the situation, reasons about it, takes an action, observes the result, and decides what to do next based on that result — is what an LLM agent is, except the "someone" is an LLM with tools instead of a person.

---

## 2. Fixed workflow vs. chatbot vs. agent — the full comparison

This distinction matters a lot for interviews, because people misuse the word "agent" constantly (marketing teams love slapping "agentic" on anything with an API call). You need to be able to say precisely what makes something agentic and what doesn't.

| Dimension | Fixed Workflow | Chatbot | LLM Agent |
|---|---|---|---|
| **Who decides what happens next?** | A human, in advance, written into code (if/else, fixed pipeline order) | The LLM decides *what to say*, but not *what to do* — there's nothing to do, only something to answer | The LLM decides *what action to take next*, in real time, based on what it just observed |
| **Does it touch the outside world?** | Yes, but only in the pre-programmed way | No — text in, text out | Yes — it can call tools, fetch data, write files, hit APIs, and the *sequence* of these is not fixed in advance |
| **Can it adapt mid-task if something unexpected happens?** | No — an unexpected input either breaks it or falls through a default branch a human anticipated | N/A — there's no multi-step task to adapt within | Yes — this is the defining feature. If a tool call returns something unexpected, the agent reasons about it and picks a different next step |
| **How many decision points does the LLM control?** | Zero (a human made all decisions when writing the code) | One (single response) | Many (one per iteration of the loop, until it decides it's done) |
| **Example in your world** | A nightly batch job that always: pulls prices → computes returns → writes to a fixed report format | Asking Claude "explain the Sharpe ratio" in a chat window | An agent that takes "test momentum on the NASDAQ-100," decides it needs price data, calls a tool to get it, notices three tickers have missing data, decides to investigate why, then proceeds with a cleaned dataset, then decides which statistical tests to run based on what it found |

**The one-sentence version you should be able to say in an interview:** *"A fixed workflow has a human deciding the sequence of steps in advance; a chatbot has an LLM deciding only what to say; an agent has an LLM deciding what to do — including which tools to use and in what order — based on what it observes as it goes."*

---

## 3. The perceive → reason → act loop

This is the mechanical heart of every agent, from the simplest single-tool-use loop (P1-LA5, coming soon) all the way up to a multi-agent orchestration system (P1-LA7, later, which is literally what Project 1's architecture will be).

**Plain-language intuition first.** Think about how you actually do open-ended investigative work — not a checklist task, but something like "figure out why portfolio manager complaints about the IBOR platform spiked last quarter." You don't have a fixed script. You do something more like:

1. **Perceive** — look at what's currently in front of you (the complaint tickets, whatever data exists)
2. **Reason** — think about what that data suggests and what you'd need to know next to test a hypothesis
3. **Act** — go do something to get that next piece of information (pull a report, ask a stakeholder a question, look at a system log)
4. **Observe** — see what came back
5. Loop back to **Reason** with this new information, and keep going until you're confident you understand the problem

That cycle — perceive, reason, act, observe, repeat — is exactly what an LLM agent does mechanically, just automated. Here's the formal breakdown of each step:

| Loop stage | What it means for an LLM agent | Plain-language equivalent |
|---|---|---|
| **Perceive** | The agent receives its current context: the original goal, conversation history, and results of any tool calls made so far | "Here's everything I know right now" |
| **Reason** | The LLM generates a thought about what should happen next, given everything it perceives — this is just the LLM "thinking out loud" internally (or sometimes visibly, depending on system design) | "Given what I know, what's the next useful thing to do?" |
| **Act** | The LLM chooses and executes an action — most commonly, calling a tool (a function, API, or data source) with specific arguments | "I'm going to call `get_price_data(ticker='AAPL', start='2024-01-01')`" |
| **Observe** | The result of that action (the tool's output) gets added back into what the agent perceives on the next loop | "The tool came back with 250 rows of price data, and three of them are NaN" |
| **Repeat or Stop** | The agent decides — again, itself, not a human script — whether the goal is met or whether another perceive→reason→act cycle is needed | "I now have what I need to compute the momentum signal, so I'll stop looping and produce the final answer" — OR — "The data has gaps, I need to investigate before proceeding" |

You may also hear this called the **agent loop**, the **ReAct loop** (short for "Reason + Act," a specific technique/paper name covered in depth in P1-LA5), or — if you've ever touched military/systems-engineering vocabulary — it's a close cousin of the **OODA loop** (Observe, Orient, Decide, Act), a decision-making framework originally developed for fighter pilots. Different fields invented very similar loop structures independently because it's a fairly fundamental pattern for "how does an intelligent actor operate in an environment it doesn't fully control or know in advance."

**Important nuance:** the loop doesn't have to be long. A single perceive→reason→act→observe cycle that terminates immediately (one tool call, done) is *technically* agentic behavior — it's the same mechanism as a 20-step loop, just a short one. What makes something "more" or "less" agentic isn't the loop length, it's whether the *LLM* is the one deciding the sequence versus a human having pre-decided it.

---

## 4. Worked example: the same task, three ways

Let's ground all three system types (fixed workflow, chatbot, agent) in a task that's directly relevant to Project 1: **"Test whether 12-month momentum works on the NASDAQ-100."**

### 4a. Fixed workflow version

A human (you) writes code that always executes this exact sequence, no matter what:

| Step | Hardcoded action |
|---|---|
| 1 | Pull adjusted close prices for all 100 NASDAQ-100 tickers, fixed date range |
| 2 | Compute 12-month-minus-1-month momentum for every ticker, no exceptions |
| 3 | Winsorize and sector-neutral z-score, using fixed parameters |
| 4 | Bucket into quintiles, fixed bucket count |
| 5 | Compute rank IC, fixed forward-return window |
| 6 | Write results to a fixed-format report |

If step 1 discovers that 3 tickers have completely missing data, the code either crashes, silently drops them (because a human anticipated that and wrote a `dropna()`), or does something else a human decided in advance. **The system itself never "decides" anything — every branch was pre-written.**

### 4b. Chatbot version

You type into a chat window: *"What would you expect if I tested 12-month momentum on the NASDAQ-100?"*

The LLM responds with a well-reasoned answer based on its training knowledge — probably something like "momentum has historically shown positive but inconsistent Information Coefficients in the 0.02-0.05 range, expect decay after 1-3 months, watch for sector concentration in tech given the NASDAQ-100's composition..." **This can be a genuinely good, useful answer.** But nothing happened in the world. No data was pulled. No test was actually run. The chatbot cannot verify or execute anything — it can only reason from what it already knows and say so.

### 4c. Agent version

You give the LLM agent access to tools (`get_price_data`, `compute_momentum`, `winsorize`, `zscore_by_sector`, `compute_rank_ic`, etc. — these are exactly the tools the MCP server in P1-Build-1 will eventually expose) and the same instruction: *"Test whether 12-month momentum works on the NASDAQ-100."*

Here's what a trace of the agent's loop might actually look like:

| Loop iteration | Perceive | Reason | Act |
|---|---|---|---|
| 1 | Goal: test momentum on NASDAQ-100. No data yet. | "I need price data before I can compute anything." | Call `get_price_data(universe='nasdaq100', lookback='13mo')` |
| 2 | Tool result: 100 tickers returned, but 3 have gaps in the data | "Some tickers have missing data — I should check why before proceeding, since gaps could break the momentum calculation." | Call `check_data_quality(tickers=[the 3 problem tickers])` |
| 3 | Tool result: those 3 tickers only IPO'd 8 months ago — not enough history for a 12-month lookback | "These tickers can't have a valid 12-month momentum value by construction. I'll exclude them rather than let them produce garbage or crash the calculation." | Call `compute_momentum(universe=remaining 97 tickers)` |
| 4 | Tool result: 97 raw momentum values returned | "Per the locked pipeline, I need to winsorize before z-scoring." | Call `winsorize(values, pctile=[1,99])` |
| 5 | Tool result: winsorized values | "Now sector-neutral z-score, per the P1-L4 decision." | Call `zscore_by_sector(winsorized_values)` |
| 6 | Tool result: sector-neutral z-scores | "Now compute rank IC against 1-month forward returns." | Call `compute_rank_ic(signal, forward_returns)` |
| 7 | Tool result: rank IC = 0.04 | "This is within the realistic 0.02-0.05 range from P1-L6 — no bug indicators. I have what's needed to answer the original question." | **Stop looping.** Produce final summary for the user. |

Notice what happened at iteration 2-3: **nothing in that branch was hardcoded by a human.** No one wrote "if 3 tickers have missing data, check if they're new IPOs, and if so, exclude them." The agent *itself* noticed something unexpected, reasoned about what it meant, and decided on a corrective action — then continued toward the original goal. That adaptive, self-directed branching is the entire distinguishing feature of agentic behavior.

---

## 5. Why "agent" is a spectrum, not a light switch

One more thing worth internalizing now, because it'll matter across the rest of this track (P1-LA5 ReAct loops, P1-LA6 planning loops, P1-LA7 subagents): **"agent" isn't binary.** There's a spectrum of autonomy, and different points on that spectrum require different amounts of human oversight — which is directly the subject of P1-LA11 (governance) later in this track.

| Level | Description | Where it sits |
|---|---|---|
| Fixed workflow | Zero LLM decision-making about sequence | Not agentic at all |
| Single tool-use loop | LLM decides to call one tool, gets a result, answers — minimal looping | Weakly agentic |
| ReAct-style loop | LLM reasons and acts repeatedly, adapting each step based on the last observation (the worked example above) | Agentic (P1-LA5) |
| Planning loop | LLM forms a multi-step plan *before* executing, and can revise the plan itself if execution reveals the plan was wrong | More autonomous (P1-LA6) |
| Multi-agent orchestration | A top-level agent delegates entire subtasks to other agents, each running their own loop | Most autonomous covered in this project (P1-LA7 — this is literally Project 1's target architecture: orchestrator + validator subagent + memo subagent) |

You don't need to fully understand planning loops or subagents yet — those get their own dedicated lessons — but it's worth knowing now that today's lesson (the basic perceive-reason-act loop) is the atomic building block that all of the fancier patterns are built out of. A planning loop is still, underneath, made of perceive-reason-act cycles. A multi-agent system is multiple perceive-reason-act loops talking to each other. Nothing later in this track invalidates today's lesson — it all just adds structure on top of it.

---

## 6. Glossary (terms introduced this lesson)

| Term | Definition |
|---|---|
| **Large Language Model (LLM)** | The underlying model (e.g., Claude) that generates text based on patterns learned from training data |
| **LLM agent** | An LLM system that can perceive its environment, reason about what to do, take actions (typically via tools), observe the results, and repeat — with the LLM itself controlling the sequence of actions, not a human-written script |
| **Fixed workflow** | A system where the sequence of steps is entirely predetermined by a human in advance; no runtime decision-making by an LLM about *what* to do next |
| **Chatbot** | An LLM system limited to single-turn text generation — no tool use, no ability to act on or fetch from the outside world |
| **Tool** | A function, API, or data source an agent can call to take an action or retrieve information (full treatment in P1-LA2, next lesson) |
| **Perceive-reason-act loop** (also: **agent loop**) | The core operating cycle of an agent: take in current context → reason about next step → take an action → observe the result → repeat until done |
| **ReAct** | Short for "Reason + Act" — a specific, named technique for structuring the perceive-reason-act loop, covered in depth in P1-LA5 |
| **OODA loop** | Observe-Orient-Decide-Act — a decision-making framework originally from military/fighter-pilot doctrine, structurally similar to the agent loop; mentioned here only as an analogy, not something Project 1 will implement directly |
| **Autonomy** (in the agentic sense) | The degree to which an agent decides its own actions/sequence without a human dictating each step in advance; exists on a spectrum from fixed workflow (zero autonomy) to multi-agent orchestration (high autonomy) |
| **Orchestrator** | A term you'll see repeatedly starting in P1-LA7 and throughout Project 1's architecture — a top-level agent that delegates subtasks to other agents (subagents). Introduced here only by name; full treatment later |

---

## 7. Follow-up clarification (2026-07-14): Where does the LLM's "knowledge" in each loop step actually come from?

A sharp follow-up question surfaced after the initial lesson, worth capturing in full because it cuts to something easy to gloss over and directly seeds a later lesson (P1-LA9, agent failure modes): in the worked loop trace in Section 4c, where does each piece of "knowledge" the LLM displays actually come from? Is the LLM "knowing" facts, or something else?

There are two fundamentally different sources of "knowledge" at play in that loop table, and conflating them is exactly the kind of confusion that causes real bugs:

| Source | What it actually is | Verified fact or generated guess? |
|---|---|---|
| **Trained-in pattern knowledge** | Patterns the LLM absorbed during training from an enormous volume of code, finance writing, tutorials, textbooks | A generated inference — plausible, usually right, but not a lookup and not guaranteed correct |
| **Tool results (perceived data)** | Actual output returned by a real tool call that queried a real data source | A fact (as accurate as the tool and its underlying data are) — not generated by the LLM at all |

### 7a. "I need price data before I can compute anything" — how does the LLM know this?

This is category 1 — pattern knowledge, not a lookup. Two things are happening:

- During training, the LLM saw a huge number of quant/data-science examples where "compute momentum/returns" is always preceded by "have price data." That pattern is so consistent across its training data that it's effectively learned the *dependency structure* of financial calculations — the same way a person learns "you can't reconcile a trade blotter before you have the trades" not from one sentence someone told them, but from having seen the pattern play out repeatedly.
- Separately: the LLM is typically handed a **list of available tools with schemas** at the start of the session (names, descriptions, required parameters — full treatment in P1-LA2, the next lesson). If `compute_momentum` is defined with a required input like `price_data`, the LLM can see directly, almost mechanically, "this tool requires price_data and I don't have any yet." That's closer to reading a function signature than "knowing" a fact.

### 7b. "Gaps could break the momentum calculation" — how does the LLM know this?

Also category 1 — pattern knowledge, not certainty. "Missing values break numerical calculations" is one of the single most reinforced patterns in all of the data-science content the model has ever seen — every pandas tutorial, every stats textbook's missing-data chapter, every Stack Overflow thread about a crashed script reinforces some version of this. The LLM isn't *certain* gaps will break this specific calculation — it's making a well-founded probabilistic inference.

This matters: it's a **hypothesis, not a fact.** That's exactly why the agent's next move in the trace is to *check* (`check_data_quality`) rather than guess and proceed, or guess and silently drop the tickers without knowing why. A weaker agent design might skip that verification and just assume — that is itself a real failure mode, named explicitly in P1-LA9 (agent failure modes) later in this track.

### 7c. "Those 3 tickers only IPO'd 8 months ago" — how does the LLM know this?

**This is a fundamentally different category, and it's the most important distinction in this whole clarification: the LLM did not know this. It could not know this. It is not something the LLM generated at all.**

Walk through the mechanics precisely:

| Step | What happened |
|---|---|
| Iteration 2 — Act | The agent called a real tool: `check_data_quality(tickers=[...])` |
| Outside the LLM | That tool is actual code that queried a real data source — e.g., looked up each ticker's earliest available trading date in the price history |
| Tool returns | A real result: "these 3 tickers' first trade date ≈ 8 months ago" |
| Iteration 3 — Perceive | That returned fact becomes new context the LLM reads — it wasn't reasoned into existence, it was *reported* to the LLM by the environment |

This is precisely the perceive/reason distinction from Section 3 of this lesson: **perceive is where real, ground-truth information enters the loop (from tool results); reason is where the LLM draws conclusions about what that information means.** The LLM never invented the IPO date. If the tool hadn't returned it, the LLM would have had no way to know it — a well-designed agent has to call another tool (or say "I don't know") rather than guess at something like an exact date.

This is also exactly why tool design matters so much (P1-LA2) and why hallucination is a real, named risk category later (P1-LA9, P1-LA10): an LLM asked to state a specific, checkable fact like "when did this ticker IPO" *without* a tool call backing it up is reasoning from fuzzy training-data memory — precisely the kind of thing LLMs get wrong. The entire point of the tool-use architecture is to force facts to come from real queries (perceive), not from the LLM's generated guesses (reason).

### 7d. Applying this lens across the full loop trace

| Iteration | Element | Source type | Why |
|---|---|---|---|
| 1 | "I need price data before I can compute anything" | Reasoning (trained pattern knowledge + tool schema) | Learned dependency pattern; also can read `compute_momentum`'s required inputs directly |
| 2 | "Some tickers have missing data — I should check why" | Reasoning (trained pattern knowledge) | Learned pattern that gaps commonly break calculations; a hypothesis, not yet verified |
| 2→3 | "Those 3 tickers only IPO'd 8 months ago" | **Perceiving** (real tool result) | Fact reported by `check_data_quality`'s actual execution, not generated by the LLM |
| 3 | "These tickers can't have a valid 12-month momentum value by construction. I'll exclude them" | Reasoning, applied to a perceived fact | The exclusion *decision* is reasoning; the *reason* the exclusion is valid (insufficient history) is a perceived fact from the previous step |
| 4-6 | "Per the locked pipeline, I need to winsorize..." / "...sector-neutral z-score, per the P1-L4 decision" / "...compute rank IC..." | Reasoning, informed by instructions given to the agent (the locked pipeline order from P1-L4/P1-L5, likely provided in the system prompt or accessible context) | Not training-data pattern knowledge alone — this is following an explicit, provided specification, closer to "reading an instruction" than "inferring a pattern" |
| 7 | "Rank IC = 0.04 is within the realistic 0.02-0.05 range from P1-L6 — no bug indicators" | Perceiving (the IC value itself, a real tool result) combined with reasoning (comparing it against a threshold, whether from trained knowledge of typical IC ranges or from a provided reference value) | The number 0.04 is perceived (real); the judgment "this is a reasonable, bug-free range" is reasoning |

### 7e. The one-sentence version to hold onto

**Everything in the "Reason" column is the LLM's generated inference — plausible, usually right, but not ground truth. Everything that shows up as a "Tool result" feeding the "Perceive" column is real data injected by an actual tool execution — not generated or guessed by the LLM at all.** Distinguishing these two categories cleanly, in real time, is a core skill for debugging agents later (P1-LA12, observability/tracing) and for reasoning about where hallucination risk actually lives in a system (P1-LA9, P1-LA10).

This lesson sets up the vocabulary for the rest of the AI/Agentic track:
- **P1-LA2 (next):** how the "Act" step actually works mechanically — tool schemas, the request/response cycle, how an LLM decides *which* tool to call and with what arguments
- **P1-LA5:** the ReAct pattern named explicitly in this lesson's glossary, covered in full depth
- **P1-LA6:** planning loops — a more structured variant of the loop where the plan is formed up front
- **P1-LA7:** subagents/orchestration — the pattern Project 1's actual architecture uses (orchestrator delegating to a validation subagent and a memo subagent)
- **P1-LA11:** governance and human-in-the-loop design — directly follows from today's autonomy spectrum (Section 5): more autonomous systems need more deliberate oversight design, not less
