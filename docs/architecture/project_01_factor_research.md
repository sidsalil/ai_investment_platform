# Project 1: Factor Research Copilot — System Architecture

**Status:** Locked 2026-07-20 (P1-Arch-1); layout tuned in draw.io same day
**Repo location:** `docs/architecture/project_01_factor_research.md` (this file), `docs/architecture/project_01_factor_research.drawio` (canonical editable source), `docs/architecture/P1_Arch1_architecture_diagram.png` (rendered image, embedded below)

---

## Component inventory

| Component | Job | Type | Invoked via |
|---|---|---|---|
| UI (Streamlit) | Takes user hypothesis, shows memo + product metrics dashboard | Entry/exit point | User interaction |
| LLM Orchestrator | Runs perceive → reason → act → observe loop; plans and delegates | Agentic | Invoked by UI per request |
| Data layer (yfinance MCP server) | Serves price history, universe constituents, sector classification | Deterministic, external resource | MCP tool-use protocol |
| Factor calc module | Raw factor → winsorize (1st/99th pctile) → sector-neutral z-score | Deterministic | Native tool call (not MCP) |
| Portfolio construction module | Quintile bucketing; long-short equal-weighted (research default) / long-only top-quintile (practitioner alternative) | Deterministic | Native tool call (not MCP) |
| Factor metrics module | Information Coefficient (IC), Rank IC, t-statistic, hit rate | Deterministic | Native tool call (not MCP) |
| Validation subagent | Independent methodology review (p-hacking, look-ahead, multiple-testing checks) | Agentic, fresh context | `subagent_invocation` |
| Memo subagent | Writes research memo in house style/tone | Agentic | `subagent_invocation` |
| Tracing/observability layer | Records all `perceive`/`reason`/`act`/`observe`/`escalation`/`subagent_invocation`/`subagent_result` events, correlation-ID (`trace_id`) threaded | Deterministic, cross-cutting | Instruments every other component |
| Product metrics subsystem | Capture → aggregate → present usage/trust/cost-of-quality metrics for PM dashboard | Deterministic, cross-cutting, async | Fed by tracing layer only |

## Locked design decisions referenced by this diagram

- **MCP scope:** only the data layer (yfinance) runs as an MCP server. Factor calc, portfolio construction, and factor metrics are native tools (in-process function calls, not a separate MCP server) — see rationale in `P1_Arch1_System_Design.md` §4. Reasoning: MCP standardizes access to *external* resources; these three modules have no external resource behind them and no reuse case outside this one agent.
- **Subagent boundary:** validator and memo-writer are subagents, not tools, because they require independent context (validator) or a distinct persona/style (memo writer) — not achievable within a shared prompt context. See §5 of lesson notes.
- **Governance:** `ValidationResult.passed` is a *recommendation* to a human accountable party, not a final decision gate (P1-LA11). The diagram's arrow from the validator to the orchestrator is labeled accordingly.
- **Metrics are two separate subsystems:** the factor metrics module (IC/rank IC/t-stat/hit rate, part of the synchronous research pipeline) is distinct from the product metrics subsystem (usage/trust/cost, fed asynchronously off the tracing layer, OLTP/OLAP separation per P1-LE2). Do not conflate these when reading or extending this diagram.

## Diagram

![P1 system architecture diagram](P1_Arch1_architecture_diagram.png)

**Canonical source: `project_01_factor_research.drawio`**, stored alongside this file at `docs/architecture/`. Open it at [app.diagrams.net](https://app.diagrams.net) (File → Open) to edit. The PNG above is the direct export from the draw.io app, tuned by hand on 2026-07-20. Keep the export uncompressed (Extras → Edit Diagram should show plain readable XML, not a base64 blob) so the file stays editable — and machine-readable — as plain text. Export a fresh PNG (File → Export as → PNG) from within the app after any future edit; don't have it re-derived from the XML by any other tool, since that has produced a visibly lower-quality result before.

There is no Mermaid or other secondary diagram format for this architecture — the `.drawio` file and its PNG export are the only representations. Anything reading this diagram programmatically (including Claude, in future sessions) should parse `project_01_factor_research.drawio` directly rather than relying on a separate text-based diagram description.

**Legend note:** MCP tool calls are drawn with a dashed border; native (in-process) tool calls with a solid border. No separate legend box is included in the current layout — restate this convention in prose if the diagram is shown without this file alongside it.

**Subagent edge note:** each subagent has a single arrow (orchestrator → subagent) with a combined invoke/result label, rather than separate out-and-back arrows. The underlying interaction is still a round trip — the validator's result is still framed as a recommendation, not a decision (P1-LA11) — say so explicitly if presenting this diagram without accompanying text.

### Reading the diagram programmatically

`project_01_factor_research.drawio` is plain XML (an `<mxfile>` containing an `<mxGraphModel>`). Each shape is an `<mxCell vertex="1">` with a `value` (label), `style` (fill/stroke/dashed color-coding), and `<mxGeometry>` (x/y/width/height). Each connector is an `<mxCell edge="1">` with `source`/`target` attributes pointing at node IDs, plus its own `style` and `value` (edge label). To extract the component list, structure, or edge relationships, parse this XML directly — do not reconstruct or infer the diagram from the PNG or from prose descriptions elsewhere in this file.

## Legend (arrow key)

- **Solid arrows:** synchronous calls on the request path (blocking).
- **Dashed arrows:** tracing/telemetry or async data flow (non-blocking, off the critical path).
- **Orchestrator is a hub, not a pipeline stage:** nearly all calls route through it (hub-and-spoke), not a linear left-to-right pipeline.

## Next architecture lessons

- **P1-Arch-2:** Data flow design — full sequence diagram / written walkthrough of a request end-to-end, with concrete data shapes at each boundary.
- **P1-Arch-3:** Orchestrator + subagent design — what exactly is passed into each subagent's fresh context, and how failures propagate.
- **P1-Arch-4:** Module structure and interfaces — Python file/function signature skeleton (no implementation), derived directly from the boxes in this diagram.
