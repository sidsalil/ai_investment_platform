# P1-LB3: The Multiple-Testing Problem (p-hacking)

**Track:** Backtesting Rigor (3 of 3 — track complete)
**Date:** 2026-07-18
**Estimated time:** 1-2 hours

---

## 0. Start here — the version that actually landed (read this first)

**Why you should care, for Project 1, in one paragraph:**

Your methodology validator (P1-Build-8) has to be able to catch cherry-picked results — not just yours, but eventually anyone's who uses this tool. If someone tests 15 versions of a factor and reports "my Value factor has an IC of 0.06!" without saying they tried 14 other versions first, that number is basically meaningless — it's not that they lied, it's that "the best of 15 tries" and "the result of one honest try" look identical on paper but mean completely different things. If your validator can't tell those two apart, it's not actually validating anything. That's the entire point of this lesson: **build a validator that asks "how many things did you try before landing on this number?"** — because that question is the difference between a credible research process and a lucky guess dressed up as a discovery.

**The walkthrough, using your actual plan, no abstract math:**

You're building a Value factor and a Momentum factor for NASDAQ-100. Say during development you get impatient with just one version of Value and decide to try a few lookback windows to see which "works best":

| What you try | Backtest Rank IC you get |
|---|---|
| Value using P/E ratio | 0.021 |
| Value using P/B ratio | 0.019 |
| Value using P/E, 6-month lookback | 0.024 |
| Value using P/E, 12-month lookback | 0.033 |
| Value using P/E, 18-month lookback | 0.017 |

You look at that table and think: "great, the 12-month P/E version is my Value factor — 0.033 IC, best of the bunch." **That's the exact move that's dishonest, even though every single one of those five backtests was run correctly, with no look-ahead bias, on properly out-of-sample data.**

Here's why: if Value has zero real predictive power at all — total coin-flip noise — and you try 5 random variations, it's not unlikely that *one* of the 5 comes out looking good just from random luck, the same way if you flip 5 coins ten times each, one of them will probably come up heads more than the others by chance. You didn't do anything wrong in your backtests. The problem is you tried 5 things and only told your boss/interviewer about the one that won.

**The fix isn't complicated in practice, even though the math behind it (Bonferroni/FDR) can look intimidating:** it comes down to two honest options —

1. **Tell people how many variants you tried.** "I tested 5 lookback windows for Value; the 12-month version had the best IC (0.033), but here's all 5 numbers, not just the winner." That single sentence is 90% of the fix.
2. **Only trust the number you get on data you haven't touched yet.** If you pick the 12-month winner during development, then check it *once* against your held-out S&P 500 test period (the thing you already locked in P1-LB2), and it holds up around 0.033 there too — now you have real evidence, because that final check couldn't have been influenced by which of the 5 you picked.

That's genuinely it. Everything else in this lesson (Bonferroni, FDR, Deflated Sharpe, Harvey-Liu-Zhu, sections 2-8 below) is just "here's how statisticians formalize disclosure option #1 with actual numbers" — useful for an interview if someone asks "how do you correct for multiple testing," but not something you need to internalize deeply to build this correctly. Your validator's actual job is dead simple: **did they disclose the search, and did they check the winner against untouched data?** If yes to both, pass. If no, flag it.

### Where the "luck" is actually coming from (the part that felt most counterintuitive)

The problem isn't "trying more than once" in general — engineers iterate on prototypes constantly against fresh, independent reality (gravity doesn't get "used up" by the 10th test). The problem is specific to backtesting: **you only have one fixed, finite slice of market history (e.g., NASDAQ-100 2015-2021), and every variant you test gets scored against that exact same slice, not a fresh independent one.**

That one slice of history had its own specific, unrepeatable sequence of events — which stocks happened to rally, which sectors happened to rotate. Any factor variant, even a completely fake, meaningless one, will show *some* correlation with that specific sequence just by coincidence — the same way flipping a fair coin 10 times might randomly produce 7 heads even though the coin has no bias. That 7/10 isn't "the coin's true nature," it's noise from that one specific run.

Illustrating with the table above — every variant given the *same* true underlying skill on purpose, differing only in how that one slice's noise happened to interact with each variant's mechanics:

| Variant | True skill (illustrative, unknowable in practice) | Luck from this one historical slice | What you measure |
|---|---|---|---|
| P/E | 0.020 | +0.001 | 0.021 |
| P/B | 0.020 | −0.001 | 0.019 |
| P/E, 6mo | 0.020 | +0.004 | 0.024 |
| P/E, 12mo | 0.020 | +0.013 | 0.033 |
| P/E, 18mo | 0.020 | −0.003 | 0.017 |

The 12-month version isn't better — its noise just happened to line up favorably with that particular slice of history. Re-run the same experiment on 2010-2016 instead, and a different variant would probably "win," for the same non-reason. **Picking "the best one" selects for (skill + whichever variant's noise happened to line up best with this one fixed dataset) — not for skill alone.** The more variants tested against that same fixed slice, the more chances noise gets to produce an impressive-looking winner with nothing to do with real predictive power.

**Does more history fix this?** It shrinks the problem but doesn't eliminate it. More history is like a bigger opinion poll — it narrows how much any one variant's IC can be pushed around by noise (illustrative: 3 years of data → true IC ± 0.015 possible noise; 15 years → ± 0.006; full history since 1985 → ± 0.003). But even with a tiny noise range, the *maximum* of several noisy draws is still mathematically expected to land above the true average — smaller noise shrinks the size of the inflation, it doesn't zero it out. Worse: using the *entire* available history to pick a winner also destroys your only real defense, because there's no untouched holdout left to check the winner against afterward (the thing locked in P1-LB2). Trading "some inflation, but a fresh holdout to verify against" for "less inflation, but zero ability to verify" is a worse trade, not a better one.

**Does this mean quant shops shouldn't iterate and refine?** No — refining is fine and expected. The dishonest move specifically is: iterating against the *same fixed historical sample*, then reporting the winner's number *as if only one thing had ever been tried*. The honest version: iterate freely during development (that's what the validation set is for, per P1-LB2's three-way split), then check the winner exactly once against a slice of history that had zero influence on which variant you picked — or, if no fresh holdout is available, explicitly disclose and mathematically discount the reported number for how many things were tried (the Bonferroni/FDR machinery below).

### Why this is different from ordinary iteration (e.g., refining a PRD 15 times)

Iterating on a PRD 15 times before shipping it to your dev team is **not** multiple testing, and doesn't need any correction. The distinction:

| | Factor testing (the bad case) | PRD iteration (fine, no correction needed) |
|---|---|---|
| **What changes between attempts** | Nothing about reality changes — you're re-scoring different variants against the *same fixed slice of the past* | The document itself changes each round, based on real, specific feedback |
| **What "improves" the score** | Coincidence — whether a variant's mechanics happened to line up with that historical noise | Actual information — a stakeholder told you requirement #4 was ambiguous, so you fixed it |
| **Is there a "true" hidden target being converged toward?** | No — there's no such thing as "the true PRD"; each version is genuinely, verifiably better at communicating intent | N/A — this framing doesn't apply |
| **Would repeating the process from scratch tend to land on the same answer?** | No — a different historical period would likely crown a different "winning" variant | Yes — starting over with the same feedback would converge to something close to the same final PRD, because you're following real signal, not noise |

Technical framing: the PRD process is **convergent optimization** — each round uses real information to close a real gap (like Newton's method walking toward a root using the actual slope at each step). Factor-testing-gone-wrong is **repeated blind draws against a fixed random yardstick** — closer to buying 15 lottery tickets and reporting only the number on the winning one, as if it told you something about your ticket-picking skill.

The bad version of "iteration" would be: writing 15 unrelated draft PRDs with no changes in between, showing all 15 to the same five stakeholders in one sitting, picking whichever got the best gut-reaction that day, and telling your VP "this PRD tested great with stakeholders" without mentioning the other 14 scored lower in the same sitting. That's the analogous move — re-querying a fixed, noisy judge (five people's one-time reaction) and reporting only the winner.

**The line, restated:** it isn't "how many times did you try." It's "is the scoring mechanism you're optimizing against fixed and noisy enough that trying more times can produce a fake winner by pure chance, and did you disclose how many shots you took." Real engineering iteration (PRDs, code, most product work) is usually convergent — each round uses real signal. Backtesting against one finite slice of market history specifically is not, because market history doesn't hand you fresh, independent information each time you re-query it.

---

## 1. The intuition, before any formula (original framing, kept for reference)

If you interview enough candidates, one of them will happen to nail every question — including the ones where they got lucky, not the ones where they're actually the strongest hire. The more candidates you interview, the more likely it is that *pure luck* produces at least one dazzling interview, even if every candidate has identical true ability. If you then hire that one person and tell your boss "I found the best candidate," you're not lying about the interview — you're lying about what the interview *proves*. A great interview from person #47 out of 50 candidates is much weaker evidence of skill than a great interview from person #1 out of 1 candidate, even though the interview itself looked identical.

**Multiple testing** is the finance/statistics name for this exact problem: when you evaluate many things and then report only the one that looked best, the "best" result is inflated by luck, not just skill — and the more things you tested, the bigger that inflation gets.

This is different from a single backtest being wrong. Every individual test you ran might be completely honest, uncontaminated by look-ahead bias (P1-LB1), and properly out-of-sample (P1-LB2). The dishonesty creeps in at a different layer: **the act of searching across many candidates and reporting only the winner, without disclosing the search.**

You already met a bite-sized version of this in P1-LB2: the "winner's curse" table, where three honestly-validated factor variants had identical true skill (0.040) but different backtest-period luck (+0.005, +0.001, +0.008), and picking the best-looking one (0.048) overstated the truth. P1-LB3 formalizes *why* that happens and gives you the standard tools finance and statistics use to correct for it.

---

## 2. The formal concept: false positives multiply with the number of tests

**p-value** — a p-value answers: "If there were actually no real skill/edge here (pure noise), what's the probability I'd see a result this good or better, just by chance?" A p-value of 0.05 means "a result this strong would happen by chance 5% of the time even with zero real skill." The conventional cutoff for calling something "statistically significant" is p < 0.05 — i.e., "this is unlikely enough to be chance that I'll treat it as real."

**The problem:** that 5% threshold is calibrated for testing *one* thing. It quietly breaks down when you test many things and report only the best one.

### Follow-up: is a smaller p-value always more desirable?

Yes, with a caveat. **Smaller p-value = stronger evidence against "this is just noise."** In the context of a single, honest test, a smaller p-value is better — it means the result observed would be rarer under the "no real effect" assumption, which is stronger evidence the effect is real. But two things temper "smaller is always better":

| Point | Why it matters |
|---|---|
| A tiny p-value isn't the same as a large or useful effect | You can get p = 0.0001 on a factor with a Rank IC of 0.01 (statistically real, but too weak to trade on) just by using a huge sample. Statistical significance and economic/practical significance are different questions — this is why the locked metrics decision pairs IC with IR and a full-window t-stat, not just a p-value in isolation. |
| This is exactly where multiple testing bites | If you go looking across many variants for the smallest p-value you can find, a small p-value stops being trustworthy evidence — it might just be the one that won the "luck lottery" among everything tried. At n=15 tests, there's already a 53.7% chance *something* shows p < 0.05 purely by chance (see worked table below). So "smaller p-value" is only good evidence when you know how many things were tested to find it. |

So the honest version: **a smaller p-value is desirable, conditional on it being either (a) from a single pre-specified test, or (b) corrected for however many tests were actually run** (Bonferroni/FDR, both covered below). An uncorrected small p-value fished out of a big batch of trials is not the reassurance it looks like.

### Follow-up: where does α (alpha) come from, if we're dealing with p-values?

These are two different things that are easy to conflate.

| Term | What it is | Who sets it / where it comes from |
|---|---|---|
| **α (alpha)** | The threshold decided **in advance** — the predetermined tolerance for false positives. "I will only call something significant if the p-value is below this line." | **Chosen before running the test.** By convention, most fields default to α = 0.05, but it's a decision, not a measurement. |
| **p-value** | The thing **computed after running the test**, from the actual data. "Given the data observed, here's the probability of seeing a result this extreme if there were truly no effect." | **The data produces it.** Not chosen — it falls out of the sample and the test statistic. |

The relationship: pick α first (the bar), then compute the p-value from the backtest (the result), then compare — **if p < α, call it "significant."**

Concretely, in the factor research case:
- **α = 0.05** is deciding in advance: "I'm willing to accept a 5% chance of falsely calling a factor real when it isn't."
- The **p-value** is what comes out of a specific factor's IC test on actual NASDAQ-100 data — say the test produces p = 0.03.
- Since 0.03 < 0.05, that factor clears the bar and gets called "significant."

Why α shows up in the multiple-testing formula (below) specifically: the FWER formula `1 - (1-α)^n` asks "given the bar set (α) and the number of tests run (n), what's the chance at least one clears that bar by pure luck?" It's a question about the *threshold* and the *test count* — the actual p-values from the data don't enter that particular formula at all. That formula tells you how worried to be *before* even looking at results; the p-values are what come out *after*.

One more precision point: **Bonferroni doesn't touch the p-values** — it adjusts α downward (α/n) so that whatever p-values do come out face a harder bar. FDR/Benjamini-Hochberg, by contrast, *does* work directly with the sorted p-values, comparing each one to a rank-dependent threshold (see worked example below). So alpha and the p-value interact, but they're not the same lever.

**Family-wise error rate (FWER)** — the probability that *at least one* of your multiple tests shows a "significant" result purely by chance, even though nothing you tested is actually real. This is the number that matters when you're going to pick the best-looking test out of a batch and report it.

### The formula

If you run **n** independent tests, each with a false-positive rate of α (alpha, e.g., 0.05), the probability that *at least one* shows a false "significant" result by chance is:

$$
P(\text{at least one false positive}) = 1 - (1-\alpha)^n
$$

This is not additive (it's *not* just n × 0.05) — it compounds, because each test independently gets its own 95% chance of correctly showing "nothing here," and you're asking about the chance that *all* of them correctly show nothing.

### Worked numerical example — factor research context

Suppose you're testing factor variants (different combinations of value, momentum, quality, and lookback windows) with no real edge in any of them, α = 0.05:

| Number of variants tested (n) | Calculation | P(at least one false "significant" result) |
|---|---|---|
| 1 | 1 − (0.95)¹ | 5.0% |
| 5 | 1 − (0.95)⁵ | 22.6% |
| 10 | 1 − (0.95)¹⁰ | 40.1% |
| 15 | 1 − (0.95)¹⁵ | 53.7% |
| 20 | 1 − (0.95)²⁰ | 64.2% |
| 50 | 1 − (0.95)⁵⁰ | 92.3% |

At n=15 (a realistic count if you tried 3 base factors × 5 lookback windows each): even if **none of the 15 variants have any real predictive power at all**, there's a 53.7% chance at least one of them clears the "statistically significant" bar purely from noise. If you then report that one variant as your discovery, you've p-hacked — even if you never touched the math, never peeked at the test set (P1-LB2), and did everything else honestly.

This is why "I tested momentum, volatility, and value — why can't I just report whichever had the best backtest?" is the wrong question. The answer: because "whichever had the best backtest" is a biased selection process, and the bias grows mechanically with how many things you tried, independent of whether any of them are actually good.

---

## 3. Correction approach #1: Bonferroni correction (simple, conservative)

**Intuition:** if testing n things inflates your false-positive rate, shrink the bar for "significant" proportionally to how many things you tested. Make each individual test harder to pass, so that the *combined* chance of a false positive across all of them stays at your original 5%.

**Formula:**

$$
\alpha_{\text{adjusted}} = \frac{\alpha}{n}
$$

### Worked example

| Scenario | α (original) | n (tests) | α_adjusted (Bonferroni) | Practical meaning |
|---|---|---|---|---|
| Testing 1 factor variant | 0.05 | 1 | 0.05 | No change — original bar |
| Testing 5 variants | 0.05 | 5 | 0.01 | Each test now needs p < 0.01 to count |
| Testing 15 variants | 0.05 | 15 | 0.0033 | Each test now needs p < 0.0033 to count |
| Testing 50 variants | 0.05 | 50 | 0.001 | Each test now needs p < 0.001 to count |

Bonferroni is simple and widely understood, but it's known to be **overly conservative** — it treats every test as if it needs to survive the harshest possible correction, which means real, genuine effects can get thrown out as "not significant" once you're testing dozens of things. In factor research specifically, this matters: you'd rather not discard a genuinely good factor just because you tested it alongside 40 other variants.

---

## 4. Correction approach #2: False Discovery Rate (FDR) — less conservative

**Intuition:** instead of controlling "the chance of even one false positive across the whole batch" (Bonferroni's very strict goal), control **the expected proportion of your reported "significant" results that are actually false positives**. This lets you accept more discoveries at the cost of tolerating a controlled, known rate of mistakes among them — the same trade-off a portfolio manager makes when accepting some position sizing risk in exchange for expected return, rather than demanding zero risk.

**Benjamini-Hochberg procedure (the standard FDR method), in words:**
1. Run all n tests, get n p-values.
2. Sort them from smallest (best-looking) to largest.
3. Rank them 1 through n.
4. For each ranked p-value, check: is p ≤ (rank / n) × α?
5. Find the *largest* rank where this is true — call everything at or better than that rank a real "discovery." Everything past it gets discarded.

### Worked example

10 factor variants tested, p-values sorted, α = 0.05:

| Rank (k) | p-value | Threshold: (k/10) × 0.05 | Passes? |
|---|---|---|---|
| 1 | 0.001 | 0.005 | Yes |
| 2 | 0.004 | 0.010 | Yes |
| 3 | 0.011 | 0.015 | Yes |
| 4 | 0.018 | 0.020 | Yes |
| 5 | 0.044 | 0.025 | No |
| 6 | 0.060 | 0.030 | No |
| 7-10 | (higher) | (higher) | No |

Rule: find the *last* rank (largest k) where p ≤ threshold, then keep everything up to and including that rank. Here, rank 4 is the last one that passes (rank 5 fails even though its raw p-value of 0.044 would individually have passed the naive α = 0.05 bar). So variants ranked 1-4 are treated as real discoveries; 5-10 are discarded.

Compare to Bonferroni on the same data: Bonferroni's adjusted threshold would be 0.05/10 = 0.005 for *every* test — only rank 1 (p=0.001) would survive. FDR is visibly less conservative, which is why it's the more commonly used approach in fields (genomics, and increasingly factor research) where you're screening large batches of candidates and don't want to throw away everything real along with everything fake.

---

## 5. Correction approach #3: finance-specific tools

**Deflated Sharpe Ratio (DSR)** — developed by Bailey and López de Prado. Intuition: instead of adjusting your significance threshold, directly **shrink your headline performance metric** (Sharpe ratio, or in your case Rank IC) downward, based on (a) how many strategy variants you tried, (b) how much variance there was across those trials (a wide spread across trials signals more "luck lottery" going on), and (c) the length of your backtest track record (more data = more trustworthy = less deflation needed). The point for interview purposes: **the reported metric itself gets penalized as a function of how much searching produced it**, which is a more finance-native framing than "adjust your p-value threshold."

**Harvey, Liu, and Zhu's multiple-testing framework (2016)** — this paper reframed how the entire academic factor literature should be read. Their argument: hundreds of "anomaly" factors have been published in finance journals over the decades (momentum, value, quality, low-volatility, dozens more), each cleared the traditional single-test significance bar (t-statistic > 2.0, roughly p < 0.05). But treated as one enormous multiple-testing exercise across the whole research community, that bar is far too permissive — they argue the *effective* threshold, once you account for how many factors have collectively been tried, should be closer to **t-statistic > 3.0**. This directly extends the **data snooping** distinction already in the notes (community-wide reuse of the same historical dataset, as opposed to multiple testing being something one researcher does within one study) — Harvey-Liu-Zhu is essentially "what does multiple testing look like when the tester is the entire academic field over 50 years, not just you in one afternoon."

### Summary table

| Approach | What it adjusts | Conservative? | Best used when |
|---|---|---|---|
| Bonferroni | Significance threshold (α/n) | Very conservative | Small number of tests, need certainty |
| FDR (Benjamini-Hochberg) | Which discoveries you keep, accepting a known error rate | Moderate | Larger batches (dozens+), screening many candidates |
| Deflated Sharpe Ratio | The headline performance metric itself | Scales with # trials + trial variance | Reporting a single backtest's Sharpe/IC honestly |
| Harvey-Liu-Zhu (t > 3.0) | The bar for "this factor is real," field-wide | Very conservative, field-level | Judging whether a factor is genuinely novel vs. already-known noise |

---

## 6. Direct connection back to prior decisions

This is not a disconnected new topic — it's the formal justification behind several decisions already locked:

- **Rank IC (Spearman) + IR + full-window t-statistic, not cherry-picked periods** (locked metrics decision) — this is exactly the discipline multiple testing demands: report the metric across the entire honest track record, not the best-looking sub-period, because reporting a sub-period is itself a form of testing many "candidate periods" and picking the winner.
- **The winner's curse (P1-LB2)** — is literally the n=3 case of this lesson's general n-test formula. Three honestly-validated candidates, true skill 0.040 each, luck components +0.005/+0.001/+0.008 → picking the best (0.048) is exactly "reporting the best of n tests without correcting for having tested n things." P1-LB3 is P1-LB2's math, generalized.
- **Data snooping vs. multiple testing** (already distinguished in the notes) — multiple testing is what *you* do within one project (testing 15 factor variants this afternoon); data snooping is structural and field-wide (the same historical dataset reused by the entire academic community for 50 years). Harvey-Liu-Zhu bridges the two: their t > 3.0 recommendation is essentially "correct for field-wide data snooping the same way you'd correct for your own multiple testing, just at a much larger n."
- **Honest replication framing, not novel discovery** — the existing decision to frame Project 1's factors as replicating established literature (momentum, value) rather than claiming new discoveries is, in this lesson's language, a way of sidestepping the multiple-testing problem almost entirely: you're not searching across dozens of untested variants hoping one clears a significance bar, you're implementing factors that already survived the field's t > 3.0 bar.

---

## 7. Answering the "explain back" question directly

**"I tested momentum, volatility, and value — why can't I just report whichever had the best backtest?"**

Because "whichever had the best backtest" is not a neutral description of your best strategy — it's the output of a selection process, and that selection process mechanically inflates whatever number you report, in direct proportion to how many things you tested. Even if all three factors have genuine, real, honest predictive power (no look-ahead bias, no in-sample peeking), the best-performing one among the three will still be flattered by that period's luck, the same way the best of three honestly-interviewed, equally-skilled candidates will still look artificially better than they really are. The fix isn't "distrust your backtest" — it's **disclose how many things you tried, and either correct your reported number for that count (deflate it, Bonferroni/FDR-adjust it) or validate the winner on data that had zero influence on which one you picked** (the untouched holdout from P1-LB2 is exactly this — it's the only check immune to the winner's curse, because the holdout couldn't have influenced the selection).

---

## 8. Implication for the Project 1 build (methodology validator, P1-Build-8)

Carrying forward as a concrete requirement: the methodology validator should flag as a red flag any submission that:
1. Reports a single best-period or best-variant metric without disclosing how many variants/periods were tested (echoes the existing carried-forward item from P1-L6).
2. Shows no multiple-testing correction (Bonferroni/FDR) or deflation applied when multiple factor variants were compared.
3. Presents a factor as "novel" without framing against the Harvey-Liu-Zhu field-wide bar — i.e., doesn't acknowledge that hundreds of factors have already been tested in the literature.

---

**Deliverable:** This notes file.
**Track status:** Backtesting Rigor track complete (3/3). Evals track (P1-LE1-LE2, 0/2) remains before Phase 2 (Architecture) begins.
