# P1-LA16: Fine-Tuning vs. Prompting vs. Retrieval-Augmented Generation (RAG)

**Completed:** 2026-07-18
**Track:** AI/Agentic (16 of 17)
**Builds on:** P1-LA15 (RAG Fundamentals) — extends the "is this a knowledge-access problem?" diagnostic into a full three-way decision framework.

---

## 1. The three levers, in plain language

Think of a Large Language Model (LLM) as a new research analyst you've just hired. That analyst arrives with a huge amount of general knowledge and reasoning ability baked in from years of training (their "education"), but they don't know anything about *your* specific desk's conventions yet. There are three different ways to get them working the way you need:

| Lever | What you're actually doing | Trading-desk analogy |
|---|---|---|
| **Prompting** | Give instructions and examples *at the moment of the request*, every single time | Handing the analyst a briefing memo before every single meeting — "here's our house style, here's an example of the output format we want" |
| **Retrieval-Augmented Generation (RAG)** (see P1-LA15) | Give the analyst a searchable library they can look things up in at request-time | Giving the analyst real-time access to a document repository, so they can pull the actual 10-K filing instead of working from memory |
| **Fine-tuning** | Actually retrain the analyst — update what they *know how to do by default*, permanently, before any request ever comes in | Sending the analyst through an internal training program until the house style becomes second nature — you no longer need to remind them every time |

The critical distinction, and the one that trips people up: **prompting and RAG both leave the model's weights completely untouched.** Every technique covered so far — few-shot examples, context engineering (P1-LA8), tool use, RAG's retrieval step — all of it works by controlling what goes *into* the model's context window at request time. The model itself, the actual neural network, is identical before and after the request. Fine-tuning is the only one of the three that changes the model itself.

### What "the model itself" means, concretely

Recall from P1-LA15's follow-up discussion on the tokenization → embedding → transformer-layer → pooling pipeline: a transformer model's actual "intelligence" lives in the transformer layers step — enormous matrices of learned numbers (weights) that get multiplied against the input at every layer via self-attention and learned weight matrices. Those weight matrices are what turns raw token embeddings into contextualized, meaningful output, and they hold the large majority of a transformer model's total parameters and nearly all of its computation.

**Fine-tuning means running additional training — more backpropagation — on those exact weight matrices, using a custom dataset of examples specific to your task.** You're not adding text to a prompt. You're nudging millions or billions of numbers inside the network itself, so that the behavior you want happens *by default*, without you having to ask for it in the prompt every time.

### Follow-up clarification: training vs. inference (2026-07-18)

A follow-up question surfaced an important mix-up worth flagging explicitly, since it's the exact distinction fine-tuning depends on. The two phases:

| Phase | When it happens | What changes |
|---|---|---|
| **Training** | Once, before the model is ever deployed (and again, separately, during fine-tuning) | The weight matrices themselves get updated via backpropagation |
| **Inference** | Every single time a request is sent | Nothing in the model changes. The *fixed*, already-learned weights are applied to *that specific input* to compute a fresh, context-aware output |

The Step 3 transformer layers do **not** "adjust as part of learning" every time the model runs. They use fixed, already-trained attention weight matrices to look at every other token in a given input and compute a new contextualized vector for each token — a live *computation*, not a *learning* event. The weights doing that computing are frozen after training; only the computed output changes per input.

**Worked example — the token "bank":** Its Step 2 embedding (the raw lookup-table row) is an identical fixed vector regardless of sentence — it has no idea yet whether "bank" means a riverbank or a financial institution. Step 3 then produces a different contextualized output depending on the sentence: "I deposited cash at the bank" pulls the vector toward a financial-institution meaning (attention weighted in "deposited," "cash"); "We sat by the river bank" pulls it toward a riverbank meaning (attention weighted in "river"). Same starting point, different ending point — but the *weights* doing the pulling are identical, fixed numbers in both cases. Nothing about the model is "learning" differently between the two sentences; one fixed set of trained weights is being applied to two different inputs.

### Follow-up: full numeric walkthrough — token ID lookup vs. attention weights vs. fresh computation (2026-07-18)

A follow-up question asked for a fully concrete walkthrough distinguishing three specific terms — token ID lookup, attention weights, and "on-the-fly computation" — since the earlier explanation left them feeling conflated. Worked using the sentence **"The bank raised interest rates,"** with toy 3-dimensional vectors (same simplification style as P1-LA15's cosine-similarity example — real models use thousands of dimensions, but the mechanics are identical at any size).

**Step 1 — Tokenization:** "The" / "bank" / "raised" / "interest" / "rates" / "." (simplified to whole-word tokens for clarity).

**Step 2 — Token ID lookup: the static spreadsheet.**

| Token | Token ID (illustrative) | Initial embedding vector (fixed, looked up by ID) |
|---|---|---|
| "The" | 464 | [0.02, 0.01, 0.03] |
| **"bank"** | **2762** | **[0.10, 0.85, -0.30]** |
| "raised" | 8921 | [0.40, -0.10, 0.55] |
| "interest" | 3305 | [0.70, 0.05, 0.60] |
| "rates" | 6120 | [0.65, 0.02, 0.58] |
| "." | 13 | [0.00, 0.00, 0.00] |

Token ID 2762 always returns the exact same row for "bank," in any sentence. At this point the vector has no idea whether the sentence is about finance or a river — same blind, generic starting point either way.

**Step 3 — Attention weight matrices: the fixed formula, not a lookup.** The model also has weight matrices (Query, Key, Value — $W_Q$, $W_K$, $W_V$) learned once during training and now frozen. These are **not indexed by token ID** — there's no "give me the matrix for 'bank'" the way Step 2 works. The exact same matrices are applied to every token, in every sentence, regardless of what the token is. What they do: for "bank" at position 2, they compute how much attention to pay to every other token in the sentence, then blend those other tokens' vectors together, weighted by that attention, into a new vector for "bank."

| Other token | Attention weight to "bank" (illustrative — computed fresh for this specific sentence) |
|---|---|
| "The" | 0.05 |
| "raised" | 0.20 |
| "interest" | 0.40 |
| "rates" | 0.30 |
| "." | 0.05 |

"Interest" and "rates" get the heaviest weight — the fixed formula, applied to this specific sentence, decides those are the most relevant neighbors for disambiguating "bank."

**Step 4 — the new, contextualized vector, computed fresh, right now.** Blending "bank"'s original vector with its weighted neighbors produces something like [0.10, 0.85, -0.30] → [0.72, 0.18, 0.20] — shifted toward the "financial institution" region of vector-space, because "interest" and "rates" pulled it there.

**Contrast with "I sat by the river bank":**

| Step | Same as the finance sentence? |
|---|---|
| Step 2: initial embedding for "bank" | **Identical** — [0.10, 0.85, -0.30], same lookup, same row |
| Step 3: attention weight matrices themselves | **Identical** — the exact same frozen $W_Q, W_K, W_V$ |
| Attention weights *computed* for this sentence | **Different** — "river" and "sat" get the heavy weight, not "interest"/"rates" |
| Step 4: resulting contextualized vector | **Different** — shifts toward "geographic feature," something like [0.04, 0.91, -0.55] |

**Full summary table:**

| Term | What it is | Fixed, or computed fresh? | Changes across the two example sentences? |
|---|---|---|---|
| Token ID | An index number for a word/subword | Fixed (assigned once, part of the vocabulary) | No — "bank" is always ID 2762 |
| Initial embedding vector (Step 2) | The row returned by looking up that ID | Fixed — same answer every time, literal lookup | No — identical in both sentences |
| Attention weight matrices ($W_Q, W_K, W_V$) | The formula/matrices themselves, learned during training | Fixed — frozen after training, never touched at inference | No — identical matrices used in both sentences |
| Attention weights (how much focus on each neighboring token) | The *output* of applying those fixed matrices to this specific input | Computed fresh, every single time, because it depends on which tokens are actually present | Yes — completely different in "interest rates" vs. "river bank" |
| Final contextualized vector for "bank" | The blended result after attention | Computed fresh, every single time | Yes — ends up in a different region of vector-space each time |

**The one-sentence version:** the *tools* (token ID table, attention matrices) never change. What changes, every single time a sentence is sent to the model, is the *output* of running those fixed tools against that sentence's specific set of tokens.

**Why this matters for the fine-tuning vs. prompting/RAG distinction:** every ordinary inference call — no matter how contextual the output looks — runs on frozen weights. Prompting and RAG feed different *inputs* into that same frozen machinery. Fine-tuning is the one process that goes back and changes the machinery itself, via a separate training run.

| | Prompting / RAG | Fine-tuning |
|---|---|---|
| What changes | The *input* (context window) | The *model's weights* |
| When it changes | Fresh, every single request | Once, in a training run, before deployment |
| Where the "knowledge" lives | In the prompt/retrieved docs, temporary | Baked into the network, permanent (until retrained) |
| Analyst analogy | Reminded every meeting | Retrained until it's habit |

---

## 2. The diagnostic question: what kind of problem do you actually have?

P1-LA15 introduced the question "is this really a knowledge-access problem?" as the test for whether RAG applies. This lesson extends that into a three-way diagnostic. Before reaching for any of these three tools, ask what *kind* of gap you're actually trying to close:

| Kind of gap | Diagnostic question | Right tool |
|---|---|---|
| **Knowledge-access problem** | "Does the model not *know* a specific fact, or does that fact change over time / is it too obscure to have been in training data?" | **RAG** — give it a lookup mechanism |
| **Behavior / style / format problem** | "Does the model know how to do this in principle, but isn't doing it in *my* preferred way — wrong tone, wrong output structure, missing a step I want every time?" | **Prompting first.** Only escalate to fine-tuning if prompting genuinely can't fix it at the volume/consistency needed |
| **Capability / reasoning problem** | "Is the model actually failing to reason correctly about something, regardless of how it's asked or what it's given to read?" | **Usually none of the three.** This is a "pick a smarter/bigger base model" problem, not a prompting/RAG/fine-tuning problem |

This third row is worth sitting with, because it's the trap people fall into: assuming fine-tuning can fix a model that's fundamentally not smart enough for a task. It can't — fine-tuning teaches a model a *pattern of behavior* from examples, it doesn't add reasoning capacity it doesn't already have. If the base model genuinely can't reason through a factor-construction edge case no matter how it's prompted, the fix is a better model or a decomposed workflow (e.g., breaking the task into smaller tool-use steps), not fine-tuning.

### Follow-up clarification: what "smart enough" actually means, and how to test for it (2026-07-18)

A follow-up question surfaced how to concretely answer, e.g., "is Sonnet 5 smart enough for financial services but not healthcare (or vice versa)?" This is worth capturing in full since it directly extends the capability-gap row above and previews the upcoming Evals track.

**Core reframe:** "smart enough" is not a single intelligence dial a model either clears or doesn't. It's a function of how well the reasoning patterns needed for a given task were represented in the model's training data, combined with how much precise multi-step reasoning the task demands. A model isn't globally smart or dumb — its competence is an uneven landscape shaped by domain, not one number.

**The only real way to answer the question: domain-specific evals, not intuition.** This is literally what a **model eval** is for (as distinct from a **system eval**, which tests whether your specific pipeline/prompts/tools work) — this exact question is the subject of the upcoming P1-LE1 lesson (model evals vs. system evals).

| | What it tests | Example |
|---|---|---|
| Model eval | Raw capability of the base model itself, domain by domain | Does Sonnet 5 correctly answer 200 held-out clinical reasoning questions vs. 200 held-out financial-statement-analysis questions? |
| System eval | Whether the specific product (prompts + tools + retrieval) works end-to-end | Does the factor-spec extractor correctly parse 200 real user hypotheses? |

**Before concluding "not smart enough," rule out the other two explanations first** — a knowledge gap and a behavior/prompting gap both look identical to a capability gap from the outside (wrong answer either way), but have completely different fixes:

| Step | Test | If this fixes the failure | If it doesn't |
|---|---|---|---|
| 1. Rule out knowledge gap | Hand the model the correct facts directly in context | Not capability — it was a knowledge-access problem, fix with RAG | Move to step 2 |
| 2. Rule out behavior/prompting gap | Rewrite the prompt with clearer instructions and strong few-shot examples | Not capability — it was a behavior problem, fix with prompting | Move to step 3 |
| 3. Test actual reasoning | With correct facts *and* a well-crafted prompt, does the model still get the underlying logic/reasoning steps wrong? | — | Genuine capability gap — needs a different/bigger model or a decomposed workflow |

Only failures that survive both of the first two tests count as real evidence of a capability gap.

**Worked illustrative shape (not a real result — no eval was actually run, and no specific claim about Sonnet 5's real comparative performance is being made):** running the same model against a 200-question healthcare eval and a 200-question financial-services eval, with facts and prompting controlled for in both, might show something like 92% accuracy on healthcare with mostly close-but-slightly-off misses, versus 68% accuracy on financial services with misses showing confidently-wrong multi-step arithmetic rather than near-misses. That *shape* — high accuracy with graceful near-misses in one domain vs. lower accuracy with confidently-wrong multi-step reasoning in another, after controlling for facts and prompting — is what real evidence of "not smart enough for X" would look like. The numbers above are illustrative of the analysis shape only.

**Why capability plausibly varies by domain (a hypothesis, not an asserted fact about any specific model):** domains with dense, well-structured public training material (e.g., large public corpora of textbooks and licensing-exam question banks) are plausibly better-represented than domains requiring very specific, less-standardized multi-step numeric reasoning conventions (e.g., a particular firm's backtesting methodology). This is exactly the kind of claim that should be tested via eval, not assumed — the eval is the source of truth, not the guess.

---

## 3. Why fine-tuning is rarely the first move in practice

Four reasons, each mapping to a real cost that would have to be justified:

### a) Data requirements
Fine-tuning needs a real dataset of high-quality input→output examples — typically hundreds to thousands, sometimes more, depending on how narrow and consistent the target behavior is. Prompting needs zero to a handful of examples (few-shot). A fine-tuning-sized dataset almost never exists at the moment a problem is first noticed — it has to be deliberately built, by hand or mined from production logs over time.

### b) Iteration speed
If a prompt isn't working, you edit it and re-run — seconds to minutes. If a fine-tuned model isn't working, you have to curate more/better data, re-run a training job, re-evaluate, and re-deploy — hours to days, and each cycle costs real money (training compute, not just inference).

### c) Maintainability
A prompt lives in the codebase as plain text — anyone on a team can read it, review it in a pull request, and understand exactly why the model does what it does. A fine-tuned model's new behavior is baked into weights nobody can directly inspect. If the underlying base model gets upgraded (e.g., a move from one model generation to the next), the entire fine-tuning run may need to be redone from scratch on the new base model. A prompt usually just keeps working, at most needing minor tweaks.

### d) Cost — see the worked numerical example in Section 4 below.

**The practical decision rule:** exhaust prompting (and RAG, if it's a knowledge problem) first; only fine-tune when there is (1) a real, recurring, well-defined behavior gap, (2) demonstrated failure of prompting to close it even after real effort, and (3) sufficient volume of training data available or buildable.

---

## 4. Worked numerical example: the cost tradeoff, concretely

Applied to a live P1 scenario: **the factor-spec extractor keeps missing a specific phrasing pattern** (e.g., a user says "value trap avoidance" and the extractor doesn't map it correctly to a value-factor-with-quality-filter spec).

### Fix option A: Add few-shot examples to the prompt

Adding 4 worked examples of tricky phrasing → correct spec mapping, adding roughly 600 tokens to every extractor call.

Current Claude API pricing (Sonnet tier, standard rate as of mid-2026, confirmed via web search rather than assumed from memory): **$3 per million input tokens.**

| Item | Value |
|---|---|
| Extra tokens per call (few-shot examples) | 600 tokens |
| Cost per million input tokens | $3.00 |
| Extra cost per call | 600 / 1,000,000 × $3.00 = **$0.0018** |
| Calls per day (illustrative, dev/demo scale) | 50 |
| Extra cost per day | 50 × $0.0018 = **$0.09** |
| Extra cost per month | ~**$2.70** |

Total cost of Option A: under $3/month at this scale, deployable in minutes, fully reversible if it doesn't work (just edit the prompt back).

### Fix option B: Fine-tune the model on the phrasing pattern

| Item | Value |
|---|---|
| Training examples needed (rough floor for a narrow behavior fix) | ~200-500 curated examples |
| Time to curate/label those examples by hand | Many hours, possibly days |
| Training job cost | A one-time compute charge (varies by provider/model — meaningfully more than a few dollars) |
| Ongoing cost | Removes the 600 extra prompt tokens per call, but requires enormous call volume for that per-call savings to outweigh the upfront data + training cost |
| Iteration cost if it doesn't work | Full cycle repeats: re-curate data, re-run training, re-evaluate |
| Fragility | Must be redone if the base model is switched |

**Break-even framing:** if Option A costs ~$0.0018/call in extra tokens and Option B costs a conservative $50 one-time setup cost in compute alone (ignoring the larger real cost of data-curation labor), roughly 50 / 0.0018 ≈ **27,800 calls** would be needed before fine-tuning even pays back its setup cost in token savings alone. At P1's dev/demo scale (tens of calls a day), reaching that break-even would take **years** of steady-state volume. This is why fine-tuning is a production-scale, high-volume decision, not a "the prompt isn't perfect yet" decision.

*Note on the numbers: the $3/million input token rate reflects current published Sonnet-tier pricing as of this session (confirmed via web search, not assumed from training data, since pricing changes over time). The fine-tuning compute cost above is an illustrative order-of-magnitude figure, not a quoted number from any specific provider — actual fine-tuning cost depends heavily on model, provider, and dataset size.*

---

## 5. Decision framework table

| Dimension | Prompting | RAG | Fine-tuning |
|---|---|---|---|
| **Best for** | Behavior, style, format, one-off logic changes | Knowledge that's current, obscure, or proprietary (docs, filings, internal wikis) | Deeply ingrained, high-volume, narrow behavior patterns that prompting can't reliably fix |
| **Data needed** | 0-10 examples | A document corpus (any size) | Hundreds-thousands of labeled examples |
| **Setup cost** | Minutes | Hours-days (build the retrieval pipeline once — see P1-LA15) | Days-weeks (curate data, run training, evaluate) |
| **Iteration speed** | Seconds-minutes | Fast for new docs; pipeline itself is stable | Slow — full retrain cycle |
| **Per-call marginal cost** | Slightly higher (extra prompt tokens) | Retrieval latency + slightly higher tokens (P1-LA15) | Lower per-call (no extra prompt tokens) *if* volume justifies it |
| **Transparency/auditability** | High — plain text, reviewable | High — exact retrieved content is visible | Low — behavior is baked into opaque weights |
| **Fragility to model upgrades** | Low — mostly still works | Low — retrieval pipeline is model-agnostic | High — may need full retrain on new base model |
| **First move?** | **Yes, almost always** | Yes, if it's genuinely a knowledge-access gap | **No** — last resort after prompting/RAG demonstrably fail |

---

## 6. What would have to be true for fine-tuning to become the right call for P1

The honest bar Project 1 would need to clear before fine-tuning became justified rather than premature:

1. **A specific, recurring behavior gap** that shows up consistently across many real production calls — not a one-off noticed once or twice while testing.
2. **Demonstrated, documented failure of prompting** to fix it — meaning several rounds of prompt iteration (including few-shot examples) were tried and the failure rate stayed unacceptably high.
3. **A real dataset** of hundreds of labeled correct examples, either hand-curated or mined from eval/trace logs — this connects directly to P1-LA12's observability work, since the `TraceEvent` logs are exactly the kind of data that would be mined for this.
4. **Enough call volume** that the per-call savings (no extra prompt tokens) would plausibly repay the training cost within a reasonable time horizon — per the worked example above, a high bar at portfolio-project scale.

None of P1's 13 build sprints currently meet this bar. This is consistent with P1-LA15's conclusion about RAG: both fine-tuning and RAG are "understood as mechanisms, available if a genuine need surfaces, not built into current scope."

---

## 7. Deliverable: one-page decision-framework note applied to P1 scenarios

### Scenario 1: "The factor-spec extractor keeps missing a specific phrasing pattern"
- **Diagnosis:** Behavior/format problem — the model can do this in principle, it's just not consistently following the mapping convention.
- **Right tool:** Prompting (few-shot examples showing the tricky phrasing → correct spec mapping).
- **Why not fine-tuning:** No demonstrated failure of prompting yet; call volume is far too low to justify the setup cost (see Section 4 worked example).
- **Escalation trigger:** If, after adding targeted few-shot examples, the eval suite (P1-LE1/LE2, once built) still shows a persistent failure rate on this pattern across a large, real call volume — revisit.

### Scenario 2: "The memo generator's tone doesn't match a target house style"
- **Diagnosis:** Behavior/style problem — not a knowledge gap. The model knows how to write in different tones; it just needs to be told which one.
- **Right tool:** Prompting (a style guide + 1-2 example memos in the target tone, injected via context engineering per P1-LA8).
- **Why not fine-tuning:** Style matching via prompting is one of the best-established, cheapest use cases for prompting; there is no realistic scenario where P1's scale would justify fine-tuning for this.

### Scenario 3 (hypothetical, used to stress-test the diagnostic): "The memo generator needs to cite specific academic factor-research papers by name and page"
- **Diagnosis:** Knowledge-access problem — this is exactly the scenario flagged in P1-LA15 as a legitimate *future* RAG use case (the model doesn't reliably know specific paper citations from training data alone, and that's not something prompting can fix by itself).
- **Right tool:** RAG — index the papers, retrieve relevant chunks at generation time.
- **Why not fine-tuning:** Fine-tuning doesn't give a model new facts reliably or update-ably; it's the wrong tool for "look up something specific and current." RAG is designed exactly for this.

### Scenario 4 (real-world, not hypothetical — validation of the diagnostic outside P1): An Azure AI Search-based investment research chat app, with proprietary content vectorized ahead of time and stored in an Azure AI Index, queried via hybrid search (vector + semantic)
- **Diagnosis:** Textbook RAG — every step (vectorize → index → hybrid search at query time → inject into context → generate) maps directly onto the Phase A/Phase B pipeline in P1-LA15 Section 3.
- **Terminology check:** "Grounding" is not a competing label for a different pattern — it's the goal RAG serves, and in Microsoft's own Azure documentation, "grounding data" specifically means the retrieved content itself, once pulled from the index. See P1-LA15's Follow-up Q7 for the full applied write-up, including the Microsoft-documentation citation.
- **Why not fine-tuning:** No step in this setup touches the LLM's weights — vectorizing, indexing, and retrieving all operate on the *input* side, not the model itself.

### Scenario 5 (real-world, not hypothetical — validation of the diagnostic in the opposite direction): Uploading a single one-or-two-page resume directly into a Claude chat window and asking questions against that one file only
- **Diagnosis:** Not RAG. The file is small enough to fit entirely inside the context window, so there's no need for a search/retrieval step to select "relevant" pieces — the whole document is simply read in full every time. This is the other branch of the same diagnostic: RAG solves the problem of a corpus too large to hand the model in full; a one-page resume isn't that problem.
- **Confirmed against Claude's own official documentation** (not assumed): direct chat uploads, and even Claude Projects below a certain knowledge-volume threshold, load full documents into context rather than retrieving from them. RAG mode in Projects activates automatically only once total project knowledge approaches or exceeds the context window limit. Full applied write-up in P1-LA15's Follow-up Q8.
- **Why this matters:** it's a useful reminder that RAG is a solution to a *scale* problem, not a general-purpose "the model is reading a document" pattern — plenty of document-reading tasks never need retrieval at all.

---

## Summary — the one-sentence diagnostic to carry into interviews

*"Is this a knowledge problem (→ RAG), a behavior problem (→ prompting, escalate to fine-tuning only under real sustained volume), or a capability problem (→ neither — you need a different model)?"*

---

## Connections to prior lessons

- **P1-LA8 (Context engineering):** Prompting-based fixes (few-shot examples, style guides) are applications of context engineering — controlling what goes into the context window, not changing the model.
- **P1-LA12 (Observability & tracing):** The `TraceEvent` schema and correlation-ID logging discipline are exactly the mechanism that would generate the labeled dataset needed if fine-tuning ever became justified — trace logs of failures are raw material for training examples.
- **P1-LA15 (RAG fundamentals):** This lesson directly extends LA15's closing diagnostic question ("is this really a knowledge-access problem?") into a full three-way framework covering behavior and capability problems as well.

---

## Decision logged

No fine-tuning added to Project 1's build scope. Fine-tuning is understood as a mechanism and a decision framework, available if a genuine, high-volume, well-documented behavior gap emerges after prompting has demonstrably failed — not built into P1's active 13-sprint build plan. Revisit only if a concrete need surfaces, following the same posture already established for RAG in P1-LA15.

**Estimated time spent:** 1-2 hours
