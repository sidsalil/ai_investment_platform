# P1-Arch-4: Module Structure and Interfaces

**Completed:** 2026-07-22
**Phase:** Phase 2 (Architecture & Design) — final lesson, 5/5
**Deliverable:** Skeleton of Python file/function signatures (no implementation)

---

## 1. What is a "module," and why does structure matter?

A **module** in Python is one file (`.py`) that does one coherent job. A **package** is a folder of related modules, marked as a package by containing an `__init__.py` file.

**Analogy:** a trading desk's systems aren't one monolithic application handling order routing, risk checks, market data, compliance, and reporting in a single file. Each is a separate, independently testable component with a defined job and a defined way of talking to the others. If the market data vendor changes, you swap that one component; the risk engine doesn't need to know or care.

This lesson turns the P1-Arch-1 architecture diagram's *boxes* into actual files, and the *arrows between boxes* into actual function signatures.

**Why this matters beyond tidiness:**

| Reason | Trading-desk equivalent |
|---|---|
| You can change one module without breaking others, as long as the interface (signature) doesn't change | Swapping your market data vendor doesn't require rewriting the risk engine, as long as the price feed format is unchanged |
| Multiple people (or Claude Code + you) can work on different modules in parallel | Different desks build their own systems against an agreed FIX spec, without waiting for each other |
| A reviewer (or interviewer) can understand the *shape* of the system from file/folder names alone, before reading logic | An architecture review reads a system diagram before reading source code |
| Tests can target one module in isolation | Unit-testing the risk engine's VaR calc doesn't require a live market data connection |

---

## 2. What is an "interface," and why design it before writing logic?

An interface, at the code level, is a **function signature**: the function's name, its parameter names and types, and its return type — with no body, or a body that just says `pass`. It's a promise about the *shape* of an exchange, without committing to *how* that exchange happens internally.

**Analogy:** a FIX message specification or REST API contract. Two counterparties agree "field 55 (Symbol) is a string, field 44 (Price) is a decimal, field 38 (OrderQty) is an integer" *before* either side writes matching-engine or order-router code. Once the contract is locked, teams build independently and in parallel — and a contract review can catch a missing or wrong field before anyone writes the internal logic that would make the mistake expensive to fix.

Example signature, read left to right:

```python
def compute_ic(factor_scores: pd.Series, forward_returns: pd.Series, method: str = "pearson") -> float:
    ...
```

Function name `compute_ic`; takes `factor_scores` (must be a pandas Series), `forward_returns` (must also be a pandas Series), an optional `method` defaulting to `"pearson"`; promises to return a single `float`.

**Important nuance:** Python type hints like `-> float` are **not enforced at runtime** by plain Python — nothing crashes if the function actually returns a string. They're read by your editor (VS Code) and by a static-checking tool, **mypy**, which scans code *without running it* and flags mismatches. This differs from a **Pydantic model**, which *does* enforce field types at runtime, at construction time — which is precisely why `FactorSpec` and its siblings are Pydantic models rather than plain function-signature-style objects: they're the "hard" contracts that cross real trust boundaries (LLM output → validated object, subagent handoff), while plain function signatures are the "soft," reviewer-facing contracts inside your own trusted code.

| | Function type hints | Pydantic model |
|---|---|---|
| Enforced at runtime? | No (advisory only) | Yes (raises `ValidationError`) |
| Checked by | mypy / your editor, statically | Python itself, at object-construction time |
| Used for | Contracts between your own functions | Contracts crossing a trust boundary (LLM output, user input, subagent handoff) |
| Analogy | Internal desk convention: "always pass price as a Decimal" | A clearing firm's message validator that actually rejects a malformed trade |

Today's "skeleton of file/function signatures, no implementation" deliverable lives entirely in the first column.

---

## 3. Repo directory structure

Turning the P1-Arch-1 component inventory (UI → orchestrator → yfinance MCP data layer → factor calc/portfolio construction/factor metrics native tools → validation subagent → memo subagent → tracing layer → product metrics subsystem) into files, consistent with the two folder names already anchored in `curriculum.md` (`shared/data/` for P1-Build-1, `modules/01_factor_research/` for P1-Build-2):

```
ai_investment_platform/
├── shared/
│   └── data/
│       ├── __init__.py
│       └── mcp_server.py          # P1-Build-1 — the ONLY MCP server in the system (P1-Arch-1 MCP-scope decision)
│
├── modules/
│   └── 01_factor_research/
│       ├── __init__.py
│       ├── schemas.py             # ALL six Pydantic models — flat at top level, shared by all three subpackages below
│       │
│       ├── pipeline/              # deterministic (P1-Arch-1 classification)
│       │   ├── __init__.py
│       │   ├── factor_calc.py         # P1-Build-2, P1-Build-3
│       │   ├── portfolio_construction.py  # P1-Build-4
│       │   ├── backtest.py            # P1-Build-5
│       │   ├── factor_metrics.py      # P1-Build-6
│       │   └── research_pipeline.py   # glue: run_research_pipeline() — the ONE native tool call (P1-Arch-2)
│       │
│       ├── agents/                # agentic (P1-Arch-1 classification)
│       │   ├── __init__.py
│       │   ├── orchestrator.py        # P1-Build-7
│       │   ├── validator_subagent.py  # P1-Build-8
│       │   └── memo_subagent.py       # P1-Build-9
│       │
│       └── observability/         # cross-cutting — instruments both of the above (P1-Arch-1's third category)
│           ├── __init__.py
│           ├── tracing.py             # P1-Build-10 — TraceEvent schema + logger
│           └── product_metrics.py     # P1-LE2's capture→aggregate→present, async, OLAP-side
│
├── ui/
│   └── streamlit_app.py           # P1-Build-13
│
└── tests/
    └── 01_factor_research/
        ├── test_factor_calc.py
        ├── test_portfolio_construction.py
        ├── test_factor_metrics.py
        └── test_schemas.py
```

**Why `shared/data/` sits outside `modules/`:** direct structural payoff of the P1-Arch-1 MCP-scope decision. The yfinance MCP server is the one component explicitly designed for reuse — Project 2 swaps it for Polygon.io. Placing it outside `01_factor_research` means that swap touches one folder that was never module-specific to begin with. Burying it inside `modules/01_factor_research/` would misleadingly imply the data layer belongs to Project 1 alone.

**Why `schemas.py` is one file, not six:** resolves a carried-forward item from P1-LA4 — "`FactorSpec` (and later any other structured objects) should be defined in a single shared schemas/models module, not duplicated per file." Every pipeline stage imports from `schemas.py`; nobody redefines `ValidationResult` locally inside `validator_subagent.py`. Same discipline as a firm-wide data dictionary: one canonical definition, not five slightly-different local copies.

**Why `pipeline/`, `agents/`, and `observability/` subpackages, added as a same-day follow-up refinement:** a subpackage boundary should mirror a real distinction someone would reason about as a unit, not just "files that feel related." This project already has exactly that distinction, locked at P1-Arch-1: every component is either deterministic (regular Python, unit-tested) or agentic (LLM-driven, eval-tested), drawn as two visually distinct box types on the architecture diagram. Reflecting that same split in the folder tree means a reader gets the classification for free from the directory structure, rather than having to re-derive it from file names.

**Deliberate non-choice, worth naming explicitly — no separate `metrics/` subpackage.** P1-Arch-1 went out of its way to flag that "metrics" is two unrelated concepts sharing a word: factor metrics (IC, Sharpe, drawdown — a synchronous pipeline stage) and product metrics (the PM-dashboard-feeding, async, cross-cutting subsystem). Grouping `factor_metrics.py` and `product_metrics.py` into one `metrics/` folder would recreate exactly the conflation that distinction was designed to prevent. `factor_metrics.py` stays in `pipeline/` (it's stage 5 of the deterministic pipeline); `product_metrics.py` stays in `observability/` (it's fed only by tracing, per P1-Arch-1's diagram rule that it never connects directly to the orchestrator or subagents).

**Why `schemas.py` doesn't get its own subpackage:** it's imported *by* all three subpackages — `pipeline/` needs `FactorSpec`/`FactorMetricsResult`, `agents/` needs all six models, `observability/` needs `TraceEvent`. Nesting it inside any one subpackage would force the other two to reach into a sibling package for a shared dependency, which is backwards — a shared dependency sits above the things that depend on it, not alongside them.

**Optional polish, not required for Phase 2 completion:** a subpackage's `__init__.py` can re-export its main entry point, e.g. `agents/__init__.py` re-exporting `run_orchestrator`, so callers write `from modules.factor_research.agents import run_orchestrator` instead of reaching into `agents.orchestrator` directly. Flagged here so it doesn't need rediscovering later; not a blocking decision.

---

## 4. Finalizing the six schemas

### 4a. `FactorSpec` — finalized, plus new `exclusion_criteria` field

**Open question resolved:** P1-Arch-2 surfaced a real gap — a hypothesis like "test value, but exclude value traps" has no honest home in the schema. `exclusion_months` is purely numeric and momentum-specific (skip the most recent N months of the lookback). A qualitative exclusion isn't a number.

**Decision and reasoning:** add `exclusion_criteria: list[str] | None = None` to capture this — but the P1 pipeline does **not** mechanically filter on it. Building a real "value trap detector" (e.g., screening on negative earnings growth, high leverage) is quantitative-screening work out of scope for a factor research copilot's P1 build. The dishonest move would be to silently drop the exclusion criteria the user asked for, or accept them while pretending they were applied. The honest move — consistent with every disclosure decision since P1-L2 — is to capture it structurally, never silently swallow it, and force it to be disclosed as an unimplemented gap. This is enforced by a new sixth row in the validator's check table (§4d) and guaranteed visible in the memo via the existing `disclosed_flags` audit.

```python
class FactorSpec(BaseModel):
    hypothesis_text: str
    factor_type: Literal["momentum", "volatility", "liquidity", "value"]
    universe: Literal["NASDAQ100", "SP500"]
    lookback_months: int = Field(ge=1)
    exclusion_months: int = Field(default=0, ge=0)
    exclusion_criteria: list[str] | None = None   # NEW — captured, not yet operationalized
    rebalance_frequency: Literal["monthly", "weekly", "daily"] = "monthly"
    long_short: bool = True
```

**Worked example — the "value trap" hypothesis, now representable honestly:**

| Field | Value |
|---|---|
| `hypothesis_text` | `"Test value, but exclude value traps"` |
| `factor_type` | `"value"` |
| `universe` | `"NASDAQ100"` |
| `lookback_months` | `12` |
| `exclusion_months` | `0` |
| `exclusion_criteria` | `["value traps"]` |
| `rebalance_frequency` | `"monthly"` |
| `long_short` | `True` |

This round-trips cleanly through Pydantic validation. Nothing about "value traps" is lost between extraction and the rest of the pipeline — it's honestly labeled, at the validator stage, as a request the pipeline received but did not act on.

### 4b. `FactorMetricsResult` — finalized from the P1-Arch-2 provisional sketch

```python
class FactorMetricsResult(BaseModel):
    ic_mean: float
    ic_tstat: float
    rank_ic_mean: float
    hit_rate: float = Field(ge=0, le=1)
    sharpe: float
    sortino: float
    max_drawdown: float                # negative, e.g. -0.23 for a 23% drawdown
    calmar: float
    beta_to_market: float
    beta_long_leg: float
    beta_short_leg: float
    turnover_cost_drag_bps: float
    holdout_split: Literal["in_sample", "out_of_sample", "holdout"]
```

**Why `hit_rate` gets `Field(ge=0, le=1)` but `sharpe` doesn't get a bound:** hit rate is a proportion — mathematically impossible to be outside [0, 1], so Pydantic can enforce that as a hard runtime guarantee (like a FIX field with a documented valid range). Sharpe ratio has no such natural bound — a Sharpe of -3 or +8 is unusual but not *invalid* — so bounding it would enforce a business rule as if it were a data-type rule, the wrong layer for that check (that's the validator subagent's job, not the schema's).

**Worked example:**

| Field | Value | Read as |
|---|---|---|
| `ic_mean` | `0.034` | Weak-but-real average monthly rank correlation |
| `ic_tstat` | `2.1` | Below the 3.0 Harvey-Liu-Zhu bar (P1-LB3) — flaggable |
| `rank_ic_mean` | `0.031` | Close to Pearson IC, no major nonlinearity |
| `hit_rate` | `0.54` | 54% of months, factor beat the median |
| `sharpe` | `0.71` | |
| `sortino` | `0.95` | |
| `max_drawdown` | `-0.18` | |
| `calmar` | `0.79` | |
| `beta_to_market` | `0.12` | Close to market-neutral |
| `beta_long_leg` | `0.98` | |
| `beta_short_leg` | `0.86` | |
| `turnover_cost_drag_bps` | `42.0` | 42 bps/year eaten by the 10bps flat cost assumption |
| `holdout_split` | `"out_of_sample"` | This result object is the OOS run, not the holdout |

### 4c. `RunMetadata` — finalized

```python
class RunMetadata(BaseModel):
    variants_tested: int = Field(ge=1)
    holdout_touched: bool
    universe_wide_zscore_diff: float | None
    walk_forward_window_type: Literal["rolling", "expanding"]
```

**Worked example (Branch 1 from P1-Arch-3's two-branch trace):**

| Field | Value |
|---|---|
| `variants_tested` | `3` |
| `holdout_touched` | `False` |
| `universe_wide_zscore_diff` | `None` |
| `walk_forward_window_type` | `"rolling"` |

Three variants tested, no correction applied — this is exactly the input that trips the validator's "undisclosed multiple testing" row into `severity="blocking"`.

### 4d. `ValidationResult` — finalized, six-row check table (was 5, now 6)

```python
class ValidationResult(BaseModel):
    passed: bool
    flags: list[str]
    severity: Literal["none", "advisory", "blocking"]
```

| # | Condition checked | Source lesson | Severity |
|---|---|---|---|
| 1 | Single best-period IC reported without IR/t-stat | P1-L6 / P1-LB3 | advisory |
| 2 | `variants_tested > 1` with no multiple-testing correction | P1-LB3 | blocking |
| 3 | Holdout touched more than once, or touched then changed | P1-LB2 | blocking |
| 4 | Sharp universe-wide vs. sector-neutral z-score divergence | P1-L4 | advisory |
| 5 | Novel-factor framing without Harvey-Liu-Zhu t>3.0 acknowledgment | P1-LB3 | advisory |
| **6 (new)** | **`FactorSpec.exclusion_criteria` is non-`None`** | **P1-Arch-4** | **advisory — "exclusion criteria captured but not operationalized in this pipeline version"** |

**Worked example, full object:**

```python
ValidationResult(
    passed=True,
    flags=["exclusion criteria captured but not operationalized in this pipeline version"],
    severity="advisory"
)
```

### 4e. `MemoResult` — finalized

```python
class MemoResult(BaseModel):
    memo_markdown: str
    disclosed_flags: list[str]
    word_count: int = Field(ge=0)
```

**Worked example, and the audit check it enables:**

```python
MemoResult(
    memo_markdown="## Research Memo: 12-Month Momentum, NASDAQ-100\n...",
    disclosed_flags=["exclusion criteria captured but not operationalized in this pipeline version"],
    word_count=612
)
```

Mechanical audit, run before this reaches the UI:

```python
assert set(memo_result.disclosed_flags) >= set(validation_result.flags)
```

If the memo subagent silently dropped that flag — plausible, since it's a lower-stakes "advisory" item competing against a "blocking" item in the same list — this assertion fails and the run halts on a structural check, not on hoping a human reader catches it.

### 4f. `SubagentCallResult` — a real discriminated union

**The problem with the old sketch:** `result: ValidationResult | MemoResult | None` is a plain (non-discriminated) union. It type-checks, but nothing tells Python — or a future reader — which of the two types to expect for a given `agent` value without inspecting the object at runtime. Equivalent to a FIX field that could be an order or a cancel, with no MsgType tag telling you which.

**The fix — a discriminated union.** Put the "which type am I" flag *inside* each variant as a `Literal`, and let Pydantic use that field to pick the right shape automatically:

```python
class ValidatorCallResult(BaseModel):
    agent: Literal["validator_subagent"]
    status: Literal["ok", "failed"]
    retries_used: int = Field(ge=0)
    result: ValidationResult | None
    error_summary: str | None

class MemoCallResult(BaseModel):
    agent: Literal["memo_subagent"]
    status: Literal["ok", "failed"]
    retries_used: int = Field(ge=0)
    result: MemoResult | None
    error_summary: str | None

SubagentCallResult = Annotated[
    ValidatorCallResult | MemoCallResult,
    Field(discriminator="agent"),
]
```

**Why this is worth the extra ceremony:** with a plain union, `result.recommendations` (a made-up field on neither type) can't be caught by your editor or mypy — they don't know which branch you're in. With the discriminated union, the moment code checks `if call_result.agent == "validator_subagent":`, both your editor and mypy *narrow* the type automatically and know `call_result.result` is a `ValidationResult`, catching a typo'd field access before the code ever runs. This is the direct code-level payoff of "proper discriminated union" — a real reliability improvement, not decoration.

**Worked example, mapping onto the three-way A/B/C outcome distinction locked in P1-Arch-3:**

| Outcome | `agent` | `status` | `retries_used` | `result` | `error_summary` |
|---|---|---|---|---|---|
| A (invisible internal retry, then success) | `"validator_subagent"` | `"ok"` | `2` | `ValidationResult(...)` | `None` |
| B (terminal failure) | `"validator_subagent"` | `"failed"` | `3` | `None` | `"Malformed severity value after 3 retries: 'critical'"` |
| C (successful call, bad news) | `"validator_subagent"` | `"ok"` | `0` | `ValidationResult(passed=False, severity="blocking", ...)` | `None` |

B and C are structurally similar at a glance — which is exactly why the **B-vs-C distinction must live in `status`, not be inferred from `result`**: a human or code skimming this object must be able to tell "the call itself broke" from "the call worked and reported something bad" without opening `result` and reasoning about its contents.

---

## 5. Function signatures, module by module

### `shared/data/mcp_server.py`

```python
async def get_price_history(tickers: list[str], start_date: date, end_date: date) -> dict[str, pd.DataFrame]: ...
async def get_universe_constituents(universe: Literal["NASDAQ100", "SP500"], as_of_date: date) -> list[str]: ...
async def get_sector_classification(tickers: list[str]) -> dict[str, str]: ...
```

`async def` because MCP tool calls are I/O-bound network requests — a preview of a concept not yet formally covered (async I/O), flagged as a carried-forward item for P1-Build-1, not taught in full today since it's an implementation concern, not an interface-design one.

### `modules/01_factor_research/pipeline/factor_calc.py`

```python
def compute_raw_factor(price_panel: pd.DataFrame, factor_type: Literal["momentum", "volatility", "liquidity", "value"], lookback_months: int, exclusion_months: int = 0) -> pd.Series: ...
def winsorize(raw_factor: pd.Series, lower_pct: float = 0.01, upper_pct: float = 0.99) -> pd.Series: ...
def sector_neutral_zscore(winsorized_factor: pd.Series, sector_map: dict[str, str]) -> pd.Series: ...
def universe_wide_zscore(winsorized_factor: pd.Series) -> pd.Series: ...   # diagnostic-only, per P1-L4
```

The locked signal pipeline order — raw → winsorize → sector-neutral z-score — is now visible directly in the function names, in the order they'd naturally be called. A good interface makes the intended call order legible without a separate doc.

### `modules/01_factor_research/pipeline/portfolio_construction.py`

```python
def bucket_into_quintiles(zscored_factor: pd.Series, n_buckets: int = 5) -> pd.Series: ...
def build_long_short_weights(bucketed: pd.Series) -> pd.Series: ...
def build_long_only_weights(bucketed: pd.Series) -> pd.Series: ...
```

### `modules/01_factor_research/pipeline/backtest.py`

```python
def chronological_three_way_split(data: pd.DataFrame, touch_holdout: bool = False) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: ...
def walk_forward_backtest(factor_spec: FactorSpec, price_panel: pd.DataFrame, window_type: Literal["rolling", "expanding"]) -> pd.DataFrame: ...
def apply_transaction_costs(returns: pd.DataFrame, turnover: pd.Series, cost_bps: float = 10.0) -> pd.DataFrame: ...
```

`chronological_three_way_split`'s `touch_holdout: bool = False` default makes the "structurally awkward to touch casually" holdout-protection decision concrete at the interface level. Calling this function without explicitly passing `touch_holdout=True` returns only the train/validation split; the holdout slice cannot be reached by accident.

### `modules/01_factor_research/pipeline/factor_metrics.py`

```python
def compute_ic(factor_scores: pd.Series, forward_returns: pd.Series, method: Literal["pearson", "spearman"] = "pearson") -> float: ...
def compute_factor_metrics(backtest_results: pd.DataFrame, split: Literal["in_sample", "out_of_sample", "holdout"]) -> FactorMetricsResult: ...
```

### `modules/01_factor_research/pipeline/research_pipeline.py` — the corrected signature

**A real gap caught here, not just a restated sketch.** P1-Arch-2 sketched `run_research_pipeline(factor_spec: FactorSpec) -> FactorMetricsResult`. But `RunMetadata` (introduced later, at P1-Arch-3) has to be produced by this same native pipeline code — it's the only place that actually knows `variants_tested` and `holdout_touched` as the run happens. A signature returning only `FactorMetricsResult` has nowhere to put that data. The provisional signature was correct when written, before `RunMetadata` existed — this lesson catches that it's now stale and fixes it:

```python
def run_research_pipeline(factor_spec: FactorSpec) -> tuple[FactorMetricsResult, RunMetadata]: ...
```

This is exactly the kind of gap interface-first design is supposed to catch cheaply, on paper, rather than discovering mid-P1-Build-7 that a function needs a second return value bolted on after it's already written and tested.

### `modules/01_factor_research/agents/orchestrator.py`

```python
def extract_factor_spec(user_query: str) -> FactorSpec: ...
def invoke_validator_subagent(factor_spec: FactorSpec, factor_metrics_result: FactorMetricsResult, run_metadata: RunMetadata) -> SubagentCallResult: ...
def invoke_memo_subagent(factor_spec: FactorSpec, factor_metrics_result: FactorMetricsResult, validation_result: ValidationResult) -> SubagentCallResult: ...
def run_orchestrator(user_query: str) -> MemoResult | ValidationResult: ...
```

`run_orchestrator`'s return type, `MemoResult | ValidationResult`, is a small but honest design choice: it states at the type level that the run either finishes with a memo, or finishes by handing back the blocking verdict itself — matching P1-Arch-3's Branch 1 (`severity="blocking"` → run returns `ValidationResult` directly to the UI, no memo produced). A caller reading this signature knows to handle both cases without reading the function body.

### `modules/01_factor_research/agents/validator_subagent.py`

```python
def validate_methodology(factor_spec: FactorSpec, factor_metrics_result: FactorMetricsResult, run_metadata: RunMetadata) -> ValidationResult: ...
```

### `modules/01_factor_research/agents/memo_subagent.py`

```python
def generate_memo(factor_spec: FactorSpec, factor_metrics_result: FactorMetricsResult, validation_result: ValidationResult) -> MemoResult: ...
```

### `modules/01_factor_research/observability/tracing.py`

```python
class TraceEvent(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None
    agent: Literal["orchestrator", "validator_subagent", "memo_subagent"]
    iteration: int
    event_type: Literal["perceive", "reason", "act", "observe", "escalation", "subagent_invocation", "subagent_result"]
    timestamp: datetime
    content: dict
    latency_ms: float
    token_count: int

def log_event(event: TraceEvent) -> None: ...
```

`TraceEvent` was already fully locked at P1-LA12 — placed in its own module because it's the concrete implementation of a cross-cutting concern (per P1-Arch-1, tracing instruments every other component), earning its own file rather than living inside `orchestrator.py`.

### `modules/01_factor_research/observability/product_metrics.py`

```python
def aggregate_trace_events(trace_log_path: Path) -> pd.DataFrame: ...
```

Deliberately one function today. This module's design (capture → aggregate → present, OLTP/OLAP separation) was locked at P1-LE2; today's job is just to give it a physical home, consistent with P1-Arch-1's rule that this subsystem connects only to the tracing layer, never directly to the orchestrator.

---

## 6. Full worked trace: threading types through every interface

**Request:** "Test 12-month momentum on the NASDAQ-100." No exclusions, one variant tested, no prior holdout use.

**Step 1**
- Module path: `modules/01_factor_research/agents/orchestrator.py`
- Function called: `extract_factor_spec("Test 12-month momentum on the NASDAQ-100")`
- Input: `str`
- Output: `FactorSpec(factor_type="momentum", universe="NASDAQ100", lookback_months=12, exclusion_criteria=None, ...)`

**Step 2**
- Module path: `modules/01_factor_research/pipeline/research_pipeline.py`
- Function called: `run_research_pipeline(factor_spec)`
- Input: `FactorSpec`
- Output: `(FactorMetricsResult(ic_mean=0.041, ...), RunMetadata(variants_tested=1, holdout_touched=False, ...))`

**Step 2 (internal calls)** — everything `run_research_pipeline` calls under the hood, before returning
- Module path: `shared/data/mcp_server.py` → `modules/01_factor_research/pipeline/factor_calc.py` → `.../pipeline/portfolio_construction.py` → `.../pipeline/backtest.py` → `.../pipeline/factor_metrics.py`
- Function called: `get_price_history(...)` → `compute_raw_factor(...)` → `winsorize(...)` → `sector_neutral_zscore(...)` → `bucket_into_quintiles(...)` → `build_long_short_weights(...)` → `walk_forward_backtest(...)` → `apply_transaction_costs(...)` → `compute_factor_metrics(...)`
- Input: chained pandas objects, never entering Step 3's context
- Output: `FactorMetricsResult`

**Step 3**
- Module path: `modules/01_factor_research/agents/orchestrator.py` (caller) → `.../agents/validator_subagent.py` (callee)
- Function called: `invoke_validator_subagent(...)` → `validate_methodology(...)`
- Input: `FactorSpec, FactorMetricsResult, RunMetadata`
- Output: `ValidatorCallResult(agent="validator_subagent", status="ok", result=ValidationResult(passed=True, flags=[], severity="none"))`

**Step 4**
- Module path: `modules/01_factor_research/agents/orchestrator.py` (caller) → `.../agents/memo_subagent.py` (callee)
- Function called: `invoke_memo_subagent(...)` → `generate_memo(...)`
- Input: `FactorSpec, FactorMetricsResult, ValidationResult`
- Output: `MemoCallResult(agent="memo_subagent", status="ok", result=MemoResult(memo_markdown="...", disclosed_flags=[], word_count=580))`

**Step 5**
- Module path: `modules/01_factor_research/agents/orchestrator.py`
- Function called: `run_orchestrator(...)` returns
- Input: —
- Output: `MemoResult` (final object reaching the UI)

Steps 3 and 4 each show two paths because that's the one place in the trace where control crosses from `agents/orchestrator.py` into a different file within the same subpackage — both are worth having visible rather than collapsing to one.

Every function above is a real, typed function signature from Section 5 — not illustrative prose.

---

## 7. What "skeleton compiles" means, practically

The Phase 2 completion criterion is "your skeleton compiles, even if functions just `pass`." Concretely, once these files are typed into the repo:

```python
def compute_ic(factor_scores: pd.Series, forward_returns: pd.Series, method: Literal["pearson", "spearman"] = "pearson") -> float:
    pass
```

This imports cleanly, and running `mypy modules/` checks every *call site* against these signatures even though nothing runs correctly yet — catching, for example, a future P1-Build-7 line calling `compute_ic(factor_scores, forward_returns, "spearman", extra_arg=5)` as a type error before any real math is written. That is the whole point of interface-first design: cheap mistakes now, not expensive ones during Phase 3.

---

## Summary of decisions locked this lesson

1. **Repo directory structure locked** — full file tree in Section 3, consistent with the `shared/data/` and `modules/01_factor_research/` conventions already anchored in `curriculum.md`.
2. **Same-day follow-up: `modules/01_factor_research/` split into three subpackages** — `pipeline/` (deterministic), `agents/` (agentic), `observability/` (cross-cutting) — directly mirroring the P1-Arch-1 deterministic-vs-agentic classification rather than an arbitrary grouping. `schemas.py` stays flat at the top level since all three subpackages depend on it. Deliberately no `metrics/` subpackage — `factor_metrics.py` (pipeline stage) and `product_metrics.py` (cross-cutting subsystem) stay separated per P1-Arch-1's explicit "two unrelated concepts sharing a word" distinction.
2. **`FactorSpec` gains `exclusion_criteria: list[str] | None = None`** — captured, never silently dropped, but explicitly not operationalized by the P1 pipeline. Closes the P1-Arch-2 Stage 1 schema-coverage-gap item.
3. **`FactorMetricsResult` finalized** as a 13-field Pydantic model with types (Section 4b).
4. **`RunMetadata` finalized** as a 4-field Pydantic model with types (Section 4c).
5. **`ValidationResult` finalized**, and its check table extended from 5 to 6 rows — new row 6 flags non-`None` `exclusion_criteria` as advisory (Section 4d).
6. **`MemoResult` finalized** as a 3-field Pydantic model (Section 4e).
7. **`SubagentCallResult` rebuilt as a proper Pydantic discriminated union** — `ValidatorCallResult | MemoCallResult` on an `agent: Literal[...]` discriminator, replacing the loose `ValidationResult | MemoResult | None` sketch (Section 4f).
8. **`run_research_pipeline` signature corrected** from the stale P1-Arch-2 provisional sketch (`-> FactorMetricsResult`) to `-> tuple[FactorMetricsResult, RunMetadata]`, since native pipeline code — not the validator — is the only place that can track `RunMetadata`'s fields as the run happens (Section 5).
9. **Full function-signature skeleton locked** for every module in the repo (Section 5), with a worked end-to-end type trace (Section 6).

**Phase 2 (Architecture & Design) is now complete: 5/5.** Next: Phase 3 (Build Sprints), starting with P1-Build-1 (yfinance MCP server, in `shared/data/`).

---

## Carried-forward action items surfaced this lesson

- **(P1-Arch-4) → P1-Build-1 through P1-Build-10:** all module import paths in Section 5 now include the subpackage (e.g. `from modules.01_factor_research.pipeline.factor_calc import ...`, `from modules.01_factor_research.agents.orchestrator import ...`, `from modules.01_factor_research.observability.tracing import ...`). `schemas.py` imports stay flat: `from modules.01_factor_research.schemas import FactorSpec`.

- **(P1-Arch-4) → P1-Build-1:** `get_price_history`, `get_universe_constituents`, `get_sector_classification` are specified as `async def` in the skeleton. Async I/O itself has not yet been taught as a concept — cover the basics (why I/O-bound network calls benefit from `async`/`await`, how it differs from the sequential model used everywhere else in the pipeline) at the start of P1-Build-1, before implementing the MCP server.
- **(P1-Arch-4) → P1-Build-7:** implement `run_orchestrator`'s `MemoResult | ValidationResult` return-type branching exactly as specified — callers must handle both cases explicitly, not assume a memo is always produced.
- **(P1-Arch-4) → P1-Build-7/8:** native pipeline code (`run_research_pipeline`) must produce and return `RunMetadata` alongside `FactorMetricsResult`, per the corrected signature — `variants_tested` incremented on every distinct factor/lookback configuration run in a session, `holdout_touched` set once `chronological_three_way_split(..., touch_holdout=True)` is called.
- **(P1-Arch-4) → P1-Build-8:** validator system prompt must encode all six check-table rows from Section 4d, including the new row 6 (non-`None` `exclusion_criteria` → advisory disclosure).
- **(P1-Arch-4) → P1-Build-7/8:** implement `SubagentCallResult` as the discriminated union specified in Section 4f (`ValidatorCallResult` / `MemoCallResult` on an `agent` discriminator), not a loose `Union`. Confirm the pattern works as expected with a quick `mypy` check once both variant classes exist.
- **(P1-Arch-4) → P1-Build-1/5/6:** `chronological_three_way_split`'s `touch_holdout: bool = False` default must be preserved exactly as designed — no call site should default to `True`.
- **(P1-Arch-4), open item, not resolved → future revisit only if needed:** `exclusion_criteria` is currently permanently unoperationalized for P1. If a target role's interview conversation specifically probes "how would you extend this," the honest answer is: define a small closed vocabulary of exclusion rule types (e.g., `"negative_earnings_growth"`, `"high_leverage"`) as a new Literal, and add a genuine filtering step to `factor_calc.py` — not in scope for the current build sprints, flagged here only so the gap is never rediscovered as a surprise.
