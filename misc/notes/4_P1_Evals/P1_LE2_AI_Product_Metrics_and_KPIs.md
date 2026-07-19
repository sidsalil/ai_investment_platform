# P1-LE2: AI Product Metrics & KPIs

**Status:** Completed 2026-07-19; follow-up on production instrumentation architecture added same day
**Track:** Evals & Model Evals (2 of 2 — track now COMPLETE)
**Phase:** Phase 1, Concept Lessons — this is the **final lesson of Phase 1**. Finance (10/10), AI/Agentic (17/17), Backtesting Rigor (3/3), and Evals (2/2) are all now complete: **32/32 concept lessons total.** Next step is Phase 2 (Architecture & Design).

---

## Why this lesson exists separately from LE1

LE1 (Model evals vs. system evals) covered task success rate, schema-validity rate, and groundedness. Those are **engineering metrics** — they answer "does my pipeline work correctly," computed automatically, per run, without needing a human in the loop. You could run 500 test cases overnight in continuous integration (CI) and get all three numbers by morning.

LE2 asks a completely different question: **"How would I, as a Product Manager (PM), know whether a real portfolio manager or analyst is actually getting value from this, day to day, once it's deployed?"** That's not something you can compute from a fixed test set. It requires watching real usage over time, and it's the exact question every AI PM interview will probe, because it's the one engineers are least naturally equipped to answer.

| | LE1 (System/Model Evals) | LE2 (Product Metrics) |
|---|---|---|
| Question answered | Does the pipeline work? | Is the product succeeding for real users? |
| When computed | Every build, every CI run | Ongoing, in production, over weeks/months |
| Data source | A fixed golden dataset | Real usage logs, real human behavior |
| Owned by | Engineering / you-as-builder | Product / you-as-PM |
| Example metric | Task success rate: 84% | Weekly active users: 60% of licensed seats |
| Failure mode if ignored | Ships broken software | Ships working software nobody uses or trusts |

A system can score 95% on every LE1 metric and still fail as a product — if nobody uses it, or if analysts quietly stop trusting it after two bad memos, none of that shows up in a golden-dataset eval. That gap is exactly what LE2 covers.

**Honest caveat, consistent with the standing "no fabricated metrics" principle:** Project 1 is a portfolio project with one user — Salil. There will be no real adoption curves or real trust-survey data. What this lesson builds is (a) the analytical framework, so these can be discussed fluently and correctly in an interview, and (b) the *instrumentation design* — deciding now what would be logged if this were live, so the honest answer to "did you measure this" is "I designed the system to capture it, here's exactly how" rather than a fabricated number.

---

## Metric family 1: Adoption & usage

**Intuition.** Before asking "is it good," ask "is anyone using it." A brilliant tool nobody opens is worth zero, and low usage is itself a diagnostic signal — it tells you something is wrong even before you know what. Analogy: rolling out a new trading blotter feature to a desk — you watch whether people open it once and never return, or whether it becomes part of the daily workflow.

**The standard funnel, adapted to an internal AI research tool:**

| Stage | Question | Example metric |
|---|---|---|
| Awareness/Access | Do people know it exists and have access? | # analysts with tool access |
| Trial | Did they try it at least once? | # who ran ≥1 factor research query in 30 days |
| Repeat use | Did they come back? | # who used it in ≥2 of the last 4 weeks |
| Depth of use | How much of their workflow does it touch? | avg. # queries per active user per week |

**Worked example.** Factor Research Copilot rolled out to a 200-person research desk:

| Metric | Count | Rate |
|---|---|---|
| Analysts with access | 200 | 100% (baseline) |
| Tried it at least once (30 days) | 140 | 70% (trial rate) |
| Used it in ≥2 of last 4 weeks | 60 | 30% of all, 43% of trialers (repeat/retention rate) |
| Avg queries/week among the 60 repeat users | 4.2 | — |

**Reading it like a PM:** a 70% trial rate is healthy (people are curious, access isn't the blocker). But only 43% of people who tried it came back a second week — that's a **retention** problem, not an awareness problem, and it points toward a different fix (quality, trust, workflow-fit) than a low trial rate would (which would point toward discoverability or training). The funnel stage that's broken changes the diagnosis and the fix.

**Why this matters for P1 specifically:** in the risk memo / case study, the honest framing is: "I did not have real usage data — this is a single-user project — but here is the exact instrumentation I'd add (a `user_id` and `session_id` field on every logged run) so this funnel could be computed on day one of a real deployment." That is a stronger interview answer than presenting a fabricated number.

---

## Metric family 2: Override / escalation rate

**Intuition.** This is arguably the single most underrated AI product metric, and it builds directly on P1-LA11 and P1-LA12. When the system produces an output — a memo, a validator verdict — and a human analyst edits it, rejects it, or overrides it, that's a real, unfakeable signal of trust and quality. It's not a survey answer filled out lazily; it's a *behavior*.

**Definition:** Override/escalation rate = the fraction of system outputs that a human rejects, materially edits, or overrides before treating them as final.

This connects to two things already locked earlier in the curriculum:
- **P1-LA11's escalation checkpoints** (`severity: "blocking"`) are *system-initiated* escalations — the system itself says "a human needs to look at this."
- **Override rate** is the complementary, *human-initiated* signal — even when the system didn't flag anything, did a human decide to intervene anyway?

Both matter, and they can diverge in informative ways.

**Key nuance — there is no single "good" override rate, because both directions are informative:**

| Override rate | What it might mean |
|---|---|
| Near 0% | Either the task is trivial and low-stakes (good), OR nobody is actually reviewing the output critically — automation bias (the P1-LA11 residual risk), which is bad and invisible unless review depth is separately checked |
| Moderate (roughly 10-20%) | Healthy — humans are engaged, catching real edge cases, system is a genuine assistant, not a rubber stamp |
| Very high (>40-50%) | System isn't trusted or isn't good enough — analysts are essentially redoing the work, and the "AI" step is adding latency, not value |

**Worked example**, using the P1 memo generator as the concrete case:

| | Count | Rate |
|---|---|---|
| Memos generated in a month | 500 | — |
| Memos accepted as-is by the analyst | 390 | 78% |
| Memos materially edited before use | 85 | 17% |
| Memos rejected outright, redone manually | 25 | 5% |
| **Total override rate** | 110 / 500 | **22%** |

22% sits in the "healthy engagement" zone — not zero (people are actually reading and thinking, not rubber-stamping), not so high that the tool is failing. A good PM digs one level deeper: **what are the 85 edits actually correcting?** If 60 of those 85 edits are all fixing the same thing (say, tone — consistent with the P1-LA16 memo-tone-mismatch scenario already logged), the correct read is not "the system is 22% unreliable" — it's "there's one specific, fixable prompt gap accounting for most of the override volume." Override rate signals *that* something needs attention; the trace/eval layer from LE1 and P1-LA12 tells you *what*.

**Instrumentation for P1's build:** add a `human_action: Literal["accepted", "edited", "rejected"]` field to the memo subagent's (and validator's) output, logged as its own event alongside the P1-LA12 `TraceEvent` taxonomy. This is **not** one of the seven trace event types (`perceive`/`reason`/`act`/`observe`/`escalation`/`subagent_invocation`/`subagent_result`) — it's distinct, later-arriving metadata, since it only exists once a human has acted on the output, after the trace itself completed. Worth noting explicitly on any architecture diagram: trace events are generated *during* a run; override data is generated *after*, by someone else's action, on a different timeline.

---

## Metric family 3: Trust calibration

**Intuition.** A subtler, second-order metric on top of override rate. It maps directly onto the finance concept of **calibration** in probability forecasting — or, in trading terms, whether a portfolio manager's confidence in a position matches how often that position is actually right.

**Definition:** Trust calibration asks whether a user's *subjective* trust in the system tracks the system's *actual* reliability — not whether trust is high, but whether it's **accurate**.

Two distinct failure modes, and they are opposite problems requiring opposite fixes:

| Scenario | Subjective trust | Actual reliability | Problem | Risk |
|---|---|---|---|---|
| **Over-trust** | High (e.g., "I basically don't check it anymore") | Lower than believed | User relies on it more than it deserves | Automation bias (P1-LA11) — errors slip through because nobody's really checking |
| **Under-trust** | Low (e.g., "I redo everything by hand anyway") | Higher than believed | User doesn't extract the value the system actually provides | Wasted investment — the tool works, but adoption/depth-of-use stalls because people don't believe it |
| **Well-calibrated** | Tracks actual reliability | — | User trusts it exactly as much as it's earned | Target state |

**Worked numeric example.** Quarterly survey asking analysts to self-rate trust in the methodology validator ("How much do you trust this system's pass/fail verdicts?" 0-100%), compared against actual accuracy measured from the golden dataset (LE1-style) plus real-world override data:

| Analyst group | Self-reported trust | Actual validator accuracy (measured) | Gap | Diagnosis |
|---|---|---|---|---|
| Group A | 85% | 65% | +20 pts (over-trust) | Automation-bias risk — recommend a mandatory second-look step or a visible confidence indicator |
| Group B | 40% | 88% | -48 pts (under-trust) | Value is being left on the table — investigate why (bad first impression? one early bad memo poisoned the well?) |
| Group C | 70% | 72% | +2 pts | Well-calibrated — no action needed |

**Important discipline:** over-trust cannot be fixed by making the system "seem" less trustworthy, and under-trust cannot be fixed by making it "seem" more trustworthy. The fix has to change either the actual reliability or the user's accurate perception of it — cosmetic confidence-theater in either direction is dishonest and, for Group A specifically, actively dangerous (it would widen the gap, not close it). This is the same discipline already locked in P1-LA11: `ValidationResult.passed: true` is a recommendation to a human, never a final answer — over-trust is what happens when that discipline erodes in practice, even if the code enforces it correctly.

**Connection back to override rate (family 2):** override rate is one of the *inputs* used to estimate actual reliability in the first place, alongside golden-dataset accuracy. Trust calibration is what emerges when that measured reliability is compared against what people *say* they believe. Both metrics are needed; neither alone tells the calibration story.

---

## Metric family 4: ROI / cost-of-quality

**Intuition.** This is the family PMs get wrong most often, by defaulting to the easiest number to compute: cost per API call. That number is real, but it's the wrong denominator for a business conversation, because it ignores every dollar of cost that shows up *after* the API call — human correction time, downstream error cost, and so on. The right question isn't "what does a call cost," it's **"what does a successful, usable outcome cost, all-in?"**

**Definitions:**
- **Cost per API call** — raw compute cost. Cheap, easy, and answers the wrong question in isolation.
- **Cost per successful task** — raw compute cost divided by the number of outputs that actually succeeded (LE1's task success rate is a direct input here).
- **Cost of quality (fuller version)** — raw compute cost **plus** the human labor cost of catching and fixing failures (directly using family 2's override data) **plus**, where estimable, the cost of failures that slip through uncaught.

**Worked example**, building on the numbers used earlier in this lesson:

| Component | Value |
|---|---|
| Memos generated | 500 |
| Cost per API call (LLM compute) | $0.04 |
| Raw compute cost | 500 × $0.04 = **$20.00** |
| Task success rate (LE1-style) | 84% → 420 succeeded outright |
| **Cost per successful task (compute only)** | $20.00 / 420 = **$0.048** |
| Overrides requiring human correction (family 2) | 110 memos |
| Avg. analyst time per correction | 8 minutes |
| Analyst fully-loaded hourly cost | $90/hr |
| Human correction cost | 110 × (8/60) × $90 = **$132.00** |
| **All-in cost of quality (compute + human correction)** | $20.00 + $132.00 = **$152.00** |
| **All-in cost per successful/usable memo** | $152.00 / 500 = **$0.304** |

The gap matters: cost-per-API-call framing says "$0.04 per memo, essentially free." Cost-of-quality framing says the real number is **$0.304 per usable memo — roughly 7.6x higher**, almost entirely driven by human correction time, not compute. That's the number that should actually drive a build-vs-buy or invest-more-in-quality decision, and it's the framing that separates an AI PM who understands the business from one who only understands the API bill.

**Necessary next question:** is $0.304/memo good? It depends entirely on the counterfactual — what generating that memo cost *before* the AI system existed. If a human analyst took 45 minutes to draft the same memo unaided, at $90/hr that's $67.50 — making $0.304 an enormous win even with the correction overhead included. If the honest counterfactual is closer to 10 minutes, the win is real but far smaller. **Cost of quality is only meaningful next to a real baseline** — a number in isolation ("$0.304 per memo!") is a vanity metric dressed up as rigor if it can't also be stated against what it's being compared to.

---

## Bringing the four families together

| Metric family | Core question | P1 instrumentation hook |
|---|---|---|
| Adoption & usage | Is anyone using it, and do they come back? | `user_id`/`session_id` on every logged run (not currently in the P1-LA12 `TraceEvent` schema — a noted gap) |
| Override/escalation rate | Do humans trust the output enough to leave it alone? | New `human_action` field on memo/validator output, logged post-hoc alongside the trace |
| Trust calibration | Does stated trust match measured reliability? | Requires periodic survey (product-side) + LE1 golden-dataset accuracy (engineering-side) compared side by side |
| ROI / cost-of-quality | What does a *usable* outcome actually cost, all-in? | Combine raw compute cost (cheap to log) with override-driven human-correction time (family 2's data) |

**Dependency chain, worth stating plainly:** family 4 needs family 2's data as an input; trust calibration (family 3) needs both LE1's accuracy numbers and independently-collected survey data. None of these four metrics is fully self-contained — presenting each as if it stood alone would misrepresent how they actually relate.

**Honest scope note for the case study / risk memo:** real numbers for any of these four families cannot be shown from a single-user portfolio project — a real adoption funnel, a real override rate across many users, real survey-based trust data, and a real cost-of-quality baseline all require actual deployment scale not available here. What *can* be shown, and what is arguably more impressive to a technical interviewer, is that the schema and instrumentation were designed to capture all of this on day one of a real deployment, with a clear understanding of which number depends on which other number — that is the PM skill, independent of whether toy numbers were actually run.

---

## Follow-up: Production instrumentation architecture (capture → calculation → presentation)

**Follow-up question:** in a real deployment to (say) 200 analysts, wouldn't there be separate development cycles dedicated to capturing metrics, then a logic/reporting layer computing them, then a dashboard presenting them? What does capture, calculation, and presentation actually look like, and where does this data get stored without slowing the platform down?

**Answer: yes — this is a genuine three-layer architecture, not one piece of code.** This is a standard data-engineering pattern (capture → aggregate → present), directly analogous to how end-of-day risk numbers reach a portfolio manager: trade tickets are logged in real time, a batch job aggregates positions and computes risk overnight, and the dashboard the next morning reads the already-computed result rather than recomputing from raw trade tickets live.

### The three layers

| Layer | Question it answers | What it actually is | Update cadence | Who builds/owns it |
|---|---|---|---|---|
| 1. Capture / Instrumentation | What raw events happened? | Logging code embedded at every user-facing touchpoint | Real-time, every event | Engineers building the agent/UI |
| 2. Calculation / Aggregation | What do those raw events mean in aggregate? | A scheduled batch job (or streaming pipeline) reading raw logs and computing rates, funnels, cost figures | Batch — hourly/daily/weekly/monthly depending on the metric | Data/analytics engineers |
| 3. Presentation / Dashboard | How does a human see it? | A dashboard reading *pre-computed* aggregates — never raw logs | On dashboard load, reading cheap pre-aggregated data | PM/analytics + frontend |

**The critical discipline:** layer 3 never computes directly from layer 1's raw logs. If the dashboard issued a query across hundreds of thousands of raw events every time an analyst opened it, that couples UI performance to log volume — a design mistake. Layer 2 exists specifically to do the expensive work once, on a schedule, so layer 3 stays cheap and fast.

### Layer 1: Capture — what actually gets logged

The P1-LA12 `TraceEvent` schema (`perceive`/`reason`/`act`/`observe`/`escalation`/`subagent_invocation`/`subagent_result`) is a capture-layer design already — but it captures *system-internal* behavior, not *product/user* behavior. Product metrics need a second, parallel event stream, captured at different moments:

| Metric family | Raw event(s) needed | Automatic or manual? | Captured where |
|---|---|---|---|
| Adoption & usage | `session_start` (user_id, timestamp), `query_submitted` (user_id, timestamp) | Automatic | The web/Streamlit app layer, not the agent itself |
| Override/escalation rate | `human_action` (accepted/edited/rejected) + real timestamps for when review started and ended | Automatic, but requires the review UI to have explicit accept/edit/reject controls | The review UI, at the moment of the click |
| Trust calibration | Self-reported trust score | **Manual** — a periodic survey, not a naturally occurring event | A separate survey tool, joined later by `user_id` |
| ROI/cost-of-quality | `token_count`/`latency_ms` (already in `TraceEvent`) + real correction time (from override event timestamps) + a maintained $/hour rate | Mostly automatic, one manual config value | `TraceEvent` for compute cost; override timestamps for correction time; a small config table for hourly rate |

Two corrections to the original worked examples in this lesson, surfaced by this follow-up: (1) trust calibration cannot be captured automatically at all — it's a belief, not a behavior, which caps its practical cadence at however often surveys are tolerable (realistically quarterly, at most monthly before survey fatigue); (2) the "8 minutes per correction" figure used earlier in this lesson was illustrative only — a real system would capture the actual elapsed time between memo-shown and human_action-logged as a real, measured interval, not an assumed constant.

### Layer 2: Calculation — the aggregation job

A scheduled program (commonly an Extract-Transform-Load, or ETL, job) wakes up on a schedule, reads the raw events layer 1 wrote to durable storage, and turns thousands of raw rows into a handful of meaningful numbers. Worked example — override rate computed weekly from a raw events table:

| memo_id | user_id | generated_at | human_action | action_at |
|---|---|---|---|---|
| M001 | analyst_07 | 2026-08-03 09:14 | accepted | 2026-08-03 09:16 |
| M002 | analyst_07 | 2026-08-03 10:02 | edited | 2026-08-03 10:11 |
| M003 | analyst_22 | 2026-08-03 11:40 | rejected | 2026-08-03 11:52 |

The weekly job groups rows where `generated_at` falls in the last 7 days, counts total rows, counts rows where `human_action != accepted`, and divides — the entire calculation. The same run also computes the correction-time distribution from `action_at - generated_at`, replacing the earlier assumed 8-minute placeholder with a real measured average.

**Different metrics need different aggregation windows — a real design decision, not an arbitrary one:**

| Metric | Sensible aggregation window | Why |
|---|---|---|
| Adoption/usage funnel | Weekly (rolling 4-week for retention) | Daily usage is noisy; weekly smooths enough to see trend |
| Override rate | Daily or weekly | Want to catch a regression (a bad prompt change) fast |
| Trust calibration | Quarterly | Bottlenecked by survey cadence, not compute |
| Cost-of-quality | Monthly | Ties naturally to a billing/budget cycle |

This cadence mismatch is itself a real engineering fact: no single dashboard-refresh job computes all four families on the same schedule, because each is bottlenecked by a different constraint (compute cost for override rate vs. human survey logistics for trust calibration).

### Layer 3: Presentation — the dashboard

By the time data reaches this layer, the hard work is done — the dashboard reads a small, pre-computed summary table and renders charts, never touching raw event logs.

| Dashboard section | Chart type | Data source (from Layer 2) |
|---|---|---|
| Adoption funnel | Funnel/bar chart: access → trial → repeat-use | Weekly aggregation table |
| Override rate trend | Line chart over time, annotated with prompt/model-change events | Daily/weekly aggregation table |
| Trust calibration | Scatter plot: self-reported trust (x) vs. measured accuracy (y), diagonal = perfect calibration | Quarterly survey join |
| Cost-of-quality | Stacked bar: compute cost + human correction cost, per month | Monthly aggregation table |

Annotating the override-rate chart with deployment events (a prompt change, a model upgrade) turns a number into a diagnosis — a spike lining up exactly with a shipped prompt change is a far stronger signal than the raw rate alone, the same instinct as annotating a P&L chart with strategy-change dates.

### Storage and the read/write performance question

Product metrics never share a database, or even a read/write path, with the agent's live execution. This maps directly onto a distinction already familiar from trading systems: **OLTP vs. OLAP.**

| | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |
|---|---|---|
| Optimized for | Fast, small, frequent writes; one row at a time | Fast reads over huge volumes; aggregations, group-bys |
| Example in trading | The order management system (OMS) routing live orders | The end-of-day risk/analytics data warehouse |
| Example here | The agent's live execution path (tool calls, memo generation) | The metrics/aggregation store (Layer 2) |
| Touched by a live user request? | Yes — critical path | Never directly — always a batch copy |

**Core discipline:** metrics writes must never sit on the critical path of a live user request, and metrics reads must never query the live/operational database.

**Write side — why synchronous writes are the actual danger:** if the agent code did "generate memo → *synchronously* write to the metrics database → return response," the user's response time becomes dependent on the metrics database's health, for a concern (analytics) unrelated to whether the memo itself was correct. The standard fix is asynchronous, decoupled logging:

| Pattern | How it works | Trade-off |
|---|---|---|
| Fire-and-forget / buffered write | Event appended to an in-memory buffer or local log file immediately (sub-millisecond); a background process flushes periodically | Simple; small risk of losing the last few unflushed events on a crash |
| Message queue (e.g., Kafka, SQS, or similar) | Application publishes the event to a queue and moves on immediately; a separate consumer writes to storage whenever it can | More durable, more infrastructure; standard at real production scale |

Either way, the user's request returns without waiting on the metrics write. The P1-LA12 decision to hand-roll `TraceEvent` and write it to a local JSON-lines file is already this pattern in miniature, at a scale where a background flush process isn't yet necessary.

**Read side — why the dashboard never queries raw events live:** the same "layer 3 never touches layer 1" rule applies on the read side — if the dashboard scanned every raw event row on every page load, that's the read-side equivalent of the write-side problem, competing for the same resources as the live system and getting slower as event volume grows over months. Layer 2's aggregation job absorbs that cost once, on a schedule.

**Where things concretely live:**

| Data | Storage | Why |
|---|---|---|
| Raw events (Layer 1) | An append-only event store — a log file, a dedicated events table, or a proper event-streaming system at real scale | Writes are simple appends, never updates — matches the aggregation job's access pattern (read everything since last run) |
| Aggregated summaries (Layer 2 output) | A small, separate "metrics_summary" table, physically distinct from both the raw event store and the agent's own operational database | Tiny relative to raw events — this is what keeps dashboard reads cheap |
| Dashboard | Reads only the summary table | Never sees raw events at all |

**Direct answer to the original question:** yes, constant reads/writes against a shared live database would slow the platform down if done naively — which is exactly why real systems separate the write path (async, off critical path) from the read path (pre-aggregated, physically separate table), the same instinct as never running a heavy risk report directly against a live order-routing database.

### Development cycles — confirmed as genuinely 2-3 separate sprints

| Sprint | Deliverable | Why this order |
|---|---|---|
| 1. Instrumentation | Event schemas + logging code wired into every touchpoint (login, query, review-action) | Cannot aggregate data that was never captured — the one true hard dependency |
| 2. Aggregation pipeline | Scheduled jobs computing the four families from raw events into summary tables | Needs real event data flowing from Sprint 1 to test against |
| 3. Dashboard | The PM-facing UI reading Sprint 2's output | Trivial once Sprint 2's tables exist — usually the fastest of the three sprints, which surprises people who assume the dashboard is "the product" |

A common, costly mistake: building the dashboard first against fake/hardcoded data, only to discover later that the real event data needed for it was never cleanly captured. Instrumentation is the layer that's expensive to retrofit; a dashboard is cheap to redo.

---

## Carried forward to Phase 2/3

- **Decision locked (resolves the open question from this lesson's original version):** rather than leaving the metrics pipeline as a described-but-unbuilt capability, Project 1 will build a small, clearly-labeled **synthetic multi-user event dataset** (a script generating plausible multi-week, multi-user logs across all four metric families) and build a *real, working* Layer 2 (aggregation job) and Layer 3 (dashboard) against it. This is not fabricating a metric — the synthetic-data labeling stays explicit throughout — but it demonstrates the full three-layer pipeline mechanically works, which is a materially stronger portfolio artifact than an unbuilt, only-described capability.
- **Architecture (Phase 2):** the system architecture diagram must show product metrics as a genuinely separate three-layer subsystem (capture / aggregation / dashboard), architecturally distinct from the P1-LA12 `TraceEvent` observability subsystem, with an explicit note on the OLTP/OLAP-style separation between the agent's live execution path and the metrics store.
- **Architecture (Phase 2):** decide whether to add `user_id`/`session_id` to the `TraceEvent` schema now, or keep it as a separate product-events schema entirely (the follow-up discussion suggests a **separate schema** is more correct — product events like `session_start`/`query_submitted` are a different concern from agent-internal trace events, captured at different moments by different code).
- **Build (Phase 3):** implement Sprint 1 (event schemas: `human_action` on memo/validator output per the original P1-LE2 decision, plus new `session_start`/`query_submitted` product events) before attempting Sprint 2 (aggregation) or Sprint 3 (dashboard) — the dependency order is a hard constraint, not a preference.
- **Build (Phase 3):** metrics writes must be implemented as async/buffered (fire-and-forget to a local log, flushed on a schedule), never as a synchronous write on the same path as the agent's response — consistent with the JSON-lines pattern already locked for `TraceEvent` in P1-LA12.
- **Polish:** the risk memo / case study should present all four metric families as the *framework* the system was designed to support, explicitly flagged as demonstrated on synthetic, clearly-labeled data rather than presenting any fabricated adoption/trust/ROI numbers as if they were measured. This is consistent with the standing principle that honest scoping of limitations is the senior move.

---

---

## Appendix: Full Q&A exchange log (verbatim)

This appendix preserves the actual back-and-forth from this lesson's follow-up discussion, in addition to the synthesized notes above, so the full exchange is on record exactly as asked and answered.

### Q&A #1

**Question asked:** "I am a senior Product Manager at a financial services firm (Fidelity)... [context] ...One of the reasons I wont be able to show real numbers is because this is a portfolio project with one user. But assuming this is a live production project rolled out to (say) 200 analysts how would the product metrics be captured? What I mean is wouldnt there be development cycles dedicated to capturing relevant core metrics and then another logic layer or reporting layer on top that does the complex calculations? What does products metrics capture, metrics calculation and metrics presentation on a dashboard look like?"

**Answer given:**

Yes — exactly right. In a real deployment, this isn't one blob of code that "computes trust calibration." It's three distinct layers, built in separate development cycles, each with a different owner and a different update cadence. This is actually a completely standard data-engineering pattern (capture → aggregate → present), and the AI-specific stuff from the last lesson just tells you *what* to capture — the plumbing around it is the same plumbing behind any analytics dashboard.

**The three-layer architecture**

Intuition first, using a desk analogy already familiar: think of how end-of-day risk numbers get to a PM's dashboard. Nobody computes VaR (Value at Risk) live off raw trade tickets every time someone opens the dashboard. Trade tickets get logged in real time (capture), a batch job runs overnight to aggregate positions and compute risk (calculation), and the dashboard just reads the *already-computed* result the next morning (presentation). Product metrics for an AI system work the same way.

| Layer | Question it answers | What it actually is | Update cadence | Who builds/owns it |
|---|---|---|---|---|
| 1. Capture / Instrumentation | What raw events happened? | Logging code embedded at every user-facing touchpoint | Real-time, every event | Engineers building the agent/UI |
| 2. Calculation / Aggregation | What do those raw events mean in aggregate? | A scheduled batch job (or streaming pipeline) that reads raw logs and computes rates, funnels, cost figures | Batch — hourly/daily/weekly/monthly depending on the metric | Data/analytics engineers |
| 3. Presentation / Dashboard | How does a human see it? | A BI tool or dashboard app reading *pre-computed* aggregates — never raw logs | On dashboard load, but reading cheap pre-aggregated data | PM/analytics + frontend |

The critical discipline: layer 3 never computes directly from layer 1's raw logs. If the dashboard is issuing a query across 500,000 raw events every time an analyst opens it, that's a design mistake — slow, expensive, and it couples UI performance to log volume. Layer 2 exists specifically to do the expensive work once, on a schedule, so layer 3 stays cheap and fast.

**Layer 1: Capture — what actually gets logged, and by whom**

The P1-LA12 `TraceEvent` schema (`perceive`/`reason`/`act`/`observe`/`escalation`/`subagent_invocation`/`subagent_result`) *is* a capture-layer design — it just captures system-internal behavior, not product/user behavior. Product metrics need a **second, parallel stream** of raw events, captured at different moments than the trace events are.

| Metric family | Raw event(s) needed | Captured automatically or manually? | Where it comes from |
|---|---|---|---|
| Adoption & usage | `session_start` (user_id, timestamp), `query_submitted` (user_id, timestamp) | Automatic — fired by the application code the instant a user logs in / submits a query | The web/Streamlit app layer, not the agent itself |
| Override/escalation rate | `human_action` (accepted/edited/rejected), plus timestamps for when review started and ended (not assumed) | Automatic, but requires UI to have an explicit "accept/edit/reject" control that fires the event | The review UI, at the moment the analyst clicks accept/edit/reject |
| Trust calibration | Self-reported trust score | Manual — a periodic survey, not an event that happens naturally in the product | A separate survey tool (even a quarterly form), joined later by `user_id` |
| ROI/cost-of-quality | `token_count`, `latency_ms` (already in `TraceEvent`) + actual correction time (from override event's timestamps) + a maintained cost parameter (loaded hourly rate) | Mostly automatic, one manual config value | `TraceEvent` for compute cost; override event timestamps for correction time; a small config table for the $/hour rate |

Two things worth noticing: (1) trust calibration is the odd one out — it cannot be captured automatically at all, because trust is a belief, not a behavior. No amount of clever logging replaces asking people, which is a real constraint on cadence (realistically quarterly, maybe monthly at most, before survey fatigue). (2) The 8-minutes-per-correction number used earlier in the lesson was illustrative, not measured — in a real system the actual elapsed time between "memo shown" and "human_action logged" is a real, capturable interval, not an assumed constant.

**Layer 2: Calculation — the aggregation/reporting job**

This is a scheduled program — commonly an Extract-Transform-Load (ETL) job, or in modern data-stack language a "batch aggregation pipeline" — that wakes up on a schedule, reads the raw events layer 1 wrote somewhere durable, and turns thousands of raw rows into a handful of meaningful numbers.

Worked example — override rate, computed weekly. The raw events table might look like:

| memo_id | user_id | generated_at | human_action | action_at |
|---|---|---|---|---|
| M001 | analyst_07 | 2026-08-03 09:14 | accepted | 2026-08-03 09:16 |
| M002 | analyst_07 | 2026-08-03 10:02 | edited | 2026-08-03 10:11 |
| M003 | analyst_22 | 2026-08-03 11:40 | rejected | 2026-08-03 11:52 |

The weekly aggregation job runs something conceptually like: group all rows where `generated_at` falls in the last 7 days, count total rows, count rows where `human_action != accepted`, divide. That's the entire override-rate calculation — the complexity isn't in the math, it's in reliably capturing every row in layer 1 in the first place. This job would also compute, in the same run, the correction-time distribution (from `action_at - generated_at` for edited/rejected rows), directly replacing the assumed "8 minutes" with a real measured average.

Different metrics genuinely need different aggregation windows:

| Metric | Sensible aggregation window | Why |
|---|---|---|
| Adoption/usage funnel | Weekly (rolling 4-week for retention) | Usage patterns are noisy day-to-day; weekly smooths it enough to see trend |
| Override rate | Daily or weekly | Want to catch a regression (a bad prompt change) fast |
| Trust calibration | Quarterly | Bottlenecked by survey cadence, not by compute |
| Cost-of-quality | Monthly | Ties naturally to a billing/budget cycle |

That mismatch in cadence is itself a real engineering fact: you can't have one dashboard-refresh job that computes all four families on the same schedule, because they're bottlenecked by different things — compute cost for override rate, human survey logistics for trust calibration.

**Layer 3: Presentation — the dashboard**

By the time data reaches this layer, all the hard work is done — the dashboard's job is just to read a small, pre-computed table and draw charts. Given the Streamlit stack, this would literally be a page that queries a small "metrics_summary" table (the output of layer 2) and renders it — never touching the raw event logs.

| Dashboard section | Chart type | Data source (from layer 2) |
|---|---|---|
| Adoption funnel | Funnel/bar chart: access → trial → repeat-use | Weekly aggregation table |
| Override rate trend | Line chart over time, with an annotation whenever a prompt/model change shipped | Daily/weekly aggregation table |
| Trust calibration | Scatter plot: self-reported trust (x-axis) vs. measured accuracy (y-axis), diagonal line = perfect calibration | Quarterly survey join |
| Cost-of-quality | Stacked bar: compute cost + human correction cost, per month | Monthly aggregation table |

The override-rate chart is worth calling out specifically: annotating it with deployment events (a prompt change, a model upgrade) is what turns a number into a diagnosis. A spike in override rate that lines up exactly with a shipped prompt change is a much stronger signal than the raw rate alone — the same instinct as annotating a P&L chart with the dates of strategy changes.

**Development cycles — yes, genuinely 2-3 separate sprints**

| Sprint | Deliverable | Why it has to come in this order |
|---|---|---|
| 1. Instrumentation | Event schemas + logging code wired into every touchpoint (login, query, review-action) | Cannot aggregate data that was never captured — the one true hard dependency |
| 2. Aggregation pipeline | Scheduled jobs computing the four families from raw events into summary tables | Needs real event data flowing from Sprint 1 to test against |
| 3. Dashboard | The actual PM-facing UI reading Sprint 2's output | Trivial once Sprint 2's tables exist — usually the fastest of the three sprints, which surprises people who assume the dashboard is "the product" |

A common and costly mistake is building the dashboard first, against fake/hardcoded data, and only later discovering the real event data needed for it was never actually captured cleanly. Instrumentation is the layer that's expensive to retrofit — a dashboard is cheap to redo.

**What this means honestly for Project 1:** there is exactly one real, buildable piece of this today — Sprint 1's schema design, already started (the `TraceEvent` taxonomy, plus the `human_action` field carried forward from the base lesson). Sprints 2 and 3 genuinely require multi-user data that a single-user portfolio project cannot honestly produce. The strongest, most senior move is to build a small, clearly-labeled synthetic dataset (a script generating plausible multi-week, multi-user event logs) and then build a *real, working* Sprint 2 (aggregation job) and Sprint 3 (dashboard) against that synthetic data — not fabricating a metric, but demonstrating the full pipeline works mechanically, with labeling making clear the inputs are synthetic.

---

### Q&A #2

**Question asked:** "yes. And give me all files again. Before you do that answer below query. So product metrics are a captured via product code as far as possible so that they are automated. So this is a product development team's responsibility as a deliverable in production. Where do these product metrics get stored? databaase? Wouldnt the constant database read/writes slow down the entire system/platform?"

**Answer given:**

Yes — and the short answer is: product metrics never touch the same database, or even the same read/write path, as the agent's live execution. This is a real, well-established separation in data engineering, and it maps almost exactly onto something already known from a trading-systems background.

**The analogy: OLTP vs. OLAP**

In a trading system, the order management system (OMS) that actually routes and fills orders is a completely different database from the risk/analytics warehouse a PM or risk manager queries the next morning. These are two different categories of database, built for opposite workloads:

| | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |
|---|---|---|
| Optimized for | Fast, small, frequent writes; one row at a time | Fast reads over huge volumes; aggregations, group-bys |
| Example in trading | The OMS that logs and routes live orders | The end-of-day risk/analytics data warehouse |
| Example in this system | The agent's live execution path (tool calls, memo generation) | The metrics/aggregation store from Layer 2 |
| Touched by a live user request? | Yes — this is the critical path | Never directly — always a batch copy |

The core discipline: metrics writes must never sit on the critical path of a live user request, and metrics reads must never query the live/operational database. Both directions matter.

**The write side — why synchronous writes are the actual danger**

If the agent code did something like "generate memo → synchronously write a row to the metrics database → return response to user," the user's response time becomes dependent on the metrics database's health and speed. If that database is slow, has a lock, or is briefly down, every user-facing request gets slower or fails — for a concern (analytics) that has nothing to do with whether the memo itself was correct. That's a real production incident pattern, and it's avoidable.

The standard fix is asynchronous, decoupled logging:

| Pattern | How it works | Trade-off |
|---|---|---|
| Fire-and-forget / buffered write | The event is appended to an in-memory buffer or local log file immediately (sub-millisecond), and a separate background process flushes the buffer to durable storage periodically | Simple; small risk of losing the last few unflushed events if the process crashes |
| Message queue (e.g., a queue like Kafka, SQS, or similar) | The application publishes the event to a queue and moves on immediately; a separate consumer process reads from the queue and writes to storage whenever it can | More durable, more infrastructure to run; standard at real production scale |

Either way, the user's request returns without waiting on the metrics write to complete. A useful mental model: writing a metrics event should cost the user-facing request roughly the same as appending one line to a text file — because in the simplest version, that's literally what it is. The P1-LA12 decision to hand-roll `TraceEvent` and write it to a local JSON-lines file is already this pattern, just at single-user scale where a background flush process isn't even necessary yet.

**The read side — why the dashboard never queries raw events live**

This is the other half of the "layer 3 never touches layer 1 directly" rule. If the dashboard tried to compute "override rate this week" by scanning every raw event row every time a PM opens the page, that's the read-side equivalent of the same problem — a slow, expensive query competing for the same database resources as the live system, and getting slower as event volume grows over months. Layer 2's aggregation job exists specifically to absorb that cost once, on a schedule, so the dashboard's query is always cheap.

**So, concretely, where does this live?**

| Data | Storage | Why this choice |
|---|---|---|
| Raw events (Layer 1) | An append-only event store — a log file, a dedicated "events" table, or a proper event-streaming system at real scale | Writes are simple appends, never updates — the cheapest possible write pattern, and matches the access pattern of the aggregation job (read everything since last run) |
| Aggregated summaries (Layer 2 output) | A small, separate "metrics_summary" table, physically distinct from both the raw events store and the agent's own operational database | Tiny relative to raw events — this is what makes dashboard reads cheap |
| Dashboard | Reads only the summary table | Never sees raw events at all |

**Direct answer:** yes, constant reads/writes against a shared live database absolutely would slow the platform down if done naively — and that's exactly why real systems don't do it that way. The separation into an async, off-critical-path write and a pre-aggregated, physically separate read path is the standard answer, and it's the same instinct as never running a heavy risk report directly against the live order-routing database.

---

**Deliverable:** This notes file (P1_LE2_AI_Product_Metrics_and_KPIs.md)
**Estimated time:** 1-2 hours (original lesson) + follow-up discussion on production instrumentation architecture (full Q&A preserved verbatim in the appendix above)
