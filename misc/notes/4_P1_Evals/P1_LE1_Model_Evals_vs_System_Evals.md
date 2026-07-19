# P1-LE1: Model Evals vs. System Evals

**Track:** Evals & Model Evals (Phase 1, Project 1 — Factor Research Copilot)
**Completed:** 2026-07-18
**Estimated time:** 1-2 hours

---

## 1. What is an "eval," fundamentally?

An **evaluation ("eval")** is a systematic, repeatable test that measures how well an AI system performs a task, producing a number or pass/fail verdict you can track over time and compare across versions.

**Analogy from a trading/PM background:** think of it like a performance benchmark for a trading execution algorithm. You wouldn't ship a new execution algorithm because it "felt faster" in a few manual test runs — you'd run it against a standard set of historical order scenarios, measure slippage/fill-rate/latency on each, and compare the number to the previous version. An eval does the same thing for an AI system: it replaces "this output looked good to me" with "this output scored X on a defined test set, versus Y last week."

Why this matters here specifically: everything built so far (P1-LA9 reliability, P1-LA10 security, P1-LA11 governance) has been about *designing* the system to fail safely. Evals are how you'd *prove*, with a number, that it actually works — and prove it again every time a prompt changes, a model swaps, or a tool is added. Without evals, every change is a leap of faith.

---

## 2. The core distinction: model evals vs. system evals

This is the single most important thing this lesson teaches. Interviewers ask about this distinction specifically because conflating the two is a common and costly Product Manager (PM) mistake.

| | Model eval | System eval |
|---|---|---|
| **What it tests** | The underlying Large Language Model (LLM) itself — its raw, general-purpose capability | The specific end-to-end pipeline built on top of the model — prompts, tool calls, orchestration, validators, everything custom-built |
| **Question it answers** | "How good is Claude Sonnet 4.6 at math reasoning / code generation / following instructions, in general?" | "Does *my* factor-spec extractor correctly turn a user's hypothesis into valid JSON, using *my* prompt, *my* schema, *my* tools?" |
| **Who usually runs it** | Anthropic (and other model labs) — the results are consumed, not generated, by the product builder | The product builder — this is a build artifact, not something read off a leaderboard |
| **Changes when...** | A new model version ships | The prompt, tool wiring, schema, or orchestration logic changes (even if the model stays the same) |
| **Analogy** | A new analyst's GMAT score / general aptitude test | Whether that specific analyst, doing this specific job, with this specific training given to them, actually produces good work |

### Why the distinction matters in practice — a worked scenario

Say Anthropic publishes a benchmark showing Claude's newest model scores 12% higher on a general reasoning benchmark than the version currently in use. That's a **model eval** result. It tells you nothing directly about whether the factor-spec extractor will get *better* if switched to it — the extractor's behavior also depends on the prompt template, the few-shot examples (P1-LA17), and the JSON schema. The new model might:

- Improve the system eval score too (the common case), **or**
- Leave it unchanged (the bottleneck was the prompt, not model capability), **or**
- Make it *worse* (the new model's different response style breaks a rigid parsing assumption in the code)

There is no way to know which of these three happened without running a **system eval** on the new model. This is exactly why an AI Product Manager (AI PM) role expects ownership of system evals — the model lab already owns model evals; nobody else owns testing whether the actual product works.

### The reverse failure mode is just as real

If a system eval score is bad, it's tempting to blame "the model isn't good enough" and go shopping for a better one. Sometimes that's correct. But often the actual bug is in the prompt, the schema, or a tool returning malformed data — and no amount of model-swapping fixes a system-level bug. System evals are what let you tell the difference before spending a day re-plumbing model calls that weren't the actual problem.

---

## 3. Sub-concept: LLM-as-judge methodology

**The problem it solves:** for a lot of what the system produces — a research memo's prose, a validator's written reasoning — there's no single "correct answer" to string-match against. Correctness is a matter of judgment: is this memo clear? Does this validator's reasoning actually address the multiple-testing issue? A rigid exact-match test can't grade that. Historically, the answer was a human grading every output by hand — but that doesn't scale to running hundreds of test cases every time a prompt is tweaked.

**LLM-as-judge** is the practice of using a second LLM call to grade the first LLM's output against an explicit rubric, standing in for the human grader.

### Mechanically, one judge call needs three inputs

| Input | What it is |
|---|---|
| The output being graded | The memo, the validator verdict, the extracted JSON spec — whatever the system produced |
| The rubric | Explicit scoring criteria (see Section 4) |
| (Optional) A reference answer | A "gold standard" example to compare against, if one exists |

The judge model returns a score (often 1-5 per criterion) plus, ideally, a short justification that can be spot-checked.

### Two documented failure modes

1. **Verbosity bias:** judge models tend to rate longer outputs more favorably, treating length as a proxy for thoroughness even when the extra words are padding, not substance. If the memo generator produces a 400-word memo and a 700-word memo of equal actual quality, a judge model will often score the 700-word one higher purely because it's longer.

2. **Self-preference bias:** a judge model tends to rate outputs generated by its own model family more favorably than outputs from a different model family, even when a neutral human grader would call them equivalent. Comparing Claude-generated memos against a competing model's memos using a Claude judge means the judge's score is *not* neutral — it's thumb-on-the-scale toward Claude.

### Worked numeric example — grading two memo drafts on the same rubric (Correctness, Completeness, Actionability, each 1-5)

| Draft | Length | Correctness | Completeness | Actionability | Judge's total (out of 15) |
|---|---|---|---|---|---|
| Draft A | 320 words, tight, all facts correct, clear recommendation | 5 | 4 | 5 | 14 |
| Draft B | 680 words, same facts restated with extra hedging language, same recommendation buried in paragraph 4 | 5 | 5 | 3 | 13 |

A well-designed rubric with explicit anchors (e.g., "Completeness = 5 means every required section is present, not that more words were used") should score these close to what a careful human would say — Draft A is actually better because the recommendation is clearer. If a judge instead scores Draft B a 15 because it "covered more ground," that's verbosity bias showing up in the eval pipeline, silently rewarding the memo generator for being wordy.

**Practical mitigation:** write rubric criteria that penalize unnecessary length explicitly ("Completeness is capped at 3 if the required content could have been stated in half the words"), and periodically spot-check judge scores against a human read of a sample.

---

## 4. Sub-concept: Golden dataset and rubric design

**Golden dataset:** a curated, fixed set of input/expected-output pairs that represents the real range of scenarios the system will face — the test set run against every eval, so results are comparable run to run.

**Rubric:** the explicit, written scoring criteria applied to each output — turning "does this look right" into a checklist or scale that produces the same score whether a human or an LLM judge applies it, and whether it's applied today or three weeks from now.

**Why "golden" and not just "a bunch of examples":** the dataset needs deliberate coverage of edge cases, not just easy/typical cases, or the eval will look great while the system quietly fails on the fraction of real inputs that resemble nothing in the test set. This is the same instinct as P1-LA17's few-shot example design (diversity of edge cases over raw count) — applied to the test set instead of the prompt.

### Worked example — golden dataset for the factor-spec extractor (from P1-LA16/LA17)

| # | Input hypothesis | Expected `factor_type` | Expected exclusions captured? | Edge case being tested |
|---|---|---|---|---|
| 1 | "Stocks with low P/E ratios tend to outperform" | `value` | No exclusions | Baseline, unambiguous case |
| 2 | "Value stocks, but exclude anything that looks like a value trap" | `value` | Yes — value-trap exclusion flagged | The exact ambiguous case from P1-LA16/LA17 that motivated few-shot prompting |
| 3 | "Momentum works, except during earnings season" | `momentum` | Yes — earnings-season exclusion flagged | Time-conditional exclusion, a different exclusion *type* than #2 |
| 4 | "I think small caps with high short interest do well" | `size` (with `short_interest` as modifier, not a new factor) | No exclusions | Tests whether the model correctly treats a qualifier as a modifier rather than inventing a new `factor_type` |
| 5 | "asdkjf random gibberish" | N/A — should return a structured error/`escalation`, not a hallucinated guess | N/A | Tests failure-mode handling: does the system correctly refuse rather than confidently inventing a spec? |

A rubric for grading row 2, for instance, might be: *"5 = correctly identifies `value` as base factor_type AND captures the value-trap exclusion as a modifier, not a separate factor. 3 = correct factor_type but exclusion missed or miscategorized. 1 = wrong factor_type."* This specificity is exactly what "rubric design" means in practice, versus a vague "rate this 1-5 for quality" prompt which invites drift and inconsistency between grading runs.

---

## 5. Sub-concept: Eval metrics for structured/agentic output

The system doesn't just produce prose — it produces structured JSON, tool calls, and multi-step agent traces (P1-LA12). These need metrics that plain "did the LLM say something reasonable" don't capture.

| Metric | What it measures | Plain-language question it answers |
|---|---|---|
| **Task success rate** | Of all test cases run, what fraction did the system actually accomplish the end goal on (not just "produce some output" but "produce the *correct* output")? | "Out of everything it was asked to do, how often did it actually do it?" |
| **Schema-validity rate** | Of all outputs produced, what fraction successfully parse against the Pydantic schema without a validation error? | "How often does the output even come back in the shape the downstream code expects?" |
| **Groundedness / faithfulness** | Does every factual claim in the output trace back to real retrieved or computed data, rather than being invented? | "Is the memo/validator saying things that are actually true of *this* backtest, or is it making things up?" |

Schema-validity rate is a narrower, more mechanical check than task success rate — an output can be perfectly valid JSON (parses fine) while still being *wrong* (task failed), which is exactly why both metrics are needed, not just one. Groundedness is directly the system-eval version of P1-LA12's "reason vs. observation" hallucination distinction: a groundedness check is asking, formally and at scale, whether every `reason`-type claim in the trace is actually backed by a real `perceive`/`observe` event, rather than eyeballing individual traces one at a time.

### Worked numeric example — a batch eval run of 50 test cases through the factor-spec extractor

| Metric | Count | Rate | What a failure in this metric alone would look like |
|---|---|---|---|
| Task success rate | 42 / 50 correct | 84% | Extractor confidently returns a *plausible but wrong* factor_type — schema is valid, but the answer is incorrect |
| Schema-validity rate | 47 / 50 parse cleanly | 94% | Model returns malformed JSON (missing a required field, wrong data type) — this breaks downstream code even before correctness can be judged |
| Groundedness (avg. judge score, 1-5) | — | 4.1 / 5 | Validator asserts "this factor has a Rank IC of 0.06" when the actual computed Information Coefficient (IC) in the trace was 0.04 — a fabricated number dressed up as a real result |

These three numbers can diverge in informative ways. A system with 94% schema-validity but only 84% task success indicates: *the plumbing basically works, but correctness has real headroom* — a very different diagnosis, and a different fix, than a system with 60% schema-validity, where the first problem to fix is upstream of correctness entirely (the model isn't even returning usable JSON reliably).

---

## 6. Tying it back to prior lessons

| Prior lesson | How LE1 extends it |
|---|---|
| P1-LA9 (agent failure modes / reliability) | Reliability was about *designing* for failure (retries, `ValidationResult.passed` as a recommendation not a verdict). Evals are how one would *measure*, with a number, how often that design actually holds up. |
| P1-LA11 (governance) | `ValidationResult.severity: "blocking"` triggers a human checkpoint — but how does one know the validator itself is any good? A system eval on the validator subagent (does it correctly flag the multiple-testing cases from P1-LB3?) is what gives evidence to trust or distrust the validator, rather than trusting it on faith. |
| P1-LA12 (observability/tracing) | The seven-type trace taxonomy shows *what happened* in one run. An eval running across a golden dataset shows *how often it happens correctly*, aggregated across many runs — tracing is per-incident forensics, evals are the aggregate scoreboard. |
| P1-LB3 (multiple testing) | Directly usable as golden-dataset test cases for the methodology validator: a set of backtests with known undisclosed variant counts, known-missing corrections — the "expected verdict" for each is already established from that lesson. |

---

## 7. Where this lands in the build (Phase 3 preview — no build work required yet)

This lesson doesn't require any build work yet — that's Phase 3. But it directly shapes what P1-Build items will need to include:

- A **golden dataset file** for the factor-spec extractor (structured like the 5-row table above, expanded to cover real edge cases)
- A **golden dataset** for the methodology validator, directly reusing P1-LB1/LB2/LB3 scenarios (walk-forward violations, winner's-curse-style cherry-picking, undisclosed multiple testing) as test cases with known-correct verdicts
- A lightweight **LLM-as-judge harness** for the memo generator, with an explicit anti-verbosity-bias rubric
- Reporting all three metrics (task success rate, schema-validity rate, groundedness) per component, not folded into one vague "quality score"

---

**Deliverable:** This notes file (P1_LE1_Model_Evals_vs_System_Evals.md)
**Next lesson:** P1-LE2 — AI product metrics & KPIs (final lesson of Phase 1 before Architecture begins)
