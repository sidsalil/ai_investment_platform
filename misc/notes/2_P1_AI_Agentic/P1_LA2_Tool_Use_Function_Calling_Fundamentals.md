# P1-LA2: Tool Use / Function Calling Fundamentals

**Completed:** 2026-07-14
**Track:** AI/Agentic (lesson 2 of 17)
**Estimated time:** 1-2 hours

---

## 1. The core problem this solves

Here's the thing about a Large Language Model (LLM) like Claude that's easy to miss: **it can only produce text.** That's it. It cannot look anything up, run any code, query any database, or check today's date. Every single thing it "knows" is baked into it from training — frozen at some point in the past.

Think of it like this: imagine hiring the sharpest research analyst you've ever worked with — the kind of person who can reason through a momentum-strategy hypothesis in seconds — but this analyst has no Bloomberg terminal, no access to your firm's database, no internet connection, and no ability to run a single line of Python. They can only *talk*. If you ask them "What's NVDA's price today?" they either have to admit they don't know, or — worse — guess based on the last price they happened to remember from months ago and state it confidently.

**Tool use** (also called **function calling**) is the mechanism that fixes this. It lets you tell the model: "Here is a list of things I, the surrounding application, am able to do on your behalf if you ask me to — fetching a stock price, running a calculation, querying a file. If you decide one of these would help answer the question, tell me which one and with what inputs, and I'll go do it and hand you back the result."

The critical thing to hold onto, because it's the single most common misunderstanding: **the model never executes anything itself.** It only ever outputs text — text that your application code is designed to *recognize* as a structured request, then physically go execute. The "calling" happens in your code, not inside the model. The model's contribution is purely: deciding *whether* a tool is needed, *which* one, and *what inputs* to give it — expressed as a specially formatted piece of output rather than free-flowing prose.

This is the concrete mechanical implementation of the **perceive-reason-act loop** you learned in P1-LA1. The "act" step in that loop *is* a tool call, in the exact technical sense this lesson covers. P1-LA1 gave you the mental model; this lesson gives you the machinery underneath it.

## 2. What a "tool" actually is, from the model's point of view

A tool isn't code the model can see or touch. It's a **description** — a structured, written specification that says: "here is a capability that exists, here is its name, here is what it does, and here is exactly what information you'd need to provide to use it." The model never sees your Python function. It only ever sees this description, formatted in a standard structure called **JSON Schema** (JavaScript Object Notation Schema — a widely-used format for describing the shape of structured data).

This is exactly analogous to something you've done a thousand times as a Product Manager: writing an Application Programming Interface (API) specification for engineers to implement, without writing the implementation yourself. You describe *what* the endpoint does and *what inputs it needs* — the engineering team builds the actual thing behind it. The model is in the position of someone reading your API spec and deciding whether to call it; your application code is the engineering team who actually built and runs the endpoint.

### Anatomy of a tool definition

| Field | Purpose | Analogy |
|---|---|---|
| `name` | The identifier the model uses to request this tool | The function/endpoint name in an API spec |
| `description` | Plain-language explanation of what the tool does and when to use it | The "Summary" section of an API spec — this is what the model actually reads to decide relevance |
| `input_schema` | A JSON Schema object listing every parameter the tool needs, with types and which are required | The "Request Body" section of an API spec |

Here's a concrete, minimal example — a tool that fetches a stock's historical price data, directly relevant to your P1-Build-1 MCP (Model Context Protocol) server:

```json
{
  "name": "get_price_history",
  "description": "Fetches daily adjusted-close price history for a given stock ticker between two dates. Use this whenever you need historical prices to compute a return, factor, or any price-based calculation.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol, e.g. 'AAPL'"
      },
      "start_date": {
        "type": "string",
        "description": "Start date in YYYY-MM-DD format"
      },
      "end_date": {
        "type": "string",
        "description": "End date in YYYY-MM-DD format"
      }
    },
    "required": ["ticker", "start_date", "end_date"]
  }
}
```

**The `description` field is doing almost all of the real work here, and this is a point worth sitting with.** The model has no other information about what this tool does — it can't read your implementation, can't see docstrings, can't see comments. If your description is vague ("gets some price data"), the model will misuse the tool, use it at the wrong times, or fail to use it when it should. Writing a good tool description is a form of product-spec writing you already know how to do — you're writing the "when would a user need this" framing, just aimed at the model instead of a person. This is exactly why P1-LA10 (agent security) and later build sprints treat tool descriptions as a real design surface, not an afterthought.

## 3. How the model "decides" to call a tool

It's worth being precise about what "decides" means here, because the word invites a wrong mental picture. The model isn't deliberating in the way a person weighs options. Underneath, it's still doing the same thing it always does — predicting the next most likely piece of output given everything in its context (the conversation so far, the system prompt, and now, the list of available tool definitions).

What's different is that **during training, the model was shown enormous numbers of examples where a tool was relevant, and where the "correct" next output was a structured tool request rather than a sentence.** So when the current context looks like "the user is asking something that would require the `get_price_history` tool to answer accurately," the model's learned patterns push it toward generating a structured tool-call output instead of a prose guess. It is pattern-matching on *when tool use looks appropriate*, trained the same way it learned when to write a bullet list versus a paragraph.

This matters practically: it means tool selection is not perfectly reliable. The model can call the wrong tool, call a tool with slightly wrong inputs, call a tool it didn't need, or fail to call a tool it should have — all because it's still fundamentally a pattern-completion process, not a deterministic dispatcher. This is exactly the seed of what P1-LA9 (agent reliability failure modes) will cover in depth. For now, just hold the fact: **tool selection is a probabilistic judgment the model makes, not a guaranteed-correct lookup.**

## 4. The request/response cycle — the actual mechanics

This is the part that's pure mechanics, and worth walking through slowly because it's exactly what you'll be implementing in P1-Build-1 and P1-Build-7.

### The five-step cycle

| Step | Who acts | What happens |
|---|---|---|
| 1 | You (the application) | Send the model a message plus the full list of available tool definitions |
| 2 | The model | Returns either a normal text response, OR a special `tool_use` block requesting a specific tool with specific inputs |
| 3 | You (the application) | If step 2 was a `tool_use` block: actually execute the real function/API call with those inputs |
| 4 | You (the application) | Send the tool's real output back to the model as a new message, tagged as a `tool_result` |
| 5 | The model | Reads the tool result and either produces a final text answer, or requests another tool call (looping back to step 2) |

Notice: steps 1, 3, and 4 are all things *your code* does. Steps 2 and 5 are the only steps where the model itself does anything. This is worth re-reading, because it's the cleanest way to internalize "the model never executes anything" — literally count the steps and see which ones belong to you versus the model.

### Worked example: full cycle, step by step

Let's trace this concretely using the `get_price_history` tool defined above, for the request: *"What was AAPL's average price in the first week of June 2026?"*

**Step 1 — Your application sends:**

| Component | Content |
|---|---|
| User message | "What was AAPL's average price in the first week of June 2026?" |
| Available tools | `[get_price_history]` (the JSON definition above) |

**Step 2 — The model responds with a `tool_use` block** (not plain text, because it recognizes it needs actual data to answer accurately, and lacks it):

```json
{
  "id": "msg_01XYZ",
  "role": "assistant",
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_01A",
      "name": "get_price_history",
      "input": {
        "ticker": "AAPL",
        "start_date": "2026-06-01",
        "end_date": "2026-06-07"
      }
    }
  ],
  "stop_reason": "tool_use"
}
```

**Correction/clarification (added post-lesson, see Section 9):** `stop_reason` is not a field inside the `tool_use` block itself — it's a separate, sibling field on the *overall API response object*, at the same level as `content` (the list that holds the `tool_use` block). Your application checks the top-level `stop_reason`: if `"tool_use"`, go find the tool_use block(s) inside `content` and execute them; if `"end_turn"`, `content` instead holds a plain text block and no tool call is needed.

**Step 3 — Your application actually executes** `get_price_history(ticker="AAPL", start_date="2026-06-01", end_date="2026-06-07")` — this calls your real yfinance-backed function, hits the actual data source, and gets back real numbers. The model has no visibility into this step at all; it's a black box to the model.

**Step 4 — Your application sends the result back**, tagged with the same tool-call ID so the model knows which request it corresponds to:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01A",
  "content": "2026-06-01: 201.34, 2026-06-02: 203.10, 2026-06-03: 202.85, 2026-06-04: 204.02, 2026-06-05: 205.11"
}
```

**Step 5 — The model reads this and produces a final text answer**, now `stop_reason: "end_turn"`:

> "AAPL's average adjusted-close price over the first week of June 2026 (June 1–5, trading days) was approximately $203.28."

The model computed that average itself, from the numbers it was handed — but it could not have gotten those numbers without the tool. This is the clean division of labor: **the model reasons over data; your application fetches data.**

## 5. Multiple tools and tool choice

A real agent typically has more than one tool available at once — your P1 project will eventually expose several (fetch prices, compute a factor, look up sector classification, etc.) through the MCP server. When multiple tools are available, the same decision process applies, just across a larger menu: the model reads all the tool descriptions, compares them against what the current request seems to need, and picks the one (or more) that seem relevant.

**Parallel tool calls** are also possible — in a single turn, the model can request several tool calls at once if it determines they're all needed and don't depend on each other's results (e.g., fetching price history for three different tickers at the same time, since none of those calls need to know the result of another). Your application then executes all of them and returns all the results together before the model continues. This is a meaningful efficiency mechanism worth knowing exists, though the deeper implications for orchestration come later in P1-LA6 (planning loops) and P1-LA7 (subagent orchestration).

**Sequential (dependent) tool calls** happen when one tool's output is needed before the next tool call can even be formed — e.g., you can't ask for "this stock's sector-neutral z-score" until you've first fetched its raw price history and computed the raw factor. The model handles this by simply looping through the five-step cycle multiple times: get result 1, reason about it, request tool 2, get result 2, reason, and so on — this is the actual mechanical shape of the "single tool-use loop" autonomy level named in P1-LA1's spectrum.

| Pattern | When it happens | Example in Project 1 |
|---|---|---|
| Single tool call | One tool answers the whole request | "What's TSLA's current price?" → one `get_price_history` call |
| Parallel tool calls | Multiple independent tools/inputs needed at once | Fetching price history for 5 different tickers simultaneously |
| Sequential tool calls | One tool's output is required input for the next | Fetch prices → compute factor → z-score → needs each prior step's result |

## 6. Failure modes — a first look (full depth in P1-LA9)

Because tool selection is a probabilistic judgment (Section 3) rather than a guaranteed lookup, several things can go wrong, and it's worth naming them now even though the full reliability treatment is P1-LA9's job:

- **Wrong parameters:** the model calls the right tool but with a malformed or incorrect input (e.g., a wrong date format, a misspelled ticker) — your application's job is to validate inputs and fail cleanly rather than silently pass garbage through.
- **Unnecessary tool call:** the model calls a tool when it didn't actually need to (e.g., calling `get_price_history` for a question it could have answered from general knowledge), wasting time and cost.
- **Missed necessary tool call:** the model answers from its own (possibly outdated or wrong) training knowledge instead of calling a tool it should have used — this is a direct hallucination risk, and it's the exact same "Reason vs. Perceive" distinction flagged in the P1-LA1 follow-up note: if the model states a specific fact (like a price) without a backing tool call, that fact came from fuzzy training memory, not verified reality.
- **Hallucinated tool call:** in rare cases, a model can request a tool that doesn't exist in the definitions it was given, or invent parameters not in the schema — your application code must reject anything that doesn't match a real, defined tool.

None of these require a fix today — they're logged here so the vocabulary is already in place when P1-LA9 covers detection and mitigation in depth.

## 7. Why this lesson matters for Project 1 specifically

Every single build sprint from P1-Build-1 onward depends on this mechanism working correctly:

- **P1-Build-1** (MCP data server): every function you expose (price fetching, sector lookup) becomes a tool definition exactly like the `get_price_history` example above. The quality of your `description` fields directly determines whether the orchestrator agent uses them correctly.
- **P1-Build-7** (orchestrator's planning loop): the whole "natural language → structured FactorSpec → sequence of tool calls" pipeline is this five-step cycle, repeated and chained.
- **P1-Build-8** (validator subagent): will need to reason about *whether the right tools were called with the right inputs* as part of its methodology checks.

## 8. Explain-it-back check (for reference — no reply required)

A good internal test: could you explain to a non-technical colleague why "the AI called the wrong stock ticker" is a *tool-input* problem, not a *tool-execution* problem? (Answer: because the tool itself — the code that fetches prices — worked perfectly; the model just handed it the wrong ticker string. The bug is in the model's judgment about *what to ask for*, not in the deterministic code that executed the ask.)

---

## 9. Follow-up clarification: how does the model make sense of arbitrary JSON tool results?

A natural question once you've seen the five-step cycle: every tool returns a different JSON shape — how does the model know how to read any of them, given there's no universal schema for tool *outputs* the way there is for tool *inputs*?

The honest answer is: **there is no JSON parser inside the model.** It doesn't deserialize the tool result into a data structure the way your Python code would with something like `json.loads()`. It reads the tool result exactly the same way it reads anything else — as a sequence of tokens — and applies the same general language-understanding ability it uses on prose, code, tables, or CSV snippets. This works for three reasons:

**a) JSON is just structured text, and the model has seen an enormous amount of it during training.** It was exposed to huge volumes of JSON, API responses, config files, log output, code, and tables. It learned the general pattern that a `key: value` pair means "this label describes that value" — the same way it learned that a table column header describes the column beneath it. It isn't running a JSON-specific algorithm; it's applying a general "structured data has meaning-carrying keys" pattern picked up from exposure, not a dedicated parsing routine.

**b) The key names are doing the semantic work — the same role the tool `description` field played in Section 2, just on the output side.** When a tool result comes back as `{"2026-06-01": 201.34, "2026-06-02": 203.10}`, the model isn't executing code to know "these are dates mapped to prices" — it infers that from the key strings looking like dates, the values looking like plausible stock prices, and the fact that it just asked a tool called `get_price_history` for exactly that. The result isn't interpreted cold: the model already has strong context going in, since it knows which tool it called, with which inputs, and what the tool's description said it would return. It interprets the result *against the expectation it just set up*, not from a blank slate.

**c) This is exactly why poorly-named keys or opaque structures are a real design risk** — the identical lesson from Section 2's point about `description` fields, just applied to outputs instead of inputs. A tool result like `{"a": 201.34, "b": "2026-06-01"}` gives the model nothing to anchor meaning to; `{"date": "2026-06-01", "adjusted_close": 201.34}` is self-documenting. This is also the practical reason many real tool implementations return a clean, human-readable **formatted string** for a result rather than raw nested JSON — e.g. `"2026-06-01: $201.34, 2026-06-02: $203.10"` — since the model doesn't benefit from strict machine-parseable JSON the way your code would; it benefits from clarity, the same way a person skimming a report does.

**Practical implication for Project 1:** how the P1-Build-1 MCP server *formats what tools return*, not just how it names their *inputs*, is a genuine design decision affecting reliability — not an implementation detail to defer. Well-labeled, ideally human-readable tool outputs reduce the chance of the model misreading a result, in the same way a well-written tool `description` reduces the chance of it misusing the tool in the first place.

---

## Summary of key terms introduced this lesson

| Term | Plain-language definition |
|---|---|
| Tool use / function calling | The mechanism letting a model request that external code be executed on its behalf, since it can only produce text itself |
| Tool definition | A written specification (name, description, input schema) describing a capability, which is all the model ever sees of a tool |
| JSON Schema (JavaScript Object Notation Schema) | The standard structured format used to describe a tool's expected inputs |
| `tool_use` block | The model's structured output requesting a specific tool with specific inputs, instead of plain text |
| `stop_reason` | A signal field telling the application whether the model finished (`end_turn`) or is waiting on a tool result (`tool_use`) |
| `tool_result` | The message your application sends back to the model containing the real output of the executed tool |
| Parallel tool calls | Multiple independent tool requests issued by the model in a single turn |
| Sequential tool calls | Tool calls that depend on a prior tool call's result, requiring multiple loop iterations |

No new locked design decisions from this lesson — it is mechanics/vocabulary, applied directly in P1-Build-1 and P1-Build-7.
