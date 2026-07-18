# P1-LA17: Prompt Engineering Fundamentals

**Track:** AI/Agentic (final lesson — 17/17, track COMPLETE)
**Completed:** 2026-07-18
**Estimated time:** 1 hour

---

## 1. What prompt engineering fundamentally is

The intuition before any technique: **Claude is a brilliant new analyst who has just walked in the door with no memory of your team, your conventions, or your preferences — every single time you talk to it.** It knows finance broadly. It doesn't know that your firm's memo format puts the recommendation before the rationale, that "value trap" has a specific meaning in your factor taxonomy, or that when you say "flag it" you mean escalate per the P1-LA11 checkpoint framework, not just make a note.

A new human analyst learns your conventions over weeks, by watching you correct their drafts. Claude doesn't get weeks — it only has what's in the prompt, right now, for this call. Prompt engineering is the discipline of front-loading everything that analyst would normally learn through correction, so the first draft is already right.

This reframes what "prompt engineering" is *not*: it's not a bag of magic phrases ("think step by step," add exclamation marks) that trick the model into being smarter. It's closer to writing an excellent onboarding document and a clear work order — for someone who is extremely capable but has zero institutional context and won't ask clarifying questions unless you explicitly invite them to.

Three techniques dominate this discipline, used across every P1 build sprint: **few-shot examples**, **chain-of-thought prompting**, and **structured prompting patterns**.

---

## 2. Few-shot examples

### Intuition

Telling a new analyst "write it in our house style" gets you their best guess at your house style. Handing them three real memos we've published gets you our house style. Examples are more information-dense than descriptions — they show the pattern instead of describing it, and showing is far more reliable than telling for anything involving format, tone, or edge-case judgment calls.

### Vocabulary

| Term | Meaning |
|---|---|
| Zero-shot prompting | You describe the task with instructions only — no example input/output pairs |
| Few-shot prompting (also called "multishot") | You include a handful of example input/output pairs before the real task |
| In-context learning | The umbrella term for the model inferring a pattern from examples given at request time — no weight updates, unlike fine-tuning (P1-LA16) |

### Worked example — the factor-spec extractor

Running scenario from P1-LA16: a user says *"I want a factor that avoids value traps"* and the extractor needs to map this to a structured spec.

**Zero-shot prompt (instructions only):**

```
Extract the user's investment hypothesis into a FactorSpec JSON object
with fields: factor_type, direction, exclusions, rationale.
```

Given only this, Claude has to guess what "value trap" maps to in your taxonomy — is it an `exclusion`? A `factor_type` of its own? A modifier on a value factor? Nothing in the zero-shot prompt disambiguates this, so output is inconsistent across calls — exactly the "phrasing gap" failure P1-LA16 flagged.

**Few-shot prompt (3 examples added):**

```
Example 1:
Input: "I want exposure to cheap stocks with strong momentum"
Output: {"factor_type": "value+momentum composite", "direction": "long",
"exclusions": [], "rationale": "combines value and momentum signals"}

Example 2:
Input: "Value stocks, but not ones that are cheap for a bad reason"
Output: {"factor_type": "value", "direction": "long",
"exclusions": ["value_trap"], "rationale": "standard value tilt with
value-trap exclusion filter applied post-ranking"}

Example 3:
Input: "Small caps with low debt"
Output: {"factor_type": "size+quality composite", "direction": "long",
"exclusions": ["high_leverage"], "rationale": "small-cap tilt filtered
for balance-sheet quality"}

Now extract:
Input: "I want a factor that avoids value traps"
```

Example 2 is doing the real work — it directly shows the model that "value trap" language maps to `exclusions: ["value_trap"]` on top of a base `value` factor, not a new factor type. That's a pattern no amount of zero-shot instruction-writing communicates as reliably as one well-chosen example.

### Worked numeric cost comparison

Using the same Sonnet-tier pricing confirmed in P1-LA16 ($3/million input tokens, verified via web search rather than assumed from memory):

| Prompt version | Approx. tokens | Cost per call | Cost at 50 calls/day |
|---|---|---|---|
| Zero-shot (instructions only) | ~150 | $0.00045 | $0.0225/day |
| Few-shot (3 examples added, ~150 tokens each) | ~600 | $0.0018 | $0.09/day |
| **Marginal cost of going few-shot** | +450 tokens | **+$0.00135/call** | **+$0.0675/day** |

Going from zero-shot to few-shot costs about 6 cents a day at current dev-scale call volume. This is the same $0.0018/call figure P1-LA16 used as the "Option A" baseline against fine-tuning's break-even — few-shot prompting is nearly free compared to any alternative, which is exactly why P1-LA16 concluded prompting should almost always be the first move before fine-tuning is even considered.

### How many examples, and how to choose them

Confirmed via current Anthropic documentation: the recommendation is **3-5 relevant, diverse, well-tagged examples** rather than one or dozens. Reasoning: one example risks the model overfitting to that example's surface details (copying its exact phrasing rather than the underlying pattern); dozens burn tokens for diminishing returns past the point where the pattern is already clear. Diversity matters more than count — three examples that each demonstrate a *different* edge case (a composite factor, an exclusion pattern, a different composite) teach more than three examples that are trivial variations of each other.

| Choosing examples — do | Choosing examples — don't |
|---|---|
| Pick examples that each demonstrate a distinct pattern or edge case | Pick multiple examples that are near-duplicates of each other |
| Include the tricky case you actually saw fail (the "value trap" phrasing gap) | Only include easy, unambiguous cases |
| Keep the output format identical across all examples | Vary the output format between examples — this teaches inconsistency |

---

## 3. Chain-of-thought (CoT) prompting

### Intuition

If you ask a junior analyst "what's this stock worth?" and they blurt out a number with no shown work, you don't trust it — you ask them to walk you through the DCF. Chain-of-thought prompting is asking the model to write out its reasoning steps *before* committing to a final answer, the same way you'd insist on seeing the analyst's work rather than just their conclusion.

This connects directly to P1-LA12's trace event taxonomy: CoT prompting is a technique for **deliberately generating more `reason`-type trace events before the `act` or final output**, on the theory that a model forced to articulate its reasoning step by step catches its own errors along the way — the same way you catch arithmetic mistakes when forced to show your work rather than doing it in your head.

### Three levels of CoT

| Level | What it looks like | When to use |
|---|---|---|
| Basic | Append "Think step by step" to the prompt | Quick, low-stakes tasks where you just want *some* deliberation |
| Guided | Explicitly list the reasoning steps you want followed | You know the right decomposition and want it followed exactly |
| Structured | Use XML tags (`<thinking>...</thinking>`, `<answer>...</answer>`) to separate reasoning from the final output | Production use — lets you programmatically discard the reasoning and keep only the answer, while still logging the reasoning for debugging |

### Worked example — the methodology validator

Using the `ValidationResult.passed` component from P1-LA9/LA11 — recall a `passed: true` here is a *recommendation to a human accountable party*, not a final decision. Guided-CoT version:

```
Evaluate this factor backtest for methodology issues. Think through each
check in order before giving your verdict:

1. Rank IC: Is the reported Rank IC computed via Spearman correlation
   over the full backtest window, not a cherry-picked sub-period?
2. Statistical significance: Is a t-statistic reported alongside the IC,
   and does it clear a reasonable significance bar?
3. Multiple-testing exposure: How many factor variants were tested to
   arrive at this one? Does the reported significance account for that?
4. Beta-neutrality: Is beta-to-market reported as a deviation-from-zero
   check, not flagged as "good/bad" the way Sharpe or IR would be?

<thinking>
Walk through checks 1-4 against the provided backtest output.
</thinking>
<answer>
{"passed": true/false, "flagged_issues": [...], "escalate": true/false}
</answer>
```

This structured CoT prompt forces the model to check the **multiple-testing problem** explicitly (step 3) — precisely the failure mode that's easy to skip if the model jumps straight to "the Rank IC looks good, pass." Requiring the reasoning steps up front is what catches "this looks fine on the surface but 40 factor variants were silently tried to get here" — exactly the kind of methodology error a real senior analyst would catch and a rushed junior analyst would miss.

### Nuance: extended thinking vs. manual CoT prompting

Confirmed from current Anthropic guidance: newer Claude models (including the ones in this stack) have a native **extended thinking** mode — an actual reasoning capability turned on via an API parameter, distinct from prompting the model to "think step by step" in its regular output. When extended thinking is available and turned on, results are generally better with *less* prompt engineering effort than hand-building an elaborate CoT scaffold. The manual `<thinking>` tag technique above is explicitly documented as the **fallback for when thinking mode is off**, not a permanent replacement for it.

**Build-sprint action item:** before hand-rolling a CoT prompt structure for any P1 component, check whether the specific SDK/API call being made has extended thinking available and whether turning it on gets equivalent or better results with less prompt-engineering overhead.

### When to use CoT vs. skip it

| Use CoT | Skip CoT |
|---|---|
| Multi-step methodology review (the validator above) | Simple format conversion (JSON reshaping) |
| Decisions with several weighted factors (P1-LA11's escalation scoring: Consequence × Reversibility × Confidence-gap) | Straightforward lookups with one clear answer |
| Anything where a rushed answer plausibly skips a check | Tasks where extra reasoning tokens just add latency/cost for no accuracy gain (ties directly to P1-LA13's latency & cost tradeoffs) |

---

## 4. Structured prompting patterns

### Intuition

A job packet with a cover memo, a labeled attachments section, and a clearly marked "fill in this form" section gets filled out correctly far more often than the same information poured into one unstructured wall of text. Structure isn't decoration — it's how you prevent the model from confusing your *instructions* with your *data*, or your *examples* with the *actual task*.

### The mechanism: XML tags

Confirmed via current Anthropic documentation: Claude was trained to pay close attention to XML-style structure, and the recommendation is to use tags to delineate every distinct section of a prompt — instructions, background data, examples, and desired output format each get their own tag. There's no fixed required tag vocabulary; what matters is that the tags are semantically meaningful and used *consistently* throughout a given prompt.

A representative structure, adapted to the factor-spec extractor:

```xml
<role>
You are a factor-spec extraction assistant for an investment research platform.
</role>

<instructions>
Extract the user's natural-language investment hypothesis into a structured
FactorSpec JSON object. Map ambiguous language (e.g. "value trap") to the
correct combination of factor_type and exclusions rather than inventing a
new factor_type.
</instructions>

<examples>
[the 3 few-shot examples from Section 2 go here]
</examples>

<data>
{{user_query}}
</data>

<output_format>
Return only a single JSON object matching the FactorSpec schema. No
preamble, no explanation outside the JSON.
</output_format>
```

**Why this matters more than it looks like it should:** without tags, a long prompt containing instructions, three examples, and a live query all as undifferentiated prose creates real ambiguity about where the "example" ends and the "actual task" begins — exactly the kind of confusion that produces a `passed: true` on the wrong input, or an extractor that answers Example 3's question instead of the live one. Tags remove that ambiguity structurally rather than relying on the model to infer boundaries from prose flow.

### Nesting for hierarchy

Tags can nest — `<examples><example><input>...</input><output>...</output></example></examples>` — useful once examples themselves have multiple parts, exactly like the input/output pairs above.

### Combining all three techniques

The techniques compose — this is the real power move: few-shot examples *inside* a structured prompt, where the examples themselves demonstrate the desired chain-of-thought:

```xml
<examples>
<example>
<input>Backtest shows Rank IC = 0.08, t-stat = 1.4, 15 variants tested</input>
<thinking>Rank IC direction is fine, but t-stat of 1.4 doesn't clear a
2.0 threshold, and 15 variants tested with no multiple-testing
correction inflates the apparent significance further.</thinking>
<answer>{"passed": false, "flagged_issues": ["weak significance",
"multiple-testing not corrected for"], "escalate": true}</answer>
</example>
</examples>
```

This teaches the model *both* the desired reasoning pattern *and* the desired output format in one shot — few-shot and CoT reinforcing each other inside a structured skeleton.

---

## 5. Standard prompt architecture (the general recipe)

The ordering Anthropic guidance and P1-LA8 (context engineering) both point toward for a well-formed prompt:

| Order | Section | Purpose |
|---|---|---|
| 1 | Role / persona | Sets tone and scope — who is the model acting as |
| 2 | Task context / instructions | What to do, in explicit terms |
| 3 | Background data | The information the model needs to act on (large context goes here) |
| 4 | Examples | Few-shot demonstrations, ideally showing edge cases |
| 5 | Output format | Exact shape of the expected response |
| 6 | Reasoning instruction (if using manual CoT) | "Think through X, Y, Z before answering" |

**Placement detail:** when a prompt includes a very long data section (e.g., an entire trace log dump), current guidance recommends putting the actual task instructions *after* that long context rather than before — this measurably improves how well the model attends to the instructions, since instructions placed right before the response are freshest in the model's attention.

---

## 6. Where this lands in P1's actual build

| P1 component | Technique(s) it needs |
|---|---|
| Factor-spec extractor (natural language → structured spec) | Few-shot (disambiguating phrasing like "value trap") + structured output tags |
| Methodology validator (`ValidationResult`) | Guided/structured CoT (walk the Rank IC / t-stat / multiple-testing / beta-neutrality checklist before verdict) |
| Memo generator | Few-shot (house style/tone examples, per P1-LA16's "tone mismatch" scenario) + structured XML sections |
| Orchestrator / subagent instructions (P1-LA7) | Structured XML prompts, since multiple subagents need cleanly separated role/instructions/output-format blocks to avoid the confused-deputy risk from P1-LA10 |

None of this is new conceptual ground beyond what LA1-LA16 already established — this lesson is the "how to actually write it well" layer underneath everything already decided about prompting-first.

---

## Sources consulted

Current Anthropic prompt engineering documentation (Claude Platform Docs, "Prompting best practices" and "Use XML tags" pages) was checked via web search rather than relied on from memory, per standing practice for verifiable product-specific claims — specifically confirming: the 3-5 example recommendation for few-shot prompting, the "new employee with amnesia" framing for the model's lack of institutional context, the XML tagging recommendation and lack of a fixed canonical tag vocabulary, the three-level CoT framing (basic/guided/structured), and the nuance that extended thinking mode (an API-level reasoning capability) is generally preferable to hand-built CoT scaffolding when available, with manual `<thinking>` tag prompting positioned as the documented fallback for when thinking mode is off.

---

## Track status

**AI/Agentic concept track: 17/17 — COMPLETE.** (P1-LA1 through P1-LA17 all done.)

**Recommended next step:** Backtesting Rigor track (P1-LB1, P1-LB2, P1-LB3 — 0/3, not started) and Evals track (P1-LE1, P1-LE2 — 0/2, not started), before moving into Phase 2 (Architecture).
