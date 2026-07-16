# AI Investment Platform - Curriculum

> Living curriculum for the (now 2-project) journey to AI Product Manager /
> Financial Services PM / Forward Deployed Engineer conversations.
> Last updated: 2026-07-15 (P1-LA12 complete — Observability & tracing for
> agentic systems — AI/Agentic track now 12/17. P1-LA11, AI governance and
> human-in-the-loop design, P1-LA10, Agent security & adversarial failure
> modes, P1-LA9, Agent failure modes (reliability), P1-LA8, Context
> engineering, and P1-LA7, Subagents & multi-agent orchestration, also
> completed 2026-07-15. On 2026-07-14, P1-LA5 completed,
> Finance track hit 10/10
> complete, and the AI/Agentic and Evals tracks were expanded — see
> "AI/Agentic and Evals track expansion" note below)
>
> **Superseded a 4-project plan.** Old versions preserved as
> `curriculum_OLD_2026-05-25.md` (pre-restructure) and
> `curriculum_OLD_2026-07-12.md` (progress through P1-L5, old single-track
> structure — this file merges that progress into the new structure).
> Projects 3-4 kept below as reference only — not in active scope.
>
> **AI/Agentic and Evals track expansion (2026-07-14):** Before starting the
> AI/Agentic track, reviewed the original 14-lesson plan against current
> (2026) AI PM hiring signal — governance, accountability, and security are
> now consistently flagged as the top differentiators for AI PM roles in an
> agentic-AI market, not just tool-use/orchestration mechanics. Added three
> lessons to close that gap: split the original "Agent failure modes" lesson
> into a reliability half (LA9) and a new security/adversarial half (LA10);
> added a new governance and human-in-the-loop design lesson (LA11), which
> directly extends the model-risk-awareness pattern already established in
> the Finance track (P1-L2, P1-L8, P1-L9); and added a new fine-tuning vs.
> prompting vs. RAG decision-framework lesson (LA16). Also added a second
> Evals-track lesson (LE2) on AI product metrics/KPIs, distinct from LE1's
> model-evals-vs-system-evals framing — LE1 asks "does the pipeline work,"
> LE2 asks "how does a PM know the product is succeeding." AI/Agentic track
> grew from 14 to 17 lessons; Evals track grew from 1 to 2 lessons. No
> lessons in either track were complete at the time of this expansion, so
> lessons were renumbered in place rather than appended out of order.
>
> **Scope change rationale:** collapsed from 4 projects to 2 to trade
> breadth-across-projects for depth-within-projects, and to make room for an
> AI/agentic concept track, backtesting rigor, and evals/model-evals — none
> of which existed as explicit lessons in the original plan.
>
> **Target roles (as of 2026-07-11):** AI Product Manager, Product Manager —
> Financial Services, Forward Deployed Engineer. Standing caveat on FDE: this
> portfolio strengthens FDE *conversations* (systems design, agent debugging,
> model evals) but does not substitute for professional software engineering
> experience, which is what frontier-lab FDE hiring bars actually screen for.
> AI PM and Financial Services PM remain the primary near-term targets.

---

## How to use this document

- **Check off lessons as you complete them.** "Complete" means: concepts understood AND deliverables produced AND completion criteria met. Not "I read about it."
- **Lessons within a phase should generally be done in order.** The Finance track and AI/Agentic track within Phase 1 were designed to interleave, but the Finance track finished (10/10) before the AI/Agentic track started, so that interleaving window closed on 2026-07-14. As of this update: Finance track complete (10/10), AI/Agentic track 13/17 (P1-LA1, P1-LA2, P1-LA3, P1-LA4, P1-LA5, P1-LA6, P1-LA7, P1-LA8, P1-LA9, P1-LA10, P1-LA11, P1-LA12, P1-LA13 done), Backtesting Rigor track 0/3, Evals track 0/2. Recommend continuing straight through the AI/Agentic track (P1-LA14, Deployment basics, next), then the Backtesting Rigor and Evals tracks, before Phase 2 (Architecture) starts.
- **Time estimates assume focused work, not calendar time.**
- **Update CONTEXT.md after every lesson.** This curriculum tracks what's done; CONTEXT.md tracks where you are now.
- **One lesson ≈ one Claude conversation, typically.**
- **Don't skip the "Explain it back" checkpoints.**
- **Log hours in CONTEXT.md's Hours-Logged Tracker.** The estimate below is largely untested against your actual pace — recalibrate using real data as you go.

---

## Cross-Project Meta-Skills

| Skill | After P1 | After P2 |
|-------|----------|----------|
| Python (pandas, numpy) | Strong | Production |
| Quant finance vocabulary | Factor research + backtesting rigor | + event-driven backtesting mechanics |
| Agentic AI (tool use → orchestration) | Tool use, MCP, planning loops, subagent orchestration | Planning loop via Agent SDK, applied at production scale |
| Evaluation discipline | Model evals + system evals, regression eval suite | Strategy-quality reviewer subagent, iterating evals |
| Product thinking | Product brief, case study, systems-design writeup | Architecture maturity, robustness memo |
| Financial data handling | Time series, walk-forward, out-of-sample discipline | Multi-asset, event simulation |
| Methodology rigor | Look-ahead, survivorship, multiple-testing awareness | Full walk-forward validation, slippage/cost realism |

---

# PROJECT 1: Factor Research Copilot

**Goal:** Build an AI agent system that converts natural-language investment hypotheses into Python-based factor research with statistical validation, methodology checks, and auto-generated research memos — architected to demonstrate the full agentic pattern range (tool use, planning, multi-agent orchestration) in one system, with rigorous backtesting and both model- and system-level evals.

**Estimated effort:** ~106-149 hours *(updated 2026-07-14 for AI/Agentic and Evals track expansion)*

**Status:** In progress — Phase 1 (Concept Lessons), Finance track complete (10/10); AI/Agentic track 12/17 (P1-LA1, P1-LA2, P1-LA3, P1-LA4, P1-LA5, P1-LA6, P1-LA7, P1-LA8, P1-LA9, P1-LA10, P1-LA11, P1-LA12 done); Backtesting Rigor and Evals tracks remain before Phase 2

## Phase 1: Concept Lessons — Finance Track (~15-25 hours) — COMPLETE

### [x] P1-L1: What is a factor and why does anyone care? — **completed 2026-05-25**
- **Concepts:** What a factor is, why factor investing exists, the major historical factors (value, momentum, size), CAPM → Fama-French history
- **Deliverable:** Notes in CONTEXT.md under "Concepts Learned — Finance Track"
- **Estimated time:** 1-2 hours

### [x] P1-L2: The universe - what stocks am I testing on? — **completed 2026-05-25**
- **Concepts:** Why we restrict the universe, survivorship bias intro, the S&P 500 as a starting universe, point-in-time universe problem
- **Decision logged:** NASDAQ-100 for development → S&P 500 for final eval/demo. Survivorship bias acknowledged in P1-Polish-4.
- **Estimated time:** 1 hour

### [x] P1-L3: Returns - the foundation everything builds on — **completed 2026-07-12**
- **Concepts:** Simple vs log returns, when each is appropriate, adjusted vs raw prices (dividends, splits), total return vs price return
- **Deliverable:** Notes (P1_L3_Returns.md); a small Jupyter notebook computing both return types on AAPL data (hand-written per coding-ownership rule)
- **Decision logged:** Log returns for internal factor/backtest math; simple returns for cross-asset combination and reporting language. Adjusted close is the required default price series for all return calculations.
- **Estimated time:** 1-2 hours

### [x] P1-L4: Signal construction - turning data into predictions — **completed 2026-07-12**
- **Concepts:** Raw factors vs normalized factors, z-scoring, winsorization, sector neutralization (intuition)
- **Deliverable:** Notes (P1_L4_Signal_Construction.md); worked 8-stock numerical example covering z-scoring, winsorization, and sector-neutral z-scoring
- **Decision logged:** Signal construction pipeline order is raw factor → winsorize (1st/99th percentile default, configurable) → sector-neutral z-score. Sector-neutral z-scoring is the default signal for portfolio construction; universe-wide z-scoring retained as an optional diagnostic to detect sector-bet contamination.
- **Estimated time:** 2 hours

### [x] P1-L5: Portfolio construction from signals — **completed 2026-07-12**
- **Concepts:** Decile/quintile portfolios, long-only vs long-short, equal weighting vs signal weighting
- **Deliverable:** Notes (P1_L5_Portfolio_Construction.md); hand-computed quintile example for 20 stocks with equal-weight and signal-weight long-short portfolios
- **Decision logged:** Quintile bucketing (5 buckets) as default, deciles configurable for the S&P 500 final run. Long-short equal-weighted is the research/IC default from P1-L6 onward; long-only equal-weighted top-quintile retained as a practitioner-facing alternative for the memo. Signal-weighting retained as a configurable diagnostic.
- **Estimated time:** 1-2 hours

### [x] P1-L6: Information Coefficient and statistical evaluation — **completed 2026-07-13**
- **Concepts:** IC, rank IC, Information Ratio, hit rate, t-statistics for IC, what "predictive" actually means statistically
- **Deliverable:** Notes (P1_L6_Information_Coefficient.md); worked 10-stock example covering Pearson IC, rank IC (Spearman), hit rate, single-period and time-series t-statistics, and a 6-month IR calculation
- **Decision logged:** Rank IC (Spearman) is the primary headline metric for Project 1 reporting (robust to fat-tailed return outliers); Pearson IC retained as diagnostic. IR and time-series t-statistic (t = IR × √T) must be computed across the full backtest window rather than reported for a single period, to avoid cherry-picking.
- **Estimated time:** 2 hours

### [x] P1-L7: Factor decay and turnover — **completed 2026-07-13**
- **Concepts:** How long signals predict (1-day, 1-week, 1-month forward returns), decay curves, half-life, turnover, the turnover-cost relationship
- **Deliverable:** Notes (P1_L7_Factor_Decay_and_Turnover.md); illustrative 7-horizon decay curve worked example with half-life calculation; worked 5-stock turnover example (25% one-way turnover); turnover-cost comparison across monthly/weekly/daily rebalancing frequencies
- **Decision logged:** Rebalancing frequency locked to monthly (matches illustrative half-life ~21 trading days, matches academic convention). Forward-return window for all IC/IR metrics locked to 1-month (21 trading days), matching the rebalancing cadence. Overlapping forward-return window / autocorrelation concern (raised in P1-L6) resolved by construction — monthly rebalance matching monthly forward window means no autocorrelation-adjusted standard error is needed.
- **Estimated time:** 1-2 hours

### [x] P1-L8: The biases that kill backtests — **completed 2026-07-13**
- **Concepts:** Look-ahead bias (deep — restatement/reporting lag, point-in-time index membership, sector reclassification), survivorship bias (deep — magnitude quantification and construction mechanics), selection bias (universe, time-period, and factor/publication selection), data snooping (distinguished from multiple testing)
- **Deliverable:** Notes (P1_L8_The_Biases_That_Kill_Backtests.md); worked 5-stock survivorship-bias magnitude example (22-point illustrative bias); worked fundamentals-restatement look-ahead example (P/E 20.0x vs. look-ahead-contaminated 22.2x); worked time-period-selection IR comparison across four historical windows; worked dollar-neutral vs. beta-neutral numerical example (+0.20 net beta from a 1.30/0.90 average-beta split); a 9-row "methodology gotchas" cheat sheet mapping each bias to mitigation and residual disclosed risk
- **Decision logged:** Beta-neutral construction is explicitly out of scope for Project 1 (dollar-neutral equal-weighting from P1-L5 remains the default; residual market beta disclosed, not hedged). Survivorship bias and the yfinance delisting-return gap are documented, disclosed limitations, not solved. Project 1's factor/universe choices are framed as replication of established literature, not novel discovery, directly addressing publication bias and data snooping.
- **Estimated time:** 2-3 hours — this lesson matters more than most

### [x] P1-L9: Transaction costs and real-world frictions — **completed 2026-07-14**
- **Concepts:** Bid-ask spread (half-spread cost model), market impact (temporary vs. permanent, square-root law), commissions, total transaction cost model, the backtest-vs-live gap (implementation shortfall: fill-price idealization, execution latency, capacity constraints, crowding)
- **Deliverable:** Notes (P1_L9_Transaction_Costs_and_Real_World_Frictions.md); worked spread-cost example (10 bps spread → 5 bps one-way); worked square-root impact table (1%-25% participation → 2.0-10.0 bps); worked total-cost example (9.5 bps one-way for a $2M trade); worked capacity-decay table ($10M-$2B AUM → 6.1-14.4 bps one-way cost)
- **Decision logged:** Flat assumed 10 bps one-way transaction cost parameter (not computed from data — yfinance lacks bid/ask/execution data), configurable. Turnover-cost drag constant updated from P1-L7's 5 bps placeholder to 10 bps. Square-root impact model and AUM-scaled capacity/crowding effects understood conceptually but not implemented — logged as "what I'd build next" items.
- **Estimated time:** 1-2 hours

### [x] P1-L10: Risk and performance metrics — **completed 2026-07-14**
- **Concepts:** Sharpe ratio (and annualization), Sortino ratio (downside deviation), max drawdown, drawdown duration, Calmar ratio, beta-to-market (via covariance/variance regression)
- **Deliverable:** Notes (P1_L10_Risk_and_Performance_Metrics.md); worked 6-month Sharpe/Sortino example (annualized Sharpe ≈1.85, annualized Sortino ≈8.89); worked 8-month equity-curve max drawdown example (−16.67%) with drawdown duration (6 months peak-to-new-peak); worked Calmar example (≈0.90); worked 5-month beta-to-market regression example (β≈1.84); full metrics glossary table for the repo
- **Decision logged:** No new locked design decisions (this lesson is metric definitions, not a pipeline design choice) — open item logged for P1-Build-6: choice of market benchmark series for beta-to-market calculation not yet resolved, revisit at build time.
- **Estimated time:** 1-2 hours

## Phase 1: Concept Lessons — AI/Agentic Track (~25-31 hours)

### [x] P1-LA1: What is an LLM agent — **completed 2026-07-14**
- **Concepts:** Agent vs. chatbot vs. fixed workflow (full comparison table); the perceive-reason-act loop (perceive/reason/act/observe/repeat-or-stop), also called the agent loop, and its relation to ReAct (P1-LA5 preview) and the OODA loop (analogy only); autonomy as a spectrum (fixed workflow → single tool-use loop → ReAct loop → planning loop → multi-agent orchestration), not a binary
- **Deliverable:** Notes (P1_LA1_What_Is_An_LLM_Agent.md); worked three-way comparison of the same task ("test 12-month momentum on the NASDAQ-100") implemented as a fixed workflow, a chatbot, and a full agent, including a 7-iteration loop trace showing the agent adaptively handling an unexpected data-quality issue (3 tickers with insufficient history) without any hardcoded branch for it
- **No design decisions locked this lesson** — this is a conceptual-foundations lesson (definitions and mental models), not a pipeline design choice. First lesson of the AI/Agentic track.
- **Estimated time:** 1 hour

### [x] P1-LA2: Tool use / function calling fundamentals — **completed 2026-07-14**
- **Concepts:** How a model decides to call a tool (probabilistic pattern-matching, not deterministic dispatch), tool schemas (name, description, input_schema in JSON Schema format), the five-step request/response cycle (send message+tools → model returns tool_use or text → application executes → application sends tool_result → model gives final answer or loops again), `stop_reason` (`tool_use` vs `end_turn`), parallel vs. sequential tool calls, first look at tool-related failure modes (wrong parameters, unnecessary call, missed necessary call, hallucinated call)
- **Deliverable:** Notes (P1_LA2_Tool_Use_Function_Calling_Fundamentals.md); full worked five-step trace of a `get_price_history` tool call for a concrete AAPL price question, including exact JSON at every step
- **No new locked design decisions this lesson** — mechanics/vocabulary lesson, directly informs P1-Build-1 (tool description quality) and P1-Build-7 (orchestrator's tool-use cycle)
- **Estimated time:** 1-2 hours

### [x] P1-LA3: MCP (Model Context Protocol) — **completed 2026-07-14**
- **Concepts:** The N×M integration problem MCP solves (analogized to FIX protocol and USB-C); client/server/host architecture; the three MCP primitives (Tools, Resources, Prompts); how MCP's tool discovery (`tools/list`) and execution (`tools/call`) map onto the P1-LA2 five-step tool-use cycle without changing the model's reasoning mechanics; stdio vs. HTTP-based transport; MCP vs. bespoke integration tradeoffs; a security preview of least-privilege server scoping (full depth deferred to P1-LA10)
- **Deliverable:** Notes (P1_LA3_MCP_Model_Context_Protocol.md); full worked re-run of the P1-LA2 `get_price_history` five-step trace, now showing the added discovery step (`tools/list`) and server-side execution (`tools/call`) with exact JSON at each step; MCP-vs-bespoke-integration comparison table
- **No new locked design decisions this lesson** — protocol/architecture-mechanics lesson, directly informs the implementation approach for P1-Build-1 (MCP server) and P1-Build-7 (orchestrator as MCP client). Confirms (does not newly decide) the 2026-07-11 decision that MCP is in scope from Project 1.
- **Estimated time:** 2 hours

### [x] P1-LA4: Structured outputs & schema validation — **completed 2026-07-14**
- **Concepts:** Pydantic models, why structured outputs matter for reliability, schema validation as a guardrail; JSON Schema revisited as a producer/consumer contract; required/optional/Literal/nested/constrained Pydantic fields; two mechanisms for eliciting structured output from an LLM (prompt+parse vs. tool-call-based extraction); the validation-failure retry pattern (preview of P1-LA9)
- **Deliverable:** Notes (P1_LA4_Structured_Outputs_Schema_Validation.md); worked `TradeTicket` Pydantic examples (valid, coercible, and failing inputs); full `FactorSpec` field design for Project 1 with a worked success case and a worked validation-failure case
- **Decision logged:** `FactorSpec` will be implemented as a Pydantic model (fields: hypothesis_text, factor_type, universe, lookback_months, exclusion_months, rebalance_frequency, long_short) as the typed contract the orchestrator (P1-Build-7) produces for all downstream modules. Validation failures use a retry-with-feedback pattern (specific error fed back to the model as a new turn). Choice between prompt+parse and tool-call-based extraction mechanisms deferred to P1-Build-7 implementation time.
- **Estimated time:** 1-2 hours

### [x] P1-LA5: ReAct-style tool-use loops — **completed 2026-07-14**
- **Concepts:** The Thought/Action/Observation pattern (ReAct = "Reason + Act"); its 2022 origin as a text-scratchpad prompting technique for models without native tool-calling, vs. its modern meaning (visible reasoning before each tool call) now that tool_use/tool_result are structural; three-way comparison against reasoning-only (Chain-of-Thought) and acting-only patterns; criteria for when a single reactive loop is sufficient vs. needing a planning loop (P1-LA6); loop termination via `stop_reason: "end_turn"`; native-tool-use-vs-explicit-ReAct-prompting mechanics (system prompt vs. the API's `thinking`/adaptive-thinking parameter)
- **Deliverable:** Notes (P1_LA5_ReAct_Style_Tool_Use_Loops.md); worked momentum-test Thought/Action/Observation trace; worked typo-correction error-recovery trace; follow-up precise mapping of Thought↔Reason / Observation↔Perceive-Observe onto P1-LA1's agent loop, producing the "Thought masquerading as Observation" hallucination red-flag pattern
- **No new locked design decisions this lesson** — mechanics/vocabulary lesson. Open item: mechanism for visible orchestrator reasoning in P1-Build-7 (system-prompt instruction vs. `thinking` parameter) deferred to build time.
- **Estimated time:** 1-2 hours

### [x] P1-LA6: Planning loops — **completed 2026-07-15**
- **Concepts:** Multi-step planning vs. reactive tool use; precise definition of a planning loop (persistent plan artifact formed before execution, executed step by step, revised on downstream-assumption-invalidating observations) vs. ReAct's one-step-ahead reasoning; the reactive-trader-vs-portfolio-manager-with-a-thesis analogy; the concrete decision criterion for when an agent needs to plan ahead vs. react turn-by-turn; plan representation as a structured object parallel to P1-LA4's `FactorSpec`; the specific plan-revision trigger condition; preview of planning-specific failure modes (deferred to P1-LA9)
- **Deliverable:** Notes (P1_LA6_Planning_Loops.md); two-way worked trace of the P1-LA1/LA5 momentum task run first as pure ReAct and then as a planning loop, with an explicit plan-revision step triggered by the same 3-tickers-insufficient-history surprise; minimal JSON plan-object representation; decision-criterion table (ReAct-sufficient vs. planning-needed)
- **No new locked pipeline design decisions this lesson** — conceptual-foundations lesson (planning vs. reactive execution mental models), not a pipeline design choice. Concrete plan representation and replan-check trigger for P1-Build-7 deferred to that build sprint.
- **Estimated time:** 1-2 hours

### [x] P1-LA7: Subagents & multi-agent orchestration — **completed 2026-07-15**
- **Concepts:** A subagent defined mechanically as a separate Claude conversation invoked/returned via P1-LA2's 5-step tool-use cycle; orchestrator-worker pattern as the multi-agent point on the P1-LA1 autonomy spectrum; the plan object's new `owner` field; a five-signal decision table for when to decompose across agents (persona mismatch, independence/conflict-of-interest, context isolation, task substantiality, parallelizability) vs. keep work in one agent's loop; how results merge back as structured objects read by orchestrator code
- **Deliverable:** Notes (P1_LA7_Subagents_and_Multi-Agent_Orchestration.md); worked numerical token-accounting example (single-agent ≈56,000 total input tokens across 7 stages vs. subagent-isolated ≈31,200 tokens); the "grading your own homework" independence argument for the validator subagent specifically; full stage-by-stage ownership mapping of Project 1's architecture (orchestrator: stages 1-5; validator subagent: stage 6; memo subagent: stage 7)
- **No new locked pipeline design decisions beyond the ownership mapping** — architectural output (who owns each plan step and why), directly usable at P1-Build-7/P1-Build-8 implementation time.
- **Estimated time:** 2 hours

### [x] P1-LA8: Context engineering — **completed 2026-07-15**
- **Concepts:** Context window as fixed-size working memory; context engineering defined as deliberate design of what enters the window vs. naive concatenation; the LLM-context-vs-application-memory distinction (raw data lives in Python/pandas, never in context); context rot / "lost in the middle"; just-in-time retrieval; compaction; system prompt design (standing mandate vs. per-run specifics, via an Investment Policy Statement analogy); the decision framework for what belongs upfront vs. fetched/compacted on demand
- **Deliverable:** Notes (P1_LA8_Context_Engineering.md); two worked numerical examples (naive raw-OHLCV-in-context blowing past any viable token budget vs. ~150-250 token structured summary; naive full-transcript carryforward reaching ~12,000+ tokens by stage 7 vs. ~600 tokens using only structured handoff objects, extending P1-LA7's ~56k/~31.2k token-accounting example); full stage-by-stage context mapping for Project 1's 7-stage architecture
- **No new locked pipeline design decisions this lesson** — architectural/discipline output (what belongs in context at each stage), directly usable at P1-Build-7/P1-Build-8 implementation time. Carried-forward requirement: each stage's tool/function returns a small structured object, not a raw computation dump.
- **Estimated time:** 1-2 hours

### [x] P1-LA9: Agent failure modes (reliability)
- **Concepts:** Infinite loops, hallucinated tool calls, malformed outputs, retry/backoff strategy, timeout handling
- **Scope note (added 2026-07-14):** This lesson is now scoped to *reliability* failure modes only — things that go wrong because the agent is unreliable, not because someone is attacking it. Adversarial/security failure modes split out to P1-LA10.
- **Estimated time:** 1-2 hours

### [x] P1-LA10: Agent security & adversarial failure modes — **completed 2026-07-15**
- **Concepts:** Prompt injection (direct and indirect, e.g. malicious instructions embedded in a fetched web page or document), "excessive agency" (an agent doing more than it should because nothing technically stopped it, per OWASP's 2025 LLM Top 10 framing — LLM01 Prompt Injection, LLM06 Excessive Agency), tool-access scoping and least-privilege design ("prefer deterministic access controls over prompted instructions not to call a tool" — directly relevant to the MCP server's tool permissions in P1-Build-1), data exfiltration risk (the "confused deputy" pattern) when an agent can both read sensitive data and make outbound calls, including the documented 2024 Slack AI indirect-injection exfiltration case
- **Why this is its own lesson, not folded into LA9:** reliability failure modes are bugs; security failure modes assume an adversary. Different mental model, and increasingly a distinct interview topic as agentic systems get more autonomous.
- **Deliverable:** Notes (P1_LA10_Agent_Security_Adversarial_Failure_Modes.md); master security failure-mode cheat sheet (6 rows: direct injection, indirect injection, excessive functionality, excessive permissions, excessive autonomy, data exfiltration)
- **Decision logged:** No new locked architecture decisions — this lesson's conclusions manifest as build-sprint tool-scoping requirements for P1-Build-1/P1-Build-7/P1-Build-8 (see CONTEXT.md carried-forward action items), not new pipeline design decisions.
- **Estimated time:** 1-2 hours

### [x] P1-LA11: AI governance and human-in-the-loop design — **completed 2026-07-15**
- **Concepts:** Levels of agent autonomy (fixed workflow → single tool-use loop → planning loop → fully autonomous multi-agent system) and how required human oversight changes at each level; permission/access scoping as a governance mechanism, not just a security one; escalation and human-approval checkpoints (when should the system stop and ask a human before proceeding); accountability — who owns a decision an agent made; automation bias (the tendency to over-trust a system that's been reliable so far)
- **Why this matters for your target roles specifically:** 2026 hiring signal consistently frames governance/accountability design — not tool-use mechanics — as the top AI PM differentiator in an agentic-AI market. This is also a direct extension of the model-risk-awareness pattern already established in the Finance track (P1-L2 survivorship bias disclosure, P1-L8 bias cheat sheet, P1-L9 implementation-shortfall framing) — same instinct, applied to agent behavior instead of backtest methodology.
- **Direct project tie-in:** frame the P1-Build-8 methodology validator subagent explicitly as a governance/human-in-the-loop control (an automated check that flags issues for human review before a memo ships) — this lesson gives you the vocabulary to describe that build as "governance," not just "a subagent."
- **Deliverable:** Notes (P1_LA11_AI_Governance_Human_In_The_Loop_Design.md); master governance cheat sheet (5 rows: autonomy levels, governance-scoped permissions, escalation checkpoints, accountability roles, automation bias); escalation-checkpoint scoring framework (Consequence × Reversibility × Confidence-gap) worked against 4 P1 actions; accountability framework borrowed from financial model risk management (SR 11-7-style Owner/Developer-Operator/Independent Validator roles); automation bias illustrated via the verified 2012 Knight Capital trading-algorithm incident
- **Decision logged:** No new locked architecture decisions — this lesson's conclusions manifest as build-sprint/documentation requirements reframing existing mechanisms (validator subagent, `ValidationResult.severity` field) with governance vocabulary, not new pipeline design (see CONTEXT.md carried-forward action items)
- **Estimated time:** 1-2 hours

### [x] P1-LA12: Observability & tracing for agentic systems — **completed 2026-07-15**
- **Concepts:** Logging vs. tracing vs. monitoring as distinct terms; trace-vs-span vocabulary (OpenTelemetry); a seven-type trace event taxonomy (`perceive`, `reason`, `act`, `observe`, `escalation`, `subagent_invocation`, `subagent_result`) operationalizing the P1-LA1 Reason-vs-Perceive distinction and the P1-LA11 escalation checkpoint as first-class, visually distinct event types; a full `TraceEvent` Pydantic schema; correlation-ID (`trace_id`) pattern threading one trace across the orchestrator and both subagents
- **Deliverable:** Notes (P1_LA12_Observability_Tracing_For_Agentic_Systems.md); worked hallucination-debugging example (a `reason` event asserting an IPO date with no supporting `observe` event); worked escalation-event example pairing a blocking `ValidationResult` with an `escalation` event carrying P1-LA11's scoring fields
- **Decision logged:** `TraceEvent` schema and seven-type taxonomy locked as-is for P1-Build-7/P1-Build-8. No sampling at P1's scale (log everything, every run). No tracing UI/viewer being built — trace files inspected directly as JSON-lines.
- **Estimated time:** 1-2 hours

### [x] P1-LA13: Latency & cost tradeoffs — **completed 2026-07-16**
- **Concepts:** Token economics (input vs. output pricing asymmetry, parallel input processing vs. sequential/autoregressive output generation); the tool-use loop's context re-sending problem and superlinear cost growth with iteration count; latency components (time to first token, generation speed, serial-dependency compounding across a multi-stage pipeline); the three-way cost/latency/quality tradeoff in model selection; a two-question decision framework (task well-definedness + stakes, reusing the P1-LA11 Consequence × Reversibility × Confidence-gap framework) for when a smaller/cheaper model is appropriate
- **Deliverable:** Notes (P1_LA13_Latency_Cost_Tradeoffs.md); worked 7-iteration cost table (P1-LA1 trace) showing superlinear cost growth; worked end-to-end latency budget table (~26.5 sec, serial dependency chain); worked model-selection table applying the framework to P1's three subagents (extractor, validator, memo-writer)
- **Decision logged:** Validator subagent stays on the larger/stronger model (high-stakes escalation checkpoint per P1-LA11); factor-spec extractor and memo-writer subagent flagged as candidates for a smaller/cheaper model, pending the actual model-evals comparison (curriculum's existing "What you build" deliverable: run all three subagents on two models, compare cost/latency/quality) before the assignment is finalized.
- **Estimated time:** 1 hour

### [ ] P1-LA14: Deployment basics
- **Concepts:** Containerization intuition, environment config, basic AWS Bedrock deployment
- **Estimated time:** 2 hours

### [ ] P1-LA15: RAG fundamentals
- **Concepts:** Retrieval-augmented generation, when it's relevant to a research-copilot document-lookup use case
- **Estimated time:** 1-2 hours

### [ ] P1-LA16: Fine-tuning vs. prompting vs. RAG — **new, added 2026-07-14**
- **Concepts:** What fine-tuning actually is at an intuition level (adjusting model weights on a custom dataset vs. everything covered so far, which leaves the model's weights untouched); the decision framework for choosing between prompting, RAG, and fine-tuning for a given problem — cost, data requirements, latency, maintainability, and "is the problem really a knowledge-access problem (→ RAG) or a behavior/style/format problem (→ prompting or fine-tuning)"; why fine-tuning is rarely the first move in practice, and what would have to be true about Project 1 for it to become the right call
- **Deliverable:** A one-page decision-framework note applying the three options to 2-3 concrete Project 1 scenarios (e.g., "the factor-spec extractor keeps missing a specific phrasing pattern" or "the memo generator's tone doesn't match a target house style")
- **Estimated time:** 1-2 hours

### [ ] P1-LA17: Prompt engineering fundamentals
- **Concepts:** Few-shot examples, chain-of-thought prompting, structured prompting patterns
- **Estimated time:** 1 hour

## Phase 1: Concept Lessons — Backtesting Rigor Track (~4-6 hours)

### [ ] P1-LB1: Walk-forward validation done properly
- **Concepts:** Rolling vs. expanding windows, train/test discipline over time, why naive monthly rebalancing isn't the same as proper walk-forward validation
- **Estimated time:** 1-2 hours

### [ ] P1-LB2: Out-of-sample vs. in-sample discipline
- **Concepts:** What "out-of-sample" actually means in a backtest context, how to structure a test split for time series
- **Deliverable:** In-sample vs. out-of-sample comparison built into P1-Build-5
- **Estimated time:** 1-2 hours

### [ ] P1-LB3: The multiple-testing problem (p-hacking)
- **Concepts:** Why testing many factor variants and reporting only the best one is dishonest, correction approaches (intuition level)
- **Explain back:** "I tested momentum, volatility, and value — why can't I just report whichever had the best backtest?"
- **Estimated time:** 1-2 hours

## Phase 1: Concept Lessons — Evals & Model Evals Track (~2-4 hours)

### [ ] P1-LE1: Model evals vs. system evals
- **Concepts:** Model evals test the underlying LLM's raw capability (benchmark-style); system evals test your specific pipeline end-to-end. Why interviewers care about the distinction.
- **Sub-concepts:** LLM-as-judge methodology (and its failure modes — verbosity bias, self-preference bias); golden dataset and rubric design; eval metrics for structured/agentic output (task success rate, schema-validity rate, groundedness/faithfulness)
- **Estimated time:** 1-2 hours

### [ ] P1-LE2: AI product metrics & KPIs — **new, added 2026-07-14**
- **Concepts:** How a PM defines product-level success for an AI feature, distinct from LE1's pipeline-level evals — adoption and usage metrics, override/escalation rate (how often a human rejects or edits the agent's output — a real signal of trust and quality, not a vanity metric), trust calibration (does user trust in the system track its actual reliability, or drift ahead of/behind it), and ROI/cost-of-quality framing (cost per successful task, not just cost per API call)
- **Why this is separate from LE1:** LE1 answers "does my pipeline work" (an engineering/system question); LE2 answers "how would I know, as a PM, whether this product is succeeding in the hands of a real portfolio manager or analyst" — a distinct interview question you should be able to answer without conflating it with eval scores.
- **Deliverable:** A short metrics framework (one table) for Project 1, specifying what you'd track post-launch beyond IC/rank-IC/eval-pass-rate — e.g., how often a user overrides the validator's flag, how often the generated memo needs manual editing before use
- **Estimated time:** 1-2 hours

**Phase 1 completion criteria:**
- All Finance, AI/Agentic, Backtesting Rigor, and Evals lessons checked off
- You can explain factor research AND the agent architecture end-to-end to a non-technical friend in 10 minutes
- CONTEXT.md "Concepts Learned" sections are populated with your own-words summaries across all four tracks

## Phase 2: Architecture & Design (~7-11 hours)

### [ ] P1-Arch-1: System design
- **Deliverable:** Architecture diagram showing the major components (data layer via MCP, factor calc, portfolio construction, metrics, LLM orchestrator, validation subagent, memo subagent, tracing, UI)
- **Stored at:** `docs/architecture/project_01_factor_research.md`
- **Estimated time:** 2-3 hours

### [ ] P1-Arch-2: Data flow design
- **Deliverable:** Sequence diagram or written walkthrough: "User asks 'test momentum on S&P 500' → orchestrator plans → calls MCP tools → delegates to validation subagent → delegates to memo subagent → produces output"
- **Estimated time:** 1-2 hours

### [ ] P1-Arch-3: Orchestrator + subagent design
- **Concepts applied:** How the main agent's planning loop delegates to the validation subagent and memo-writing subagent, what gets passed between them, how failures propagate
- **Estimated time:** 2-3 hours

### [ ] P1-Arch-4: Module structure and interfaces
- **Deliverable:** A skeleton of Python file/function signatures (no implementation)
- **Estimated time:** 2-3 hours

**Phase 2 completion criteria:**
- You can draw the full architecture (including orchestrator/subagent/MCP layers) on a whiteboard from memory
- A junior developer could read your architecture doc and understand the system without asking you questions
- Your skeleton compiles (even if functions just `pass`)

## Phase 3: Build Sprints (~44-61 hours)

### [ ] P1-Build-1: Data ingestion module (MCP server)
- **What you build:** An MCP server wrapping yfinance that downloads, caches, and serves clean OHLCV data for a list of tickers — replaces a bespoke wrapper with a proper MCP tool interface
- **Key concerns:** Caching, handling failures, date alignment
- **Carried-forward requirement (from P1-L2, P1-L3):** Parameterize the universe so NASDAQ-100 ↔ S&P 500 switch is a config change. Source constituents from a stable public source (Wikipedia standard); freeze snapshot date for reproducibility. Confirm exact yfinance adjusted-close column name/behavior at implementation time. Cache invalidation must treat a new dividend/split as invalidating the entire cached adjusted-close series for that ticker.
- **Located in:** `shared/data/`
- **Tests:** Pytest tests that verify caching works and bad inputs fail cleanly
- **Estimated time:** 5-7 hours

### [ ] P1-Build-2: Factor calculation - Momentum
- **What you build:** A function that computes 12-month-minus-1-month momentum for a universe of stocks at a date
- **Key concerns:** Point-in-time correctness, NaN handling, vectorization
- **Carried-forward requirement (from P1-L4):** Winsorization (1st/99th percentile default, configurable) applied before z-scoring; sector-neutral z-scoring as the default signal path, universe-wide as diagnostic flag.
- **Located in:** `modules/01_factor_research/`
- **Estimated time:** 3-4 hours

### [ ] P1-Build-3: Factor calculation - Other factors
- **What you build:** Volatility factor (rolling std of returns), liquidity factor (dollar volume), simple value factor if data available
- **Carried-forward requirement (from P1-L4):** Same winsorization + sector-neutral z-scoring pipeline as P1-Build-2. Requires a sector classification data source (GICS sector via yfinance `.info`, or a static mapping) — confirm reliability at build time.
- **Carried-forward requirement (from P1-L8):** If a value factor uses fundamentals data, align it to the actual announcement/reporting date, not the quarter-end date, to avoid restatement-driven look-ahead bias.
- **Estimated time:** 3-4 hours

### [ ] P1-Build-4: Portfolio construction
- **What you build:** Take a factor signal at a date, build long-only quintile portfolios and long-short top-vs-bottom quintile portfolio
- **Carried-forward requirement (from P1-L5):** Default to quintile bucketing (5 buckets), configurable to deciles. Implement both long-short equal-weighted (research/IC default) and long-only equal-weighted top-quintile (practitioner-facing alternative), plus a signal-weighted option. Deterministic tie-breaking rule for stocks straddling bucket boundaries (e.g., secondary sort by ticker or market cap).
- **Carried-forward requirement (from P1-L7):** Implement monthly rebalancing as the default cadence, as a configurable parameter (not hardcoded) so alternate frequencies can be tested as a diagnostic.
- **Note (from P1-L8):** Long-short construction here is dollar-neutral equal-weighted only; beta-neutral construction is explicitly out of scope for Project 1.
- **Estimated time:** 3-4 hours

### [ ] P1-Build-5: Backtest mechanics (+ in-sample/out-of-sample)
- **What you build:** Walk forward in time, rebalance portfolio monthly, accumulate returns, apply transaction costs, and explicitly surface in-sample vs. out-of-sample performance side by side
- **Key concerns:** No look-ahead bias, realistic costs, proper walk-forward structure (per P1-LB1/LB2)
- **Carried-forward requirement (from P1-L9):** Implement a flat, configurable transaction cost parameter (default 10 bps one-way) applied to traded value at every rebalance via cost drag = turnover × cost_bps_per_unit_turnover. Do not attempt to compute spread/impact from yfinance data (not available) — flat assumption is a deliberate, disclosed simplification.
- **Estimated time:** 5-7 hours - **the hardest build sprint**

### [ ] P1-Build-6: Metrics calculation
- **What you build:** Compute IC, decile spreads, Sharpe, drawdown, turnover from backtest results
- **Carried-forward requirement (from P1-L6):** Implement Pearson IC, rank IC (Spearman), and hit rate at each rebalance date; implement IR and the time-series t-statistic aggregated across the full backtest window, not per-period. Primary forward-return window is 1-month (21 trading days), matching the monthly rebalance cadence.
- **Carried-forward requirement (from P1-L7):** Implement IC calculation at multiple forward-return horizons (1-day, 1-week, 1-month, 2-month, 3-month, 6-month) to produce an empirical decay curve as a diagnostic artifact, plus a half-life calculation (horizon where IC first falls to ≤50% of its shortest-horizon value). Implement turnover calculation (Σ|weight_new − weight_old| / 2) at every rebalance date for both long and short legs; feed into a simple cost-drag estimate ahead of the full transaction-cost treatment in P1-Build-5/P1-L9.
- **Estimated time:** 2-3 hours

### [ ] P1-Build-7: LLM integration - Natural language → factor spec (orchestrator)
- **What you build:** The main orchestrator agent's planning loop: takes "test 12-month momentum on the S&P 500," produces a structured FactorSpec object, plans the sequence of tool calls needed
- **Key concept:** Structured outputs, schema validation, planning loop (per P1-LA6)
- **Estimated time:** 4-6 hours

### [ ] P1-Build-8: Methodology validator (subagent)
- **What you build:** A validation subagent, delegated to by the orchestrator, that flags suspicious factor specs (look-ahead suspects, unrealistic assumptions, statistical/multiple-testing concerns)
- **This is your AI PM/FDE differentiator** — shows you understand model risk and multi-agent delegation
- **Carried-forward requirement (from P1-L4):** Flag signals where the universe-wide z-score and sector-neutral z-score diverge sharply for many stocks in the same direction — a diagnostic for a signal that's really a disguised sector bet.
- **Carried-forward requirement (from P1-L6):** Flag reporting of a single best-period IC without an accompanying IR/time-series t-statistic as a p-hacking-adjacent red flag.
- **Carried-forward requirement (from P1-L8):** Flag a single-window backtest report (no comparison across historical sub-periods) as a time-period-selection-bias red flag.
- **Estimated time:** 5-6 hours

### [ ] P1-Build-9: Research memo generator (subagent)
- **What you build:** A memo-writing subagent, delegated to by the orchestrator, that takes backtest results and generates a 1-page research memo with hypothesis, methodology, results, limitations
- **Estimated time:** 4-5 hours

### [ ] P1-Build-10: Tracing / observability layer
- **What you build:** Logging for every tool call and agent decision, so you can debug and explain *why* the agent did what it did
- **Estimated time:** 2-3 hours

### [ ] P1-Build-11: Model comparison eval
- **What you build:** Run the extractor/validator/memo-writer subagents on two different models (e.g., larger vs. smaller Claude model), compare cost, latency, and quality — your model-evals artifact in practice
- **Estimated time:** 2-3 hours

### [ ] P1-Build-12: Deployment
- **What you build:** Containerize the system and deploy to a hosted endpoint (AWS Bedrock), not just local
- **Estimated time:** 3-5 hours

### [ ] P1-Build-13: Streamlit UI
- **What you build:** Web interface where user types a question, sees factor running, gets charts + memo
- **Estimated time:** 4-6 hours

**Phase 3 completion criteria:**
- You can run the full pipeline end-to-end: type a question → orchestrator plans → MCP tools execute → validator subagent runs → memo subagent runs → get charts + memo
- All build sprints have working code with at least one test each
- The validator catches at least 5 different methodology mistakes you've intentionally seeded
- The system is reachable via a live hosted endpoint, not just local code

## Phase 4: Polish & Ship (~13-20 hours)

### [ ] P1-Eval: Build the regression eval set
- **What you build:** 25 natural-language prompts, each with an expected factor spec output, re-runnable as a regression suite whenever prompts/models change. Includes the model-comparison results from P1-Build-11 and a paragraph on what production eval/monitoring would look like.
- **Deliverable:** `docs/eval_reports/project_01_factor_extraction_eval.md`
- **Estimated time:** 3-5 hours

### [ ] P1-Polish-1: Product brief
- **What you write:** 2-page PRD covering problem, user, workflow before/after, solution, success metrics
- **Deliverable:** `docs/product_briefs/project_01_factor_research.md`
- **Note (from P1-L8):** Frame the project explicitly as replication of established, heavily-retested factor literature (momentum, and value if built), not as novel factor discovery.
- **Estimated time:** 2-3 hours

### [ ] P1-Polish-2: README
- **What you write:** Professional README with problem statement, demo, architecture, how to run, limitations, what you learned
- **Deliverable:** `modules/01_factor_research/README.md`
- **Estimated time:** 1-2 hours

### [ ] P1-Polish-3: Demo video
- **What you record:** 5-7 minute screen recording: state the problem, show the workflow, walk through architecture, highlight one design decision
- **Estimated time:** 1-2 hours

### [ ] P1-Polish-4: Methodology risk memo
- **What you write:** Honest accounting of what your project does NOT do (point-in-time data, survivorship bias, no slippage modeling)
- **Carried-forward requirement (from P1-L2, P1-L3, P1-L5):** Include explicit "Universe choice and survivorship-bias acknowledgment" section, expected magnitude, production fix path. Note yfinance's unreliable delisting-return capture. Note the long-only vs long-short distinction and why long-short is used for research validity.
- **Carried-forward requirement (from P1-L8):** Add explicit sections for look-ahead bias (restatement/reporting lag, index membership, sector reclassification), selection bias (universe and time-period choices), data snooping framing, and the dollar-neutral vs. beta-neutral disclosure with the worked-example numbers from P1-L8 (the +0.20 net beta example). Use the P1-L8 "methodology gotchas" cheat sheet table as direct source material for this memo.
- **Carried-forward requirement (from P1-L9):** Add a "Transaction cost model" section (flat-bps assumption, component breakdown, why it's a data-driven simplification not an oversight) and a separate "Backtest-vs-live gap (implementation shortfall)" section (fill-price idealization, execution latency, capacity constraints, crowding) — kept distinct from the P1-L8 research-methodology bias sections.
- **Estimated time:** 1 hour

### [ ] P1-Polish-5: Case-study one-pager
- **What you write:** One page: problem → user → key tradeoff decisions (universe choice, subagent orchestration vs. single loop, model selection for cost/latency) → what you'd build next
- **Carried-forward requirement (from P1-L8):** Beta-neutral construction (not implemented in P1) is a legitimate "what I'd build next" talking point.
- **Carried-forward requirement (from P1-L9):** Square-root market impact modeling (with real execution/TAQ data) and AUM-scaled capacity-curve modeling are both legitimate "what I'd build next" talking points.
- **Estimated time:** 1-2 hours

### [ ] P1-Polish-6: Systems-design writeup
- **What you write:** The kind of doc you'd whiteboard through in an interview — agent architecture, MCP layer, subagent delegation, and the failure modes you handled.
- **Estimated time:** 2-3 hours

**PROJECT 1 COMPLETION CRITERIA:**
- All lessons (four Phase-1 tracks) + builds + polish items checked off
- Working demo someone else can run from your README, plus a live hosted endpoint
- Demo video recorded
- Product brief, README, eval report, risk memo, case study, systems-design writeup all in your repo
- Repo pushed to GitHub, ready for portfolio link
- You can explain the project — including the agent architecture and eval methodology — to a hiring manager in 5 minutes with no notes

**Resume bullet earned:**
> Built an agentic AI Factor Research system (planning-loop orchestrator + subagent delegation via MCP) that converts natural-language investment hypotheses into Python-based factor tests with IC analysis, walk-forward validation, decile returns, transaction-cost sensitivity, model-comparison evals, and automated research memos with methodology risk caveats.

---

# PROJECT 2: Backtesting Copilot

**Goal:** AI-assisted strategy backtesting where users describe strategies in natural language and get rigorous, event-driven backtests with realistic frictions, automated quality review, and benchmark comparison — the systems-engineering complement to Project 1.

**Estimated effort:** ~57-84 hours *(updated 2026-07-15 — added a model-routing lesson/architecture/build addition, see below)*

**Status:** Not started

**Prerequisites:** Project 1 complete (or Phase 3 substantially complete); understanding of factor research, returns, transaction costs, walk-forward validation

> **Model-routing addition (2026-07-15):** Evaluated curriculum fit against a
> Perplexity Product Manager posting (general PM role, not Forward Deployed
> Engineer — corrected framing from an earlier assumption). Gap identified:
> the entire curriculum calls a single model provider (Claude via Agent SDK),
> while the target company's product thesis is model-agnostic, multi-model
> orchestration. Added P2-L11, P2-Arch-4, and P2-Build-11 (~7-14 hours) to
> close that gap with a real, evidence-backed routing build rather than just
> conceptual fluency. A second gap — product-led growth / retention
> instrumentation — was also identified and **explicitly declined** as a
> net-new project: it would have required either fabricated usage data or a
> real user-acquisition effort disproportionate to a self-initiated portfolio
> project. Decision: speak to PLG/flywheel thinking conceptually in
> interviews if it comes up, without a dedicated build. See CONTEXT.md
> decision log for full reasoning.

## Phase 1: Concept Lessons (~10-15 hours)

### [ ] P2-L1: Backtest vs paper trading vs live
### [ ] P2-L2: Event-driven vs vectorized backtesting
- Architecture choice with major downstream implications
### [ ] P2-L3: Position sizing schemes
- Equal weight, volatility-weighted, signal-weighted, Kelly intuition
### [ ] P2-L4: Rebalancing frequency tradeoffs
### [ ] P2-L5: Transaction costs deeper
- Bid-ask, market impact, commission structures, model choices
### [ ] P2-L6: Slippage modeling
### [ ] P2-L7: Walk-forward validation (applied at engine level)
- Builds directly on P1-LB1/LB2 — now implemented inside an event-driven engine
### [ ] P2-L8: Out-of-sample testing
### [ ] P2-L9: Multiple testing problem (p-hacking) — applied
- Builds directly on P1-LB3
### [ ] P2-L10: Realistic backtest gotchas
- Timezone bugs, data quality, corporate actions, exchange holidays
### [ ] P2-L11: Model routing and multi-model orchestration
- **Added 2026-07-15** — motivated by a target-role gap analysis against a Perplexity PM posting (see CONTEXT.md decision log). Concepts: task classification before dispatch, cost/quality/latency as three competing axes, why single-vendor model lock-in is a product risk and not just a cost line item, routing-by-task-type (in scope) vs. dynamic/learned routing (explicitly out of scope for this build). Deliverable: a decision table in CONTEXT.md mapping Project 2's model-calling subtasks (strategy parsing, backtest-quality review, tear-sheet summarization) to a proposed model tier, with reasoning per row.
- **Estimated time:** 1-2 hours

## Phase 2: Architecture & Design (~6-10 hours)

### [ ] P2-Arch-1: Event-driven engine design
### [ ] P2-Arch-2: Strategy specification schema design
### [ ] P2-Arch-3: Module structure
### [ ] P2-Arch-4: Router design
- **Added 2026-07-15.** Where the router sits in the call flow (before dispatch, after subtask classification), what gets logged per decision (subtask type, model chosen, cost, latency, and later quality outcome), how it interacts with the P2-Build-6 planning loop without becoming its own agent. Deliverable: extend the P2-Arch-1 architecture diagram to show the router as a layer.
- **Estimated time:** 1-2 hours

## Phase 3: Build Sprints (~25-35 hours)

### [ ] P2-Build-1: Event loop and core engine
### [ ] P2-Build-2: Order/fill simulation with costs
### [ ] P2-Build-3: Portfolio accounting
### [ ] P2-Build-4: Multi-asset support
### [ ] P2-Build-5: Risk controls (position limits, exposure caps)
### [ ] P2-Build-6: LLM strategy parser (natural language → strategy YAML)
- Uses Claude Agent SDK planning loop — applied version of P1-LA6
### [ ] P2-Build-7: Backtest quality reviewer (subagent)
- Applied version of P1-LA7 subagent orchestration, at production-simulation scale
### [ ] P2-Build-8: Tear sheet / metrics dashboard
### [ ] P2-Build-9: Benchmark comparison
### [ ] P2-Build-10: Streamlit UI
### [ ] P2-Build-11: Model router + before/after eval comparison
- **Added 2026-07-15.** Depends on P2-Build-6 and P2-Build-7 (needs the strategy parser and quality-reviewer subagent to exist as real model-calling subtasks before routing can be applied to them). Implement the router as a function/lookup in front of the existing model calls — no new agent framework. Run the P2-Eval strategy-prompt eval set twice: once fixed on a single model (baseline), once with routing enabled. Report the delta in cost, latency, and quality (did the reviewer subagent's judgment hold up on a cheaper model or not). Decision to log: which subtasks stay on the stronger model and why, backed by the eval delta rather than assumption.
- **Estimated time:** 5-10 hours

## Phase 4: Polish & Ship (~8-12 hours)

### [ ] P2-Eval: 25 strategy prompts → expected configs eval
### [ ] P2-Polish-1: Product brief
### [ ] P2-Polish-2: README
### [ ] P2-Polish-3: Demo video
### [ ] P2-Polish-4: Robustness memo

**Resume bullet earned:**
> Built an AI Backtesting Copilot (event-driven simulation engine, Claude Agent SDK planning loop) that transforms natural-language trading strategy descriptions into executable Python backtests with transaction costs, slippage, turnover analysis, exposure controls, benchmark comparison, and an automated strategy-quality reviewer subagent.

---

# PROJECT 3: Portfolio Construction Copilot *(deprioritized 2026-07-11 — reference only)*

**Goal:** Convert natural-language portfolio constraints into optimized portfolios using multiple optimization approaches, with risk decomposition, scenario analysis, and tradeoff explanation.

**Estimated effort:** 45-60 hours | **Status:** Not started, not in active scope

<details>
<summary>Original scope (collapsed)</summary>

## Phase 1: Concept Lessons (~12-18 hours)
P3-L1 Portfolio theory basics · P3-L2 Mean-variance optimization (Markowitz) · P3-L3 Why max-Sharpe is unstable · P3-L4 Covariance estimation problems · P3-L5 Covariance shrinkage (Ledoit-Wolf) · P3-L6 Risk parity intuition · P3-L7 Risk contribution analysis · P3-L8 Constrained optimization · P3-L9 Tracking error and active risk · P3-L10 Scenario analysis and stress testing · P3-L11 VaR vs CVaR

## Phase 2: Architecture & Design (~5-7 hours)
P3-Arch-1 Optimizer abstraction · P3-Arch-2 Constraint specification language · P3-Arch-3 Module structure

## Phase 3: Build Sprints (~20-30 hours)
P3-Build-1 Equal-weight/min-variance optimizers · P3-Build-2 Max-Sharpe optimizer · P3-Build-3 Risk parity optimizer · P3-Build-4 Covariance estimation · P3-Build-5 Constraint engine · P3-Build-6 Risk decomposition · P3-Build-7 Scenario shock framework · P3-Build-8 LLM constraint extractor · P3-Build-9 Infeasible-constraint detection · P3-Build-10 Comparison/explanation layer · P3-Build-11 Streamlit UI

## Phase 4: Polish & Ship (~8-12 hours)
P3-Eval · P3-Polish-1 Product brief · P3-Polish-2 README · P3-Polish-3 Demo video · P3-Polish-4 Governance & risk-controls memo

**Resume bullet:**
> Built an AI Portfolio Construction Copilot that converts natural-language investment constraints into optimized portfolios comparing equal-weight, minimum-variance, max-Sharpe, and risk-parity allocations with covariance shrinkage, risk decomposition, scenario shocks, and infeasibility detection.

</details>

---

# PROJECT 4: ML Signal Lab *(deprioritized 2026-07-11 — reference only)*

**Goal:** AI-assisted framework for designing, running, evaluating, and governing financial machine learning experiments with rigorous validation and methodology checks.

**Estimated effort:** 50-70 hours | **Status:** Not started, not in active scope

<details>
<summary>Original scope (collapsed)</summary>

## Phase 1: Concept Lessons (~15-20 hours)
P4-L1 Why ML for finance is hard · P4-L2 Train/test/validation splits for time series · P4-L3 Walk-forward validation (deeper) · P4-L4 Rolling vs expanding windows · P4-L5 Feature engineering for time series · P4-L6 Leakage detection · P4-L7 Classification vs regression · P4-L8 Bias-variance · P4-L9 Model interpretability (SHAP) · P4-L10 Model cards · P4-L11 Overfitting detection · P4-L12 Production model monitoring

## Phase 2: Architecture & Design (~6-8 hours)
P4-Arch-1 ML pipeline design · P4-Arch-2 Experiment tracking schema · P4-Arch-3 Model card schema

## Phase 3: Build Sprints (~25-35 hours)
P4-Build-1 Feature generation · P4-Build-2 Walk-forward validation framework · P4-Build-3 Model wrappers · P4-Build-4 Leakage detector · P4-Build-5 Hyperparameter search · P4-Build-6 Model comparison framework · P4-Build-7 SHAP integration · P4-Build-8 LLM experiment design assistant · P4-Build-9 Methodology reviewer · P4-Build-10 Model card auto-generator · P4-Build-11 Streamlit dashboard

## Phase 4: Polish & Ship (~8-12 hours)
P4-Eval · P4-Polish-1 Product brief · P4-Polish-2 README · P4-Polish-3 Demo video · P4-Polish-4 ML model risk and governance memo

**Resume bullet:**
> Built an AI ML Signal Lab for financial time-series research with walk-forward validation, leakage detection, SHAP-based interpretability, AI-assisted experiment design, automated methodology review, and model card generation.

</details>

---

# MASTERY MARKERS

## Technical
- [ ] Build a Python project from empty repo to deployable, hosted demo
- [ ] Design an LLM-powered agentic system: tool use, planning loop, and multi-agent orchestration
- [ ] Design and implement an MCP server as a tool/data layer
- [ ] Write both a model eval and a system eval for an AI feature you build
- [ ] Recognize and avoid look-ahead bias, survivorship bias, multiple-testing bias, and overfitting in financial research
- [ ] Implement a non-trivial event-driven simulation correctly
- [ ] Debug an agent failure mode (loop, hallucinated call) using a tracing/observability layer
- [ ] Translate ambiguous user requests into structured specifications

## Domain
- [ ] Explain factor investing to a non-quant
- [ ] Critique a backtest for methodology errors, including multiple-testing/p-hacking
- [ ] Explain the tradeoffs between model evals and system evals
- [ ] Discuss agent architecture (tool use vs. planning vs. orchestration) intelligently

## Product/Communication
- [ ] Write a clear product brief and a one-page case study for an AI-native workflow
- [ ] Draw a full system architecture diagram (including agent/MCP layers) from memory
- [ ] Produce a 5-minute demo video that holds attention
- [ ] Explain either project in 5 minutes with no notes
- [ ] Discuss model risk, governance, evals, and limitations honestly

---

# PORTFOLIO COMPLETION & APPLICATION READINESS

Applies once Project 1 (and ideally Project 2) are substantially built. Do not wait for 100% polish across both projects before starting to apply — start once P1's build sprints are substantially done and a rough demo exists; finish polish in parallel with early-stage interview pipeline.

### [ ] Resume rewrite
- Both existing tailored resumes (AI PM version, Applied AI/Solutions Engineer version) were written assuming four shipped projects. Rewrite for the real 2-project scope with the depth this scope actually earned — one deep agentic system beats four described in a sentence each, but bullet language needs to reflect that, not just get trimmed.
- Add a third resume variant or section addressing Forward Deployed Engineer conversations specifically, leaning on systems-design writeup, agent debugging, and model-evals artifacts — without overclaiming production SWE experience.

### [ ] Live, hosted demo
- Not just local code or a video. A link an interviewer can click during the conversation. Covered by P1-Build-12 (deployment).

### [ ] STAR-format interview stories (3-5)
- Pulled from the actual build as you hit them, not written retroactively. Strong candidates: debugging an agent infinite loop, a methodology mistake the validator caught, the model-comparison tradeoff decision, a walk-forward/OOS surprise.

### [ ] One piece of public writing
- LinkedIn post or short article on one hard decision from the build (subagent design, or eval methodology). Signals communication ability for PM roles specifically.

### [ ] Fidelity-workflow translation paragraph
- For Financial Services PM roles: one paragraph connecting the copilot's design choices to a real asset-management research desk problem — domain fluency layered on top of the technical build.

### [ ] LinkedIn updates
- GitHub links, project descriptions, Featured section content — low-risk, can do now. Headline changes and Open to Work badge remain deferred per existing discreet-search preference.

### [ ] Decision point: when to start applying
- Recommended: once P1 Phase 3 (Build Sprints) is substantially complete and a rough demo exists — do not wait for full Phase 4 polish across both projects. Polish finishes in parallel with early pipeline activity.

---

# COMPLETION TRACKING

## Project status summary

| Project | Concepts | Architecture | Build | Polish | Shipped |
|---------|---------|--------------|-------|--------|---------|
| P1: Factor Research (Finance) | ☑ 10/10 | ☐ 0/4 | ☐ 0/13 | ☐ 0/6 | ☐ |
| P1: Factor Research (AI/Agentic) | ☐ 12/17 | — | — | — | — |
| P1: Factor Research (Backtesting Rigor) | ☐ 0/3 | — | — | — | — |
| P1: Factor Research (Evals) | ☐ 0/2 | — | — | — | — |
| P2: Backtesting Copilot | ☐ 0/11 | ☐ 0/4 | ☐ 0/11 | ☐ 0/5 | ☐ |
| ~~P3: Portfolio Construction~~ | deprioritized | — | — | — | — |
| ~~P4: ML Signal Lab~~ | deprioritized | — | — | — | — |

## Aggregate metrics (2-project scope)

- Total P1 lessons planned: 10 (finance) + 17 (AI/agentic) + 3 (backtesting rigor) + 2 (evals) = 32
- Total P1 build sprints planned: 13
- Total P1 polish items planned: 6
- Total P2 lessons planned: 11
- Total P2 build sprints planned: 11
- Total P2 polish items planned: 5
- **Total trackable items (active scope):** 78
- **Total estimated hours (active scope):** ~163-233 hours (~106-149 for P1, ~57-84 for P2)
- *(Updated 2026-07-14: AI/Agentic track grew from 14→17 lessons and Evals track from 1→2 lessons — see "AI/Agentic and Evals track expansion" note at the top of this document. Adds roughly 6-9 hours to the P1 estimate.)*
- *(Updated 2026-07-15: Added P2-L11, P2-Arch-4, P2-Build-11 — model routing addition, ~7-14 hours — see decision note under Project 2's goal section and CONTEXT.md decision log.)*

Update monthly:

| Month | Lessons completed | Builds completed | Polish completed |
|-------|------------------|------------------|------------------|
| 2026-05 | 2 (P1-L1, P1-L2) | 0 | 0 |
| 2026-07 | 20 (P1-L3, P1-L4, P1-L5, P1-L6, P1-L7, P1-L8, P1-L9, P1-L10, P1-LA1, P1-LA2, P1-LA3, P1-LA4, P1-LA5, P1-LA6, P1-LA7, P1-LA8, P1-LA9, P1-LA10, P1-LA11, P1-LA12) | 0 | 0 |

---

# NOTES ON THIS CURRICULUM

- Project 2 lessons are sketched at title level for now (per original plan); full content develops when you approach it. Don't try to learn it ahead of time.
- Time estimates are a first-pass estimate, not a commitment — you have zero hours logged against the new AI/agentic, backtesting-rigor, or evals tracks yet. Recalibrate using CONTEXT.md's Hours-Logged Tracker.
- This curriculum focuses on shippable, interview-ready artifacts, not "I learned X." Hiring managers care what you can do and explain, not what you read about.
- Projects 3 and 4 remain fully scoped below (collapsed) in case priorities shift again later — no work needed to revive them, just uncollapse and resume.
