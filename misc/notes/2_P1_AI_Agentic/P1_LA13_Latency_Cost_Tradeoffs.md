# P1-LA13: Latency & Cost Tradeoffs

**Track:** AI/Agentic (13 of 17)
**Date completed:** 2026-07-16
**Estimated time:** 1 hour

---

## 1. Token economics — what you're actually paying for

You've been building `TraceEvent` objects since P1-LA12 with a `token_count` field sitting there unused. This lesson is where that field starts paying rent.

**What a token is.** A **token** is the basic unit a language model reads and writes — roughly ¾ of an English word, or about 4 characters. "Portfolio" might be one token; "counterparty" might split into two ("counter" + "party"). You don't control tokenization directly; the API does it for you. What matters for this lesson is simpler: tokens are the unit the API bills you on, the same way your firm doesn't bill a trade in "effort," it bills in shares or notional.

**Two token types, two prices — and they are not the same price.** Every API call has:
- **Input tokens** — everything you send: system prompt, conversation history, tool results, the user's message.
- **Output tokens** — everything the model generates in response.

Anthropic (and every other provider) prices these separately, and output tokens cost meaningfully more per token than input tokens — typically 4-5x more.

**Why the asymmetry — the intuition, not just the price sheet.** Think of input processing like a trader reading a research report: the whole page is in front of them at once, so reading it is fast and parallel — the model can process the entire input in one pass. Output generation is different. A language model produces one token, then must look at everything so far (including the token it just wrote) to decide the *next* token, then the next, one at a time, in sequence. It's the difference between skimming a memo (input) and being asked to compose the reply live, word by word, unable to skip ahead (output). That sequential, one-token-at-a-time process is inherently more expensive per token — which is also, not coincidentally, why output is *slower* per token too (see Section 3).

**Worked example — pricing a single call.**

Say a mid-tier model is priced at $3 per million input tokens and $15 per million output tokens (illustrative numbers — always check current pricing at build time, rates change).

| Component | Tokens | Rate | Cost |
|---|---|---|---|
| Input (system prompt + conversation so far + tool result) | 2,400 | $3 / 1M | $0.0072 |
| Output (model's reasoning + next tool call) | 180 | $15 / 1M | $0.0027 |
| **Total, this one call** | 2,580 | — | **$0.0099** |

Ten thousand tokens sounds like a lot until you see it's about a penny. The danger isn't any single call — it's what happens when you multiply this across an agent loop with many calls per run and many runs per day. That's Section 2.

---

## 2. The tool-use loop's hidden cost trap: context re-sending

Here's the part that catches almost everyone building their first agent, and it's a direct callback to P1-LA1's 7-iteration momentum trace.

**The core fact:** in a multi-turn tool-use loop, the model has no persistent memory between API calls. Every single call must resend the *entire conversation so far* as input — every prior `perceive`, `reason`, `act`, `observe` event, every tool result, every system prompt. It's not additive memory on the server side; it's a fresh call each time carrying the whole transcript.

**Analogy from your world:** imagine every time you wanted to add one line to a due-diligence memo, you had to reprint and resubmit the *entire* memo from page one, get it stamped, and then add your one new line at the end. The stamping cost (input token cost) scales with the whole memo's length, not just your new line — even though your new contribution might be tiny.

**Worked example — reconstructing cost across P1-LA1's 7-iteration trace.**

Assume each iteration adds roughly 300 tokens of new content (a tool call + tool result + reasoning), and the system prompt is a fixed 500 tokens included every time. Output per iteration averages 150 tokens (reasoning + next action). The "what this step does" column reconstructs the actual 7-iteration momentum trace first introduced in P1-LA1 (pull data → discover data gaps → exclude bad tickers → winsorize → sector-neutral z-score → compute rank IC and stop).

| Iteration | What this step does | Input tokens (cumulative history) | Output tokens | Input cost ($3/1M) | Output cost ($15/1M) | Running total |
|---|---|---|---|---|---|---|
| 1 | Pull 13 months of price history for the full NASDAQ-100 universe | 500 (system only) | 150 | $0.0015 | $0.00225 | $0.00375 |
| 2 | Observe data gaps — notice 3 tickers have incomplete price history | 950 | 150 | $0.00285 | $0.00225 | $0.0089 |
| 3 | Investigate the gaps — reason that the 3 tickers are likely recent IPOs | 1,250 | 150 | $0.00375 | $0.00225 | $0.0149 |
| 4 | Confirm and exclude — observe confirms insufficient history for the flagged ticker(s); decide to exclude from the universe (no hardcoded rule) | 1,550 | 150 | $0.00465 | $0.00225 | $0.0219 |
| 5 | Winsorize the raw momentum factor (1st/99th percentile) for the remaining 97 tickers | 1,850 | 150 | $0.00555 | $0.00225 | $0.0296 |
| 6 | Compute sector-neutral z-scores from the winsorized values | 2,150 | 150 | $0.00645 | $0.00225 | $0.0384 |
| 7 | Compute rank IC, compare to the realistic range (IC≈0.04 vs. P1-L6's expected range), stop with no bug indicators | 2,450 | 150 | $0.00735 | $0.00225 | $0.0480 |

**Note — this is the clean trace, not the planted-bug version.** Iteration 4 above is the same iteration used in P1-LA12's worked hallucination-debugging example, but that example used a *different, deliberately broken* version of iteration 4: an `observe` event reporting only "insufficient history — only 45 days available," followed by a `reason` event claiming the ticker "IPO'd 8 months ago" with no supporting observation behind it. That version exists purely to illustrate the Reason-vs-Observe hallucination signature from P1-LA12; the version in the table above is the clean, no-bug trace this lesson's cost/latency math is built on.

**The shape that matters:** input tokens grow *linearly* with iteration count (each iteration adds a fixed slice of history), but because you pay for the *cumulative* history on every single call, total cost across the run grows **superlinearly** — a run with twice the iterations doesn't cost twice as much, it costs more than twice as much. A 7-iteration run here costs $0.048; a 14-iteration run (double the steps) would cost roughly $0.17 — over 3x, not 2x. This is exactly why P1-LA6's "replan only when a downstream assumption breaks" principle and P1-LA9's retry caps aren't just correctness safeguards — they're cost safeguards. An agent that loops longer than necessary is spending money on the same growing-history tax every single step.

**This is what `token_count` in your `TraceEvent` schema is for.** You already log it per event (from P1-LA12). The concrete build-time task this unlocks: sum `token_count` across every event sharing a `trace_id`, split by input vs. output, and you have the actual dollar cost of one end-to-end run — not an estimate, a measurement.

---

## 3. Latency — what actually makes an agent feel slow

**What latency is, concretely.** Two components matter:
- **Time to first token (TTFT)** — how long you wait before the model starts responding at all (this includes processing all that input you just sent).
- **Generation speed** — tokens per second once it starts producing output, which — per Section 1's sequential-generation point — is inherently slower than input processing and gets slower still with larger, more capable models (more computation per token generated).

**Why latency compounds in an agent, not just in a single call.** In your P1 pipeline, calls are **serial, not parallel** — the orchestrator can't call iteration 4 before it has iteration 3's result, and it can't invoke the validator subagent (P1-LA7) before the factor-spec extractor has finished. Each step's latency stacks directly onto the next.

**Worked example — a latency budget for one end-to-end P1 run.**

| Stage | Calls | Latency per call (est.) | Stage total |
|---|---|---|---|
| Orchestrator, 7-iteration momentum loop | 7 | ~2.5 sec/call | 17.5 sec |
| Factor-spec extraction subagent | 1 | ~2 sec | 2 sec |
| Validator subagent (P1-LA7/LA9) | 1 | ~3 sec (larger model, per Section 4) | 3 sec |
| Memo-generation subagent | 1 | ~4 sec (longer output) | 4 sec |
| **Total, one full run** | 10 | — | **~26.5 sec** |

Nothing here is parallelizable given the current architecture (each stage depends on the prior stage's output), so this ~26.5 seconds is close to a hard floor, not an average — the run *cannot* go faster than the sum of its serial dependencies, only slower (network variance, rate limiting, larger responses). If a PM stakeholder asked "why does this take 30 seconds," this table is the honest answer: it's not one slow thing, it's ten sequential things.

---

## 4. Model selection: the three-way tradeoff

**The core tradeoff, stated plainly:** cost, latency, and quality move together — you generally cannot improve one without giving up ground on another, for a fixed task. A larger/more capable model produces higher-quality output but costs more per token *and* generates each token more slowly. A smaller/cheaper model is fast and cheap but may miss nuance, follow instructions less reliably, or make more extraction errors.

**Analogy from your world:** this is a staffing decision, not a technology decision. You wouldn't route every single trade ticket to your most senior, most expensive analyst for review — that person is expensive and their time is scarce, and a junior analyst (or a well-defined checklist) handles routine tickets fine. You *do* route the trade that breaches a risk limit to the senior analyst, because the cost of a wrong call there is high and the judgment required is real. Model selection in an agentic pipeline is the same allocation problem: match the model's capability (and cost) to the task's actual difficulty and stakes — not to the hardest task in the pipeline, applied uniformly to all of them.

**The framework — two questions, not one.** For any given step in your pipeline, ask:

| Question | If answer is "narrow / low" | If answer is "broad / high" |
|---|---|---|
| **How well-defined is the task?** (Is it structured extraction/classification, or open-ended judgment?) | Smaller model is often fine | Larger model earns its cost |
| **What are the stakes if it's wrong?** (Tie back to P1-LA11's Consequence × Reversibility × Confidence-gap framework) | Smaller model's occasional errors are cheap to tolerate | Larger model's better judgment is worth paying for |

This second question is the one people skip, and it's the one that matters most in this specific pipeline, because the exact scoring framework for it was already built in P1-LA11.

**Worked example — applying the framework to P1's own three subagents.**

| Subagent | Task well-definedness | Stakes (P1-LA11 framework) | Recommendation | Why |
|---|---|---|---|---|
| Factor-spec extractor | Narrow — structured extraction into a `FactorSpec` Pydantic model, closed set of fields | Low-moderate — a `ValidationError` triggers the P1-LA5 retry-with-feedback pattern rather than silently propagating a bad spec | **Candidate for smaller/cheaper model** | Well-defined, low blast radius if wrong on the first attempt, cheap to retry |
| Validator subagent | Broad — judgment call requiring `severity: "blocking"` decisions that halt the pipeline (P1-LA11) | High — this *is* the escalation checkpoint; a missed blocking case defeats the governance design | **Keep on the larger/stronger model** | This is exactly the "high stakes, real judgment" cell — the one place in the pipeline where cost-cutting is the wrong move |
| Memo-generation subagent | Moderate — requires coherent prose and correct tone, but works from already-validated structured inputs | Low-moderate — output requires human sign-off before being "final" (P1-LA11 governance decision), so a mediocre draft is a nuisance, not a failure | **Candidate for smaller/cheaper model, worth testing** | Human review is already the safety net (per LA11); a cheaper model producing a slightly less polished first draft is an acceptable cost/quality trade *because that safety net exists* |

Notice the pattern: **the validator's exemption from cost-cutting isn't a vague "it's important" — it's a direct consequence of the escalation-checkpoint design already locked in P1-LA11.** That's the payoff of doing these lessons in order: the governance framework is now also the model-selection framework.

**The critical caveat — this table is a hypothesis, not a decision.** Everything above is *reasoning* about which subagents are good candidates for a cheaper model. It is not evidence. The curriculum already has the actual test built in as a deliverable (P1-Build task, `curriculum.md` line 366): run the extractor, validator, and memo-writer subagents on two different models — a larger and a smaller Claude model — on the same inputs, and measure cost, latency, *and* quality side by side. That comparison is the **model-evals artifact** (distinct from the system evals covered in the Evals track) — and it's exactly the kind of empirical, "I didn't just guess, I measured it" story that's strong interview material for an AI PM role.

---

## 5. Putting it together — the decision checklist

When deciding which model tier to assign to any given step in an agentic pipeline, work through these in order:

1. **Classify the task.** Structured extraction/classification/formatting → lean toward smaller. Open-ended judgment, nuanced reasoning, high ambiguity → lean toward larger.
2. **Score the stakes**, reusing P1-LA11's Consequence × Reversibility × Confidence-gap framework — don't invent a new stakes framework, one already exists.
3. **Check what safety net already exists downstream** (retry-with-feedback, human sign-off, an escalation checkpoint). A strong safety net raises the tolerance for a cheaper, occasionally-wrong model upstream of it.
4. **Estimate the cost/latency delta empirically**, using the `TraceEvent` `token_count` and `latency_ms` fields — don't eyeball it, sum it from real trace logs the way Section 2's worked table did.
5. **Run the actual eval** (larger vs. smaller model, same inputs, measure cost/latency/quality) before locking the decision. Reasoning gets you a hypothesis; the eval gets you a decision you can defend.

---

## Summary of concepts covered

- Tokens as the billing unit; input vs. output token pricing asymmetry and why it exists (parallel input processing vs. sequential/autoregressive output generation)
- The tool-use loop's context re-sending problem: no persistent server-side memory between calls, full conversation history resent every call, cost grows superlinearly with iteration count
- Latency components: time to first token, generation speed, and serial-dependency compounding across a multi-stage pipeline
- The three-way cost/latency/quality tradeoff in model selection, and the two-question framework (task well-definedness + stakes) for deciding when a smaller/cheaper model is appropriate
- Direct reuse of the P1-LA11 Consequence × Reversibility × Confidence-gap framework as the stakes axis of the model-selection decision
- The distinction between reasoning toward a model-selection hypothesis and validating it with an actual model-evals comparison (cost/latency/quality on two models, same inputs)

## Carried-forward action items surfaced this lesson

- **(P1-LA13) → P1-Build-7/P1-Build-8:** Compute actual per-run cost and latency from `TraceEvent` logs — sum `token_count` (split input/output) and `latency_ms` across all events sharing a `trace_id`. This turns Section 2/3's worked estimates into real measurements once the pipeline is built.
- **(P1-LA13) → P1-Build (model-evals artifact, per curriculum.md's existing "What you build" deliverable):** Run the factor-spec extractor, validator, and memo-writer subagents on two different Claude models (larger vs. smaller) against the same inputs; report cost, latency, and quality deltas per subagent. Use this lesson's Section 4 table as the starting hypothesis, not the final answer — the eval result is what actually decides model assignment per subagent.
- **(P1-LA13) → P1-Polish (risk memo / README):** The cost/latency tradeoff table (Section 4) and the "reasoning vs. empirical eval" distinction (Section 4 caveat, Section 5 step 5) are strong interview material for "how do you decide which model to use for which task" — cite the actual eval numbers once available, not just the reasoning framework.
- **(P1-LA13, open/residual item):** Exact latency-per-call figures used in Section 3's worked table are illustrative placeholders, not measured values. Re-verify against real API latency at P1-Build-7 implementation time — figures will vary by model tier, prompt length, and provider load, and should not be treated as reliable estimates for capacity planning.
