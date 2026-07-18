# P1-LB2: Out-of-Sample vs. In-Sample Discipline

**Track:** Backtesting Rigor (2 of 3)
**Completed:** 2026-07-18
**Estimated time:** 1-2 hours

---

## Where this sits

P1-LB1 taught the mechanics of **walk-forward validation** — how to make sure any parameter fit at time T only uses data from before T. That's a within-the-fold discipline: it governs how each individual train/test split is built.

This lesson (P1-LB2) zooms out one level. It's about the discipline of the entire research *process*, not just one fold: how much data you're allowed to look at while building and tweaking a strategy, and how much has to be locked away completely until the very end. It sets up P1-LB3 (multiple testing / p-hacking) directly — this lesson establishes *why* looking at data changes its status; LB3 gives the formal statistical language for the damage that repeated looking does.

---

## 1. What "in-sample" and "out-of-sample" actually mean

**In-sample (IS) data** is any data used, directly or indirectly, to arrive at a strategy's design — which factor to use, what lookback window, what weighting scheme, which threshold. If it touched the decision-making process at all, it's in-sample with respect to that decision.

**Out-of-sample (OOS) data** is data that played zero role in shaping the strategy. It is only ever used to *evaluate* — never allowed to feed back into a change.

**Plain-language analogy:** think of hiring a new research analyst. During training, you give them 50 historical trade write-ups with outcomes attached — they study these, learn the patterns, you correct their thinking a few times. That's the in-sample set. Before certifying them, you hand them 10 brand-new situations they've never seen, with outcomes hidden, and ask them to make calls. You only find out afterward whether they were right. That evaluation — where they can't have learned the specific answer in advance — is the out-of-sample test. If you accidentally let them peek at the answer key and then adjust how they were trained, the test is contaminated and no longer tells you how they'll perform on the next genuinely new case.

| | In-sample (IS) | Out-of-sample (OOS) |
|---|---|---|
| **Role** | Data used to *build* the strategy (choose factors, tune parameters, pick weighting scheme) | Data used only to *evaluate* the already-finished strategy |
| **Question it answers** | "What works well on data I've studied?" | "Does it still work on data I haven't studied?" |
| **Risk if misused** | None — this is exactly what it's for | Becomes worthless the moment it's used to make a decision and then something is changed |
| **Analogy** | Practice exam questions with an answer key | The real exam — never seen before, taken once |

---

## 2. Why in-sample performance is inherently optimistic

Any strategy with tunable choices (which lookback, which threshold, how many factors) will fit the *noise* in the data it was built on, not just the true underlying signal. The more knobs are turned while looking at the same data, the more of what gets called "performance" is really the strategy having memorized quirks specific to that historical stretch — quirks that won't repeat.

There is already a real number for this from P1-LB1's worked example:

| Version | How it was fit | Average IC |
|---|---|---|
| Naive (in-sample) | Weights fit once on the full 16-month sample, including the exact months being "tested" | 0.048 |
| Honest walk-forward (out-of-sample) | Weights fit only on data strictly before each test month | 0.038 |

That gap — **0.048 vs. 0.038, ~26% relative inflation** — is in-sample optimism showing up as a real number. P1-LB1 showed *how* that leak happens mechanically (a weight-fit step seeing its own test months). This lesson is about a different, higher-level version of the same problem: what happens when the researcher looks at results and then goes and tweaks the strategy — even if every individual walk-forward fold along the way was computed honestly.

---

## 3. The three-way split: train / validation / test

Walk-forward validation (LB1) explains how to build individual train/test folds correctly. But in practice, strategy development isn't a single build-and-check — it's iterative: try a 12-month lookback, look at the result, try 9-month, compare, maybe add a volatility filter, check again. Each of those "checks" is a decision point. If every check happens on the same slice of history, that entire slice has been used to shape the final choice — even though each individual walk-forward fold inside it was itself honestly time-ordered.

The standard fix is to split total available history into **three** partitions, not two:

| Partition | Purpose | How many times it's examined |
|---|---|---|
| **Training window(s)** | Fit parameters (factor weights, model coefficients) — what walk-forward's rolling/expanding folds operate on | As many times as needed — this is what building *is* |
| **Validation set** | Compare candidate designs against each other (12mo vs. 9mo lookback, with vs. without a filter) and pick the winner | Repeatedly, during development — this is where iteration happens |
| **Test set (the "holdout")** | The final, once-only check on the strategy already locked in | **Exactly once**, after all decisions are final |

**Analogy:** the training window is the analyst's coursework. The validation set is a set of practice cases with answers available to the instructor, used to decide which of several trained analysts to actually hire — these results can be examined as many times as needed, because comparing candidates against each other is precisely what a validation set is for. The test set is the analyst's first real client engagement after being hired — the one result that tells you what will actually happen going forward, and one that can't be "redone" if the outcome is disliked.

The critical discipline: **once the test set result has been seen, the strategy cannot be changed.** Doing so silently converts the test set into another validation set, and there is no longer an honest final number. (This is exactly the temptation P1-LB3 formalizes as the multiple-testing problem.)

---

## 4. Why time series splits cannot be shuffled

In a generic machine learning context, "k-fold" cross-validation typically shuffles rows randomly into folds. **This approach is invalid for backtesting.** Two reasons, both already locked in earlier lessons:

1. **Look-ahead bias (P1-L8):** if months are shuffled randomly across the whole history, some "training" rows land *after* some "test" rows in actual calendar time. A model trained partly on future information and tested on the past produces meaningless results — the P1-LB1 contamination test ("could any information used to set this parameter have come from after the date I'm using it for?") fails immediately.
2. **Autocorrelation (2026-07-13 decision, referenced in LB1's Connections):** financial time series have serial dependence — this month's return correlates with last month's. Randomly shuffled folds break up that dependency structure in a way that doesn't reflect how the strategy will actually be deployed (forward in time, never backward).

**The only valid split for time series is chronological: everything in the training/validation partition must come strictly before everything in the test partition, on the calendar.** There is no fold-shuffling escape hatch — this is a hard constraint, not a stylistic preference.

---

## 5. Worked example: designing the actual split for Project 1

Illustrative numbers resembling Project 1's actual setup (NASDAQ-100 for development). Say 10 years of daily price history are pulled, 2015–2024 (120 months total) — treat the specific years here as illustrative scaffolding, not a locked decision; the real date range will be confirmed at P1-Build-5 based on actual yfinance data availability. A reasonable chronological three-way split:

| Partition | Date range | Length | What happens here |
|---|---|---|---|
| **Development period** (training + validation, via LB1's walk-forward folds) | Jan 2015 – Dec 2021 | 84 months (70%) | All factor design decisions happen here: lookback window choice, weighting scheme, exclusion window. Walk-forward folds (rolling or expanding, per LB1) run *within* this period only. These results can be examined as many times as needed while iterating. |
| **Holdout test period** | Jan 2022 – Dec 2024 | 36 months (30%) | Locked away. Not examined, not plotted, not peeked at, while any development decision is still being made. |

**The discipline in practice, step by step:**

| Step | Action | Touches the holdout? |
|---|---|---|
| 1 | Try 12-month momentum, walk-forward across 2015–2021, get average OOS IC = 0.045 | No |
| 2 | Try 9-month momentum, same development period, get average OOS IC = 0.041 | No |
| 3 | Try 12-month momentum + a volatility filter, get average OOS IC = 0.048 | No |
| 4 | Pick the winner (12-month + volatility filter, 0.048) — final, locked configuration | No |
| 5 | Run the locked configuration, unchanged, on 2022–2024 exactly once | **Yes — the only touch** |
| 6 | Report whatever number comes out of step 5 as the genuine, honest OOS result | — |

If step 5 comes back worse than hoped and there's a temptation to return to step 3 for another variant, the discipline has been broken — the 2022–2024 period is no longer a clean test set, it's now a fourth validation candidate, and any future "final" number from that period is contaminated.

### 5a. Clarification: how "training" and "validation" actually divide up inside the development period

The 84-month development period is **not** further carved into two more static chunks (e.g., "60 months training, 24 months validation"). That would misrepresent how the split actually works. Instead, the training and validation *roles* are both served by the **walk-forward fold structure itself (P1-LB1)**, repeated across the whole development period — there is no separate, fixed-percentage validation slice sitting inside the 84 months.

Concretely, each walk-forward fold looks like this:

| Fold | Training window (fit weights) | Test month (this fold's "OOS" read) |
|---|---|---|
| 1 | Jan 2015 – Dec 2015 (or however many months the training window is) | Jan 2016 |
| 2 | Feb 2015 – Jan 2016 | Feb 2016 |
| 3 | Mar 2015 – Feb 2016 | Mar 2016 |
| ... | ... | ... |
| N | ... – Nov 2021 | Dec 2021 |

Each fold's **training window** plays the "train" role. Each fold's **test month** plays the "validation" role — but critically, it's not one held-back chunk of calendar time, it's dozens of small, rolling test months scattered across the whole development period, one per fold.

**How comparison across candidate designs actually works, given this:** when comparing two candidate designs (e.g., 12-month vs. 9-month momentum), the comparison is not done on a separate validation slice — it's done on the **aggregated walk-forward performance across all folds in the development period** (e.g., average OOS IC across all ~72 test months in a 2015–2021 development period with a 12-month training window). That aggregated number *is* the validation signal. Whichever config has the better average across all those rolling test months is the one that gets picked.

**Revised statement of roles**, correcting the impression that training and validation are two separate pools of months:

| Role | What plays that role in Project 1's design |
|---|---|
| Training | Each fold's rolling/expanding training window (P1-LB1) |
| Validation | The aggregated OOS metric across all folds in the development period — used to compare and pick between candidate configs |
| Test (holdout) | The separate, untouched holdout period (e.g., 2022–2024) — the only genuinely held-back calendar slice |

There is no locked percentage for "training vs. validation" within the development period, because they are not two separate pools of months — they are two roles played by the same rolling-fold mechanism. The only real percentage split that matters is development-period vs. holdout (illustrated as 70/30 above), and even that number is not a rule, just an illustrative choice — some practitioners use 60/40, 80/20, or a fixed number of holdout years regardless of total history length.

---

## 6. The "winner's curse": why picking the best among several honest folds still isn't enough

This is the subtle part, and the direct bridge into P1-LB3. Every one of the three candidate configurations in the worked example above (steps 1–3) was evaluated *honestly* — each used proper walk-forward validation within the development period, with no future data leaking into any individual fold. And yet, picking the best of the three (step 4) still introduces a new, different kind of optimism, on top of anything LB1 already covers.

**Why:** even with zero leakage in any single fold, some of the three candidates will look good on the 2015–2021 development period purely by chance — random noise in that particular historical stretch happens to favor one design over another. Picking the highest number among several honestly-computed candidates means, on average, picking a number that's flattered by exactly that stretch's noise. This is sometimes called the **"winner's curse"**: the winner among several honest competitions tends to be inflated by the luck that let it win, not just by genuine skill.

| Config tried | Development-period IC (honest walk-forward) | True underlying skill (unknown, illustrative) | Luck component this period |
|---|---|---|---|
| 12-month momentum | 0.045 | 0.040 | +0.005 |
| 9-month momentum | 0.041 | 0.040 | +0.001 |
| 12-month + vol filter | 0.048 | 0.040 | **+0.008** ← picked, because it got lucky |

The picked config (0.048) isn't chosen because it's genuinely the best — it's chosen partly because it drew the largest lucky draw this period. On the untouched 2022–2024 holdout, the "luck" doesn't carry over (luck, by definition, doesn't repeat), so the holdout IC would be expected to land closer to the true 0.040 than to the flattering 0.048 that was selected on.

This is exactly why the holdout test set in Section 5 matters even after walk-forward validation is done correctly at every individual fold: **the untouched test set is the only thing that can catch the winner's curse, because it's the only data that had zero influence on which configuration was selected.** P1-LB3 gives the formal name and correction approaches for this exact phenomenon when testing many factor variants and reporting the best — this lesson is the intuition; next lesson is the statistics.

---

## 7. How LB2 differs from LB1 — the boundary, stated precisely

| | P1-LB1 (Walk-forward validation) | P1-LB2 (Out-of-sample discipline) |
|---|---|---|
| **Level of the problem** | Within one fold: is a parameter fit only using past data? | Across the whole research process: has any data been used to make a decision and then re-examined? |
| **Failure mode it prevents** | A weight-fit step seeing its own test months (mechanical look-ahead) | The researcher tuning a design based on results and quietly reusing the same data (process-level leakage / winner's curse) |
| **Where it operates** | Inside the development period, across rolling/expanding folds | Across the development-period / holdout-period boundary |
| **Fixable by better code?** | Yes — a mechanical, code-level discipline | Partially — the split structure is code-level, but the "don't peek and re-tune" discipline is a human process discipline, same category as P1-LA11's automation-bias risk (no clean code fix, just discipline) |

Both exist to prevent the same underlying disease — a number that looks better than what will actually be achieved going forward — but they operate at different scopes, and Project 1 needs both.

---

## 8. What this means for P1-Build-5

The carried-forward requirement is concrete: P1-Build-5 (the backtest engine) needs to implement not just LB1's rolling/expanding walk-forward loop, but the outer chronological split described in Section 5 — a development period where iteration happens freely, and a holdout period that the code should make structurally awkward to touch casually (e.g., a config flag or a separate function call, not something that runs by default every time the notebook is re-run). The goal is to make the "don't peek" discipline something the code helps enforce, not just something that has to be remembered.

---

## Connections to prior lessons

- **P1-LB1 (walk-forward validation):** the within-fold discipline this lesson builds on; the 0.048 vs. 0.038 example is reused directly as evidence of in-sample optimism.
- **P1-L8 (look-ahead bias):** the reason time series splits can't be shuffled — training data must never come from after test data, chronologically.
- **2026-07-13 autocorrelation decision:** a second, independent reason chronological ordering matters — serial dependence in financial time series means random shuffling breaks the structure the strategy will actually face in deployment.
- **P1-LA11 (automation bias / governance):** the "don't peek and re-tune" discipline is process-level, not code-level — same category of risk as automation bias, where no clean structural fix exists and the mitigation is a documented discipline.
- **Sets up P1-LB3 (multiple testing / p-hacking) directly:** the winner's curse example in Section 6 is the intuition-level version of what LB3 will formalize with correction approaches (e.g., Bonferroni-style adjustments, at the intuition level appropriate for this curriculum).

---

## Deliverable

In-sample vs. out-of-sample comparison built into P1-Build-5, implementing the chronological three-way split (development period with walk-forward folds; untouched holdout test period) described in Section 5, with the holdout evaluated exactly once per locked configuration.
