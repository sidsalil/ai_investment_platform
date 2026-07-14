# P1-LA4: Structured Outputs & Schema Validation

**Completed:** 2026-07-14
**Track:** AI/Agentic (4th lesson, 4/17)

---

## 1. The problem this lesson solves

Picture this from a Product Manager background: you ask an analyst to "email me your trade rationale" versus handing them a trade ticket with fixed fields (ticker, side, quantity, price, settlement date). The email is fine for a human reader — but if you wanted a downstream system to automatically book that trade, free text is useless. Two analysts describing the identical trade might write "buy 100 AAPL at market" and "purchase one hundred shares of Apple, market order" — same meaning, completely different text, and no code can reliably act on either without a human (or another AI) re-interpreting it every single time.

This is exactly the problem Project 1's orchestrator has. A user types: *"test 12-month momentum on the NASDAQ-100, excluding the most recent month."* Somewhere downstream, the factor-calculation module (P1-Build-2) is plain Python code. It doesn't want a sentence — it wants a fixed set of typed values: which universe, how many months of lookback, how many months excluded, what rebalance cadence. If the Large Language Model (LLM) — the underlying AI model, like Claude — just hands back a paragraph, nothing downstream can consume it reliably.

**Structured outputs** are the fix: instead of letting the model respond however it wants, you force its answer into a fixed, machine-readable shape.

---

## 2. What "structured output" actually means

A structured output is model-generated data that conforms to a predefined, machine-parseable format — almost always JSON (JavaScript Object Notation), the same format already covered in P1-LA2/LA3 as the shape of tool schemas, `tool_use` blocks, and `tool_result` blocks. The difference here: in P1-LA2/LA3, JSON structured the model's *tool-calling* behavior. In this lesson, JSON structures the model's *final answer*.

| | Free text output | Structured (JSON) output |
|---|---|---|
| Same request | "Test twelve-month momentum on the Nasdaq 100, skip the last month" | `{"factor_type": "momentum", "universe": "NASDAQ100", "lookback_months": 12, "exclusion_months": 1}` |
| Can a human read it? | Yes, easily | Yes, but less naturally |
| Can Python code consume it directly? | No — requires a second parsing/interpretation step, which itself is unreliable | Yes — `json.loads()` gives a dict with fixed key names and types |
| Wording variation across requests | High (different phrasing → different text every time) | None (field names and types are fixed regardless of phrasing) |
| Failure visibility | Silent — wrong interpretation just produces a wrong downstream result with no error | Visible — a malformed field raises an explicit, catchable error |

---

## 3. JSON Schema, revisited

Recall from P1-LA2: a tool's `input_schema` is written in JSON Schema (JavaScript Object Notation Schema) format — it's a *contract* specifying field names, types, and which fields are required, so the model knows exactly what a valid tool call looks like before it ever generates one.

Structured outputs use the identical contract idea, just pointed at the model's *response* instead of its *tool call*. Two parties — the model producing the answer, and the Python code consuming it — agree in advance on the exact shape of the data. Neither has to guess, and neither can quietly drift from the agreement without the system noticing.

---

## 4. Pydantic — what it actually is

**Pydantic** is a Python library that lets you describe a schema as an ordinary Python class, with each field given a type annotation. Handing Pydantic some data (typically a dict, e.g. straight from a model's JSON output) causes it to automatically check that data against the class definition — raising a specific, pinpointed error if something doesn't match, or handing you back a fully-typed Python object if everything checks out.

**Analogy:** Pydantic is the compliance-checklist step in a trade-booking system. A trade ticket has fixed fields (ticker, side, quantity, price, settlement date), each with an expected type. If a ticket comes in with `quantity: "ten thousand"` (text instead of a number) or a blank settlement date, the system rejects it at the door — before it ever enters the books — rather than letting a malformed trade slip through and cause problems three steps downstream. Pydantic does exactly this rejection-at-the-door check, for Python data instead of trade tickets.

**Worked example — a minimal Pydantic model:**

```python
from pydantic import BaseModel

class TradeTicket(BaseModel):
    ticker: str
    quantity: int
    price: float
```

| Input handed to `TradeTicket(...)` | What happens |
|---|---|
| `{"ticker": "AAPL", "quantity": 100, "price": 201.50}` | Succeeds. Returns an object where `.quantity` is guaranteed to be a real Python `int`, `.price` a real `float`. |
| `{"ticker": "AAPL", "quantity": "100", "price": 201.50}` | Succeeds — Pydantic performs reasonable *coercion*: the string `"100"` can be unambiguously converted to the int `100`. |
| `{"ticker": "AAPL", "quantity": "one hundred", "price": 201.50}` | **Fails.** Pydantic cannot coerce `"one hundred"` to an integer. Raises a `ValidationError` naming exactly the field (`quantity`) and exactly why it failed ("value is not a valid integer"). |
| `{"ticker": "AAPL", "price": 201.50}` | **Fails.** `quantity` is a required field with no default — missing entirely. Error names the missing field. |

The key behavior to hold onto: Pydantic doesn't just silently accept whatever it's given — it either hands you back trustworthy, correctly-typed data, or it tells you precisely what's wrong. There is no silent middle ground where bad data slips through looking fine.

---

## 5. The building blocks of a Pydantic schema

| Building block | What it does | Example |
|---|---|---|
| Required field | No default — must be present or validation fails | `ticker: str` |
| Optional field / default | Field can be omitted; falls back to a stated default | `settlement_days: int = 2` |
| Closed set of allowed values (`Literal`) | Restricts a field to an exact enumerated list — anything outside it fails validation | `side: Literal["buy", "sell"]` |
| Nested model | A field whose value is itself another Pydantic model, for grouped sub-data | `counterparty: Counterparty` (where `Counterparty` is its own `BaseModel`) |
| Numeric constraints | Bounds beyond just "is it a number" | `quantity: int = Field(ge=1)` (must be ≥ 1) |

**Worked example — extending `TradeTicket` with these blocks:**

```python
from pydantic import BaseModel, Field
from typing import Literal

class Counterparty(BaseModel):
    name: str
    lei_code: str  # Legal Entity Identifier

class TradeTicket(BaseModel):
    ticker: str
    quantity: int = Field(ge=1)
    price: float
    side: Literal["buy", "sell"]
    settlement_days: int = 2
    counterparty: Counterparty
```

If a ticket comes in with `"side": "short"`, validation fails immediately — `"short"` isn't in the allowed `Literal["buy", "sell"]` set — even though `"short"` is a perfectly normal English word. This is the mechanism's whole point: it enforces the *specific* vocabulary your system has agreed to support, not just "is this a string."

---

## 6. How this connects to LLM output specifically — two mechanisms

Getting a model to actually produce data matching a Pydantic schema happens one of two ways:

| | **Mechanism A: Prompt + parse** | **Mechanism B: Tool-call-based extraction** |
|---|---|---|
| How it works | Tell the model in the prompt: "respond only with JSON matching this schema," then `json.loads()` the response text and hand it to Pydantic | Define a "tool" (per P1-LA2's five-step cycle) whose sole purpose is to accept the structured answer as its input — no real function runs behind it; the application just reads the `tool_use` block's input directly as the structured object |
| Model behavior | Model generates free text that is *supposed* to be pure JSON | Model is already in "fill out these exact parameters" mode, the same mechanism it uses for real tool calls |
| Common failure | Model adds conversational filler around the JSON ("Sure, here's the spec: {...}"), breaking a naive `json.loads()` | Rare — the tool-calling mechanism is inherently schema-constrained at generation time |
| Where the schema lives | Described in the prompt text (and/or generated from the Pydantic model via `model_json_schema()`) | Passed as the tool's `input_schema` — literally the same JSON Schema object Pydantic can auto-generate |
| Robustness | Lower — an extra parsing step is a second point of failure | Higher — schema-awareness happens at generation time, not just checked after the fact |

**Practical takeaway for Project 1:** Mechanism B (reusing the tool-use machinery from P1-LA2/LA3 purely for extraction, not execution) is generally the more robust route, because it makes the model schema-aware *while generating*, rather than hoping free text happens to come out parseable. Which one to actually implement is left as an open item for P1-Build-7 (see Section 10) — both are viable, and it's worth testing.

---

## 7. The FactorSpec — Project 1's first structured-output object

This is the concrete object the orchestrator (P1-Build-7) will produce from a natural-language hypothesis, before any factor math happens.

| Field | Type | Constraint | Example value |
|---|---|---|---|
| `hypothesis_text` | `str` | required | `"test 12-month momentum on the NASDAQ-100, excluding the most recent month"` |
| `factor_type` | `Literal["momentum", "volatility", "liquidity", "value"]` | required, closed set (matches the factors actually planned in P1-Build-2/3) | `"momentum"` |
| `universe` | `Literal["NASDAQ100", "SP500"]` | required (matches the P1-L2 universe decision) | `"NASDAQ100"` |
| `lookback_months` | `int` | required, `ge=1` | `12` |
| `exclusion_months` | `int` | default `0`, `ge=0` | `1` |
| `rebalance_frequency` | `Literal["monthly", "weekly", "daily"]` | default `"monthly"` (matches the P1-L7 decision) | `"monthly"` |
| `long_short` | `bool` | default `True` (matches the P1-L5 research-default decision) | `true` |

**Worked example — success case:**

User query: *"test 12-month momentum on the NASDAQ-100, excluding the most recent month"*

Model (via mechanism A or B) produces:
```json
{"hypothesis_text": "test 12-month momentum on the NASDAQ-100, excluding the most recent month",
 "factor_type": "momentum", "universe": "NASDAQ100",
 "lookback_months": 12, "exclusion_months": 1,
 "rebalance_frequency": "monthly", "long_short": true}
```
Pydantic validates this cleanly → downstream code receives a typed `FactorSpec` object. `spec.lookback_months` is guaranteed to be a real Python `int` (`12`), not a string that might say `"twelve"` — every downstream module can rely on that without re-checking.

**Worked example — failure case:**

Same query, but the model (mis-)produces `"rebalance_frequency": "biweekly"`. `"biweekly"` is not in `Literal["monthly", "weekly", "daily"]`. Pydantic raises a `ValidationError` naming the exact field and the exact allowed values — not a generic crash, a precise diagnostic.

---

## 8. What happens on a validation failure — the retry pattern (preview of P1-LA9)

A validation failure is not a dead end. The application catches the `ValidationError` and, rather than showing the user a stack trace, feeds the *specific error message* back to the model as a new turn: *"Your last output failed validation: rebalance_frequency must be one of ['monthly', 'weekly', 'daily'], you gave 'biweekly'. Please correct and resend."* The model gets another attempt, now armed with the exact reason it failed.

This mirrors the "loop back to step 2" behavior from P1-LA2's five-step tool-use cycle — except here the loop is validation-driven rather than tool-execution-driven. The corrective detail (naming the exact field and the exact allowed values) is what makes the retry useful; a vague "try again" would give the model far less to work with.

**What this lesson does *not* cover:** what happens if validation keeps failing after 2, 3, 5 attempts — that's a reliability failure mode, covered in full in P1-LA9 (retry caps, backoff, escalation-to-human-or-error). This lesson only establishes that a validation failure is recoverable and specific, not that it's handled indefinitely.

---

## 9. Why this matters architecturally

Every handoff in Project 1's planned pipeline is a schema boundary:

**Orchestrator → FactorSpec → factor-calc/portfolio-construction modules → backtest results → validator subagent → memo subagent**

If any one of these handoffs used free text instead of a validated structured object, small wording drift (e.g., "NASDAQ 100" vs. "Nasdaq-100" vs. "the hundred largest Nasdaq names") could silently produce a different, wrong result three steps downstream — with no error, no warning, nothing to debug against. Structured outputs turn a "hope the words line up" handoff into a "the code physically cannot proceed with malformed data" handoff. This is the same interface/contract discipline that exists in ordinary software engineering between two systems, just applied here to the human-language-to-code boundary specifically.

Direct tie to the validator subagent (P1-Build-8): because `FactorSpec` is a typed Pydantic object, the validator can check `spec.rebalance_frequency == "monthly"` or `spec.factor_type == "momentum"` directly as ordinary Python — it never has to re-parse or re-interpret free text to do its job. This materially simplifies that build sprint.

---

## 10. Decisions locked this lesson

1. **`FactorSpec` will be implemented as a Pydantic model** (fields per Section 7 table above), produced by the orchestrator in P1-Build-7, and used as the typed contract between the orchestrator and every downstream module.
2. **Validation failures use a retry-with-feedback pattern**: on `ValidationError`, the specific error message is fed back to the model as a new turn rather than failing the request outright. A retry cap (exact number TBD) will be set in P1-LA9/P1-Build-7 — not decided yet, just the pattern.
3. **Choice between Mechanism A (prompt + parse) and Mechanism B (tool-call-based extraction) is deferred to P1-Build-7 implementation time** — both are viable; worth testing both against real prompts before locking one in.

---

## Carried-forward action items surfaced this lesson

- **(P1-LA4) → P1-Build-7 (orchestrator):** Implement `FactorSpec` as a Pydantic model with fields `hypothesis_text`, `factor_type` (Literal), `universe` (Literal), `lookback_months` (int, ge=1), `exclusion_months` (int, default 0, ge=0), `rebalance_frequency` (Literal, default "monthly"), `long_short` (bool, default True). Use Pydantic's `model_json_schema()` method to auto-generate the target schema handed to the model (whether via Mechanism A prompt text or Mechanism B tool `input_schema`).
- **(P1-LA4) → P1-Build-7:** Implement a retry-with-feedback loop on `ValidationError` — feed the specific error message back to the model as a new turn rather than failing the request immediately. Cap the number of retries (exact number to be decided) before escalating — this cap-and-escalate behavior is covered in full in P1-LA9.
- **(P1-LA4) → P1-LA9 (agent failure modes — reliability):** Revisit the malformed-output/validation-failure failure mode in full depth, including retry-cap and escalation behavior. This lesson only introduces the retry pattern at an intuition level.
- **(P1-LA4) → P1-Build-8 (methodology validator subagent):** Validator can operate directly on `FactorSpec`'s typed fields (e.g., `spec.rebalance_frequency`, `spec.factor_type`) rather than parsing free text — simplifies that build sprint materially.
- **(P1-LA4) → P1-Arch-4 (module structure):** `FactorSpec` (and later any other structured objects, e.g. a validator result or memo metadata object) should be defined in a single shared schemas/models module, not duplicated per file, so field-type decisions live in one place.
- **(P1-LA4) → P1-Build-7 (open question, not yet resolved):** Choice between Mechanism A (prompt + parse) and Mechanism B (tool-call-based extraction) for producing `FactorSpec` — deferred to implementation time; worth testing both against real prompts.
