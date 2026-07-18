# P1-LB1: Walk-Forward Validation Done Properly

**Track:** Backtesting Rigor (1 of 3 lessons in this track)
**Completed:** 2026-07-18

## Where this sits

Backtesting Rigor track, lesson 1 of 3. This track exists because Project 2 (Backtesting Copilot) no longer automatically teaches this before Project 1 ships, and this is the difference between a backtest that's honest and one that's quietly cheating. This lesson covers the mechanics; P1-LB2 goes deeper on in-sample/out-of-sample structure specifically, and P1-LB3 covers what happens when you test many factor variants and only report the winner (multiple-testing/p-hacking).

---

## The core intuition, before any terminology

Think about how you'd actually operate this system if it were live at Fidelity, not a backtest.

On the first trading day of each month, you look at everything you know **as of that morning** — prices, fundamentals, whatever historical data exists up to yesterday's close — and you make a decision: which stocks to buy, which to sell, how much weight to give value versus momentum in your combined score. You commit to that decision. A month later, new data has arrived. You update your view and rebalance again.

At no point in that process do you get to see next month's numbers before making this month's decision. That's not a rule someone imposes on you — it's just what "the future hasn't happened yet" means.

A backtest is supposed to be a simulation of exactly that constraint, replayed over history. **Walk-forward validation is the discipline of enforcing that constraint in your code**, even though — unlike live trading — all the historical data already sits on your hard drive and nothing stops you from accidentally letting your model peek at it.

The failure mode this lesson is about: it's very easy to write code that looks like it respects time order, while some piece of it was actually calibrated using the whole history — including the "future" relative to the earlier months you're testing.

---

## Definition: walk-forward validation

**Walk-forward validation** is a way of testing a strategy on time-series data where, at every point in time, any parameter, weight, or model used to make a decision is estimated (or "fit," or "trained" — same idea) using only data from *before* that point, and then evaluated on data *after* that point. You then move forward in time and repeat.

Two pieces of vocabulary worth locking in now, because you'll see them everywhere in ML and quant writing:

| Term | What it means here |
|---|---|
| **Training window** | The stretch of historical data used to estimate/calibrate a parameter (e.g., factor weights) |
| **Test window** (also "out-of-sample" or "OOS") | The stretch of data — always *after* the training window in time — where you apply that already-fixed parameter and measure how well it actually performed |

The critical rule: **the boundary between train and test always moves forward with time, and test data is never touched while fitting.**

---

## Why naive monthly rebalancing is *not* the same thing

This is the specific confusion this lesson exists to clear up, because it's an easy one to fall into.

"I rebalance every month" sounds like it already implies walk-forward behavior — after all, you're updating your positions as new data arrives, month after month. But rebalancing frequency and walk-forward discipline are answering two completely different questions:

| Question | Answered by |
|---|---|
| "How often do I recompute *positions* using the latest factor scores?" | Rebalancing frequency (locked to monthly in P1-L7) |
| "Was any *parameter that generates those factor scores* estimated using data from the future relative to a given month?" | Walk-forward discipline |

Here's the trap: you can rebalance monthly — updating which stocks you hold every single month, looking perfectly dynamic — while still having calibrated something upstream (say, how much weight to give the value factor versus the momentum factor in a combined score) **once, using the entire backtest history**, including periods that hadn't happened yet relative to your earliest test months.

The monthly rebalancing is real and dynamic. The factor-weighting model behind it is frozen and omniscient. The backtest will look great — because for the early months, the model was quietly built with knowledge of how those exact months' momentum-versus-value tradeoff would play out. That's look-ahead bias (a term from P1-L8) smuggled in through a part of the pipeline you weren't watching.

**The one-sentence test to apply to any pipeline step:** *"What information determined this parameter's value, and could any of that information have come from after the date I'm using the parameter for?"* If yes, it's contaminated — no matter how monthly and rolling the trading behavior looks on the surface.

**Important nuance — not every step needs this treatment.** Winsorization and z-scoring (P1-L4) are computed fresh, cross-sectionally, at each single rebalance date — they only ever look at that month's snapshot across stocks, never across time. There's no time-series train/test question to ask there; by construction they can't leak future months into the current one. Walk-forward discipline specifically matters for anything estimated *over a historical time window* — factor combination weights, IC-based weighting schemes, ML model hyperparameters, anything where "fit this using some stretch of past months" is a step in the pipeline.

---

## Rolling vs. expanding windows

Once you accept that a training window has to sit strictly before the test point, there are two ways to define how far back that training window reaches.

| | **Rolling window** | **Expanding window** |
|---|---|---|
| **Definition** | Fixed-length lookback that slides forward — oldest month drops off as the newest month is added | Always starts at day one and keeps growing — nothing ever drops off |
| **Analogy** | A trailing 12-month performance review — only the last year counts, older history is irrelevant | A career-long track record — everything you've ever done still counts, weighted by however much data there now is |
| **Adapts to regime change?** | Faster — old, possibly stale patterns get forgotten | Slower — old patterns keep diluting new ones as more data piles on |
| **Statistical stability** | Lower — fewer data points each time, more noise in the estimate | Higher — more data points over time, less noise, but slower to react |
| **Compute/memory cost** | Constant (same-size window every time) | Grows every fold |

Neither is "correct" in the abstract — it's a bias/variance and adaptivity/stability tradeoff, the same shape of tradeoff you'd recognize from choosing a lookback period for a moving average. A short rolling window chases the current regime and gets noisy; a long expanding window is stable but sluggish to notice things have changed.

**Synonym worth knowing:** an expanding window is sometimes called an **anchored window** — the start date is "anchored" (fixed) while the end date keeps moving forward, in contrast to a rolling window where both ends move.

**For Project 1, this specific choice — rolling vs. expanding, and if rolling, what window length — is not locked yet.** It's deferred to the Architecture phase (P1-Arch), because it depends on which pipeline component actually needs a time-series-estimated parameter (most likely candidate: an IC-based factor-combination weighting scheme, discussed below). **This is an open item carried forward — see CONTEXT.md Carried-Forward Action Items.**

---

## Concrete timeline example: what "rolling forward one month" actually looks like on a calendar

The fold tables above use generic "Month 1, Month 2..." labels. It's worth translating that into real calendar dates once, because that's what actually has to get implemented.

**Setup:** monthly rebalancing (locked convention), rolling 12-month training window. Say the first rebalance date under consideration is **August 1**, and the training window is the trailing 12 completed months.

**Rolling window (12 months, constant width):**

| Rebalance date | Training window (rolling, 12 months) | Weights applied to |
|---|---|---|
| Aug 1, 2026 | Aug 2025 – Jul 2026 | Aug 2026 |
| Sep 1, 2026 | Sep 2025 – Aug 2026 | Sep 2026 |
| Oct 1, 2026 | Oct 2025 – Sep 2026 | Oct 2026 |
| Nov 1, 2026 | Nov 2025 – Oct 2026 | Nov 2026 |
| Dec 1, 2026 | Dec 2025 – Nov 2026 | Dec 2026 |

Read this row by row: for the **Aug 1 rebalance**, the training window is Aug 2025 through Jul 2026 — the 12 completed months immediately before August. Those weights get applied to trade during August.

For the **Sep 1 rebalance**, the entire window slides forward by exactly one month: **Aug 2025 (the oldest month in the previous window) drops off**, and **Aug 2026 (the month that just finished) gets added**. The window is always "the trailing 12 completed months relative to the rebalance date" — so every time the rebalance date advances by a month, the window advances by a month too, both at the front and the back end.

The constant across every row: the training window always ends the month *before* the rebalance date, and it is never applied to any date except the one immediately following it.

**Same rebalance dates, but expanding window instead (nothing ever drops):**

| Rebalance date | Training window (expanding) | Weights applied to |
|---|---|---|
| Aug 1, 2026 | Aug 2025 – Jul 2026 (12 months) | Aug 2026 |
| Sep 1, 2026 | Aug 2025 – Aug 2026 (13 months) | Sep 2026 |
| Oct 1, 2026 | Aug 2025 – Sep 2026 (14 months) | Oct 2026 |

Both windowing schemes are identical at the very first fold — they only diverge once the second fold arrives, since rolling drops Aug 2025 while expanding keeps it and just tacks on the newest month.

**One easy-to-trip-on detail:** a month only becomes usable as training input once it has actually finished and its returns/factor values are fully known — no partial months. That's why the Sep 1 training window ends at Aug 2026, not Sep 2026: standing at Sep 1, September itself hasn't happened yet, so it can't be in anyone's training data.

---

## Worked example: walking forward an IC-weighted composite factor

**Setup.** Suppose you're combining two factor scores — Value and Momentum — into one composite signal, using weights based on which factor has had the better historical Rank IC (Rank IC was locked in P1-L6/L7 as the primary signal-quality metric — the Spearman rank correlation between a factor score and next-period returns). The weighting rule: give more weight to whichever factor has historically produced a higher average IC.

w_value = IC_value / (IC_value + IC_momentum)
w_momentum = IC_momentum / (IC_value + IC_momentum)

This is exactly the kind of step that needs walk-forward treatment: the weights are *estimated over a historical window*, not computed fresh each month from a single cross-section.

*All numbers below are illustrative — invented to show the mechanics, not a result from a real backtest. Do not treat these as findings.*

Say we have 16 months of monthly data, monthly rebalancing (matching the locked convention), and we pick a **rolling 12-month training window**. That leaves months 13-16 as the first four testable months.

**Fold structure (rolling, window = 12 months, step = 1 month):**

| Fold | Train window | Test month |
|---|---|---|
| 1 | Months 1–12 | Month 13 |
| 2 | Months 2–13 | Month 14 |
| 3 | Months 3–14 | Month 15 |
| 4 | Months 4–15 | Month 16 |

Notice the window *slides* — month 1 drops out of Fold 2's training data even though it's still "in the past" relative to month 14. That's the rolling-window behavior: only the trailing 12 months count, always.

(If this were an **expanding window** instead, Fold 2's training data would be months 1–13, Fold 3 would be 1–14, Fold 4 would be 1–15 — nothing ever drops, the window just grows. Same test months, different train data.)

**Step 1 — fit weights on each training window (rolling version):**

| Fold | IC_value (train avg) | IC_momentum (train avg) | w_value | w_momentum |
|---|---|---|---|---|
| 1 | 0.050 | 0.030 | 0.625 | 0.375 |
| 2 | 0.048 | 0.032 | 0.600 | 0.400 |
| 3 | 0.045 | 0.035 | 0.5625 | 0.4375 |
| 4 | 0.042 | 0.038 | 0.525 | 0.475 |

Notice the weights drift slightly fold to fold — that's the rolling window reacting as older, more value-favorable months age out and newer, more balanced months age in. This drift is a feature of rolling windows, not a bug; an expanding window fit on the same data would drift much more slowly since old months never fully leave.

**Step 2 — apply each fold's already-fixed weights to that fold's untouched test month, and measure the realized composite IC:**

| Fold | Test month | Weights used | Realized OOS composite IC |
|---|---|---|---|
| 1 | 13 | (0.625, 0.375) | 0.044 |
| 2 | 14 | (0.600, 0.400) | 0.039 |
| 3 | 15 | (0.5625, 0.4375) | 0.036 |
| 4 | 16 | (0.525, 0.475) | 0.033 |

**Average honest, walk-forward out-of-sample IC = (0.044+0.039+0.036+0.033)/4 = 0.038**

---

## Now the naive (contaminated) version — same data, wrong process

Suppose instead you'd fit the weights **once**, using all 16 months at once (months 1-16), and then applied that single fixed weight to every month, including months 13-16.

| | Naive full-sample fit |
|---|---|
| IC_value (all 16 months) | 0.046 |
| IC_momentum (all 16 months) | 0.034 |
| w_value | 0.575 |
| w_momentum | 0.425 |

Applying this single fixed weight pair to months 13-16 (again, illustrative numbers):

| Month | "Test" IC using naive weights |
|---|---|
| 13 | 0.052 |
| 14 | 0.049 |
| 15 | 0.047 |
| 16 | 0.045 |

**Average naive "OOS" IC = (0.052+0.049+0.047+0.045)/4 = 0.048**

**The gap: 0.048 (naive) vs. 0.038 (honest walk-forward) — the naive number overstates true performance by roughly 26% relative.**

Why is it inflated? Because the weight-fitting process for the naive version was allowed to see months 13-16's own IC realizations when deciding how much to favor value versus momentum. It's not that the naive process is "lucky" — it's that it partially reverse-engineered the answer for the very months it's being scored on. This is the same underlying failure P1-L8 covered for look-ahead bias in general, just showing up specifically in a model-fitting step rather than in raw data.

---

## Follow-up Q&A: clarifications from discussion

### "But if today is Aug 1, 2026, why the heck would anybody have Dec 2026 data?"

This is exactly the right objection to raise, and it points at something worth making explicit: **the naive/contaminated version can only happen in a backtest — it is physically impossible in live trading.**

If today really is Aug 1, 2026, and you're about to trade live, nobody has Dec 2026 data. It doesn't exist yet. Live, you're stuck with the honest version by physical necessity — there's no way to cheat.

**Backtesting is different, and that's exactly the danger.** A backtest means you already have a spreadsheet or database sitting on your laptop with, say, Jan 2020 through Dec 2026 fully filled in — including months that are "in the future" relative to whichever historical date you're pretending to stand at. The whole point of the exercise is to simulate standing at Aug 1, 2026 and asking "what would my model have said, knowing only what was knowable then?" But nothing stops your code from accidentally reaching past that pretend-boundary and grabbing Dec 2026 anyway, since it's just sitting right there in the same dataframe.

So the "naive/contaminated" scenario isn't describing someone live-trading with a crystal ball. It's describing a mistake made **after the fact, while researching**: you sit down in, say, January 2027, with the full 2020–2026 history already recorded. You compute "average IC for Momentum" and "average IC for Value" using the *entire* file — because it's convenient, it's all right there — and use that single number to generate weights, which you then apply and score month by month, including August 2026. You aren't claiming to have predicted August 2026 back in August; you're claiming, retroactively, "my methodology *would have* worked in August 2026" — but the methodology being tested was actually calibrated with August 2026 (and every other month) already baked into it. The backtest ends up answering a much easier question than the one it claims to answer: not "could this have been predicted in advance," but "does this recipe fit the data it was tuned on" — which almost anything will, trivially.

**Restated side-by-side, using the Aug 2026 calendar example:**

| | Weights for Aug 2026 fit using... | Does the fitting process know how Aug 2026 actually turned out? |
|---|---|---|
| **Honest walk-forward** | Aug 2025 – Jul 2026 only | No — Aug 2026 hasn't happened yet when the weights are set |
| **Naive/contaminated (backtest-only mistake)** | Jan 2020 – Dec 2026 (the whole backtest) | Yes — Aug 2026's own result is one of the ingredients used to set the weight |

The bug only exists in backtests run on historical data you already fully possess — walk-forward validation exists specifically to force that backtest to behave as if it *didn't* already possess the future, even though, technically, it does.

### Single train/test split vs. true walk-forward

A natural next question: if today is Jan 1, 2027 and I have data from Jan 2020 through Dec 2026, and I want to predict/trade Aug 2026, shouldn't I just use data prior to Aug 2026 to predict it — e.g., **Jan 2020–Jul 2026 as training, Aug 2026–Dec 2026 as test (each month)?**

Yes — that's correct and honest, in the sense that Aug–Dec 2026 never touch the training data, so there's no look-ahead contamination. But it's a simpler cousin of walk-forward validation, not the same thing: it's a **single train/test split**, where the model is fit exactly once and then left alone across all five test months.

| | Single train/test split | True walk-forward (rolling, per earlier example) |
|---|---|---|
| Training window for Aug 2026 | Jan 2020 – Jul 2026 | Aug 2025 – Jul 2026 (trailing 12 months only) |
| Training window for Sep 2026 | **Same** — Jan 2020 – Jul 2026, reused unchanged | Sep 2025 – Aug 2026 (refit, window slid forward) |
| Training window for Dec 2026 | **Same again** — still Jan 2020 – Jul 2026 | Dec 2025 – Nov 2026 (refit again) |
| Does the model ever update across the test period? | No — fit once, tested on 5 untouched months | Yes — refit every single month as new data arrives |

Both are honest — neither lets future data leak into training. The difference is what question each one answers:

- **Single split** answers: "if I'd built this model on pre-Aug-2026 data and just left it alone for five months, how would it have done?"
- **Walk-forward** answers: "if I retrained every single month as new data came in — the way an actual desk would operate — how would it have done?"

Walk-forward is closer to how a real research/trading process actually behaves (nobody freezes their model for five months and refuses to update it), which is why it's the standard framing for this kind of validation. The single-split version isn't wrong, just a coarser, more static version of the same idea — and it's the natural bridge into P1-LB2 (out-of-sample vs. in-sample discipline), which digs further into train/test split structure specifically.

---

## Why this matters for the resume/portfolio story

An interviewer who has actually built or reviewed quant systems will ask, at some point, some version of "how did you validate this wasn't overfit / how do I know your backtest numbers are real." "I did walk-forward validation" is a claim that needs to survive a follow-up question about *which pipeline steps* actually required it and *why* — not just the fact that you rebalanced monthly. This lesson gives you the actual mechanics to answer that follow-up honestly.

---

## Connections to what's already locked

- **P1-L6/L7 (Rank IC, monthly rebalancing):** the metric and cadence used throughout this lesson's worked example were already locked — this lesson is about *how* any IC-based weighting gets fit over time, not changing what IC means.
- **P1-L8 (look-ahead bias):** the naive-vs-walk-forward gap above is look-ahead bias in a specific, model-fitting form — same root cause, different location in the pipeline than the raw-data leakage P1-L8 covered.
- **The autocorrelation decision (2026-07-13):** it was already established that monthly rebalancing + 1-month forward-return window makes IC observations non-overlapping and roughly independent. That decision is about *test-month independence*, separate from this lesson's train/test boundary question — but it's worth noting both concern "don't let information leak across time," just at different points in the pipeline.
- **P1-L2 (point-in-time universe):** a full walk-forward implementation should, in principle, use the NASDAQ-100/S&P 500 constituents as they actually existed at each historical test month, not today's list — this is the existing disclosed survivorship-bias limitation, restated here because it applies directly whenever you slice data by time.

---

## Key takeaways

| Question | Answer |
|---|---|
| Does monthly rebalancing alone guarantee walk-forward validity? | No — only guarantees positions update monthly. Says nothing about whether upstream parameters were fit using future data. |
| What's the one test to apply to any pipeline step? | "Could any information used to set this parameter have come from after the date I'm applying it to?" |
| Rolling vs. expanding — which is "correct"? | Neither, in the abstract. Rolling adapts faster but is noisier; expanding is more stable but slower to react. Trade-off, not a right answer. |
| What needs walk-forward treatment vs. what doesn't? | Anything estimated over a historical time window (factor weights, model hyperparameters) needs it. Anything computed fresh, cross-sectionally, at a single point in time (winsorization, z-scoring) doesn't. |
| What does skipping this cost you? | Backtest numbers that look better than what you could have actually achieved live — in the worked example, roughly 26% relative inflation. |

- **Deliverable:** This notes file.
- **Estimated time:** 1-2 hours.
