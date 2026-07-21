# P1-Arch-0: Tooling Setup — Claude Code Configuration and Initial Test

**Completed:** 2026-07-20
**Track:** Phase 2 — Architecture & Design (Project 1: Factor Research Copilot)
**Estimated time:** 0.25–0.5 hour (reduced from 0.5–1 hour once install/auth was found to already be done)

> **Correction (2026-07-20, same session):** This lesson originally included install and authentication steps (§5–6 below). Those were already complete as of 2026-05-25 per the Environment Setup Checklist — `claude-code: 2.1.150` installed via npm, authenticated on Claude Pro. That checklist should have been checked before generating this lesson, and wasn't on the first pass. §5–6 are left below for reference/troubleshooting only (e.g., reinstalling on a new machine), not as outstanding work.

---

## Why this lesson exists

On 2026-07-20 the code-ownership policy was revised. The old rule (2026-04-26) was "I type everything, Claude gives snippets only." The new rule is subtler — you write code yourself by default, and Claude Code's default job is to **review your diff and suggest refactors, not generate code unprompted.** Full generation is available, but only as something you explicitly ask for each time, not a standing permission.

That distinction only matters if the tool is actually configured to behave that way. A tool installed with defaults left untouched will happily auto-accept edits, run in "yolo mode," or push straight to `main` if you let it. This lesson is entirely about locking in the guardrails *before* using the tool on real project code — think of it like configuring a new analyst's system access and approval limits before their first day on the desk, not after.

---

## 1. What Claude Code actually is

**Claude Code** is a command-line tool — meaning you talk to it by typing text into a terminal window, not through a web browser or an app with buttons. You give it an instruction in plain English ("read this file and tell me what it does," "fix the bug in this function"), and it can read files, edit files, and run terminal commands on your behalf, inside whatever directory you launched it from.

The analogy from your world: think of a **Bloomberg terminal command line**. You're not clicking through menus — you type a command, it does a specific thing, and it shows you the result in the same window. Claude Code is the same shape of tool, except the "commands" are natural-language requests, and instead of pulling bond prices it's reading and writing source code.

Two terms that come up immediately:

| Term | Plain-language definition |
|---|---|
| **CLI (Command-Line Interface)** | A tool you operate by typing text commands into a terminal, as opposed to a **GUI (Graphical User Interface)** — buttons, menus, mouse clicks. Claude Code is a CLI tool. |
| **PATH** | A list your operating system keeps of "which folders to search when I type a command name." If a tool's install location isn't on your PATH, typing its name gives you `command not found` even though the tool is sitting right there on disk. Most install problems trace back to this. |

---

## 2. The permission-prompt → diff → approve loop (the core safety mechanism)

This is the single most important concept in this lesson, because it's the mechanism that actually enforces the code-ownership policy day to day.

**The mental model:** Claude Code never silently edits your files. Every time it wants to write, modify, or delete something — or run a command that changes state — it stops and shows you exactly what it wants to do, and waits for you to approve or reject it. This is called a **permission prompt**.

When the change is to an existing file, what it shows you is a **diff**. A diff is a side-by-side (or +/- marked) view of "here's the current line, here's what I want to change it to" — the same shape as reviewing a redlined document or a tracked-changes Word doc. Green/`+` lines are additions, red/`-` lines are removals. You read the diff, decide if it's right, and either approve it (it gets written to disk) or reject it (nothing happens, file stays as-is).

**Why this matters for the policy specifically:** the comprehension gate — "every non-trivial decision in the diff must be explainable without prompting, or it doesn't merge" — is only enforceable if you're actually forced to look at a diff before it lands. If an "auto-accept everything" mode is enabled, the tool will happily make dozens of small decisions on your behalf that never get reviewed, and you'd be rubber-stamping without knowing it. That's exactly the failure mode the 2026-07-20 policy revision was written to avoid. So: **permission mode stays on "ask every time" for this project, full stop.**

**Trading-desk analogy:** this is a trade blotter with a mandatory second-look before execution, not straight-through processing. Every trade (file edit) gets flagged for review before it settles (writes to disk).

---

## 3. Branch-only-never-main

One more piece of the same safety logic, at the Git level.

In **Git** (the version control system the repo uses), `main` is the name conventionally given to the "official, current, working" version of the codebase. A **branch** is a parallel, separate line of work — you can make changes on a branch without touching `main` at all, and only bring those changes into `main` once reviewed (via a **merge**).

The rule: **Claude Code generates code on a branch, never directly on `main`.** This gives a second, independent checkpoint beyond the individual diff-approval loop — even after approving individual diffs on a branch, you get one more look at the *whole* change before it becomes part of the official codebase. This is standard professional software engineering practice (nobody commits straight to `main` on a production system), and it maps directly to something already familiar: nothing goes to production without passing through a lower environment first (dev → UAT → prod). The branch is the dev/UAT equivalent.

---

## 4. What `claude mcp list` is checking for (brief recap from P1-LA3)

**MCP (Model Context Protocol)** is the standard way an AI agent connects to external tools and data sources — in Project 1's case, this will eventually be a small MCP server exposing `get_price_history`, `get_universe_constituents`, and `get_sector_classification` from yfinance. At this stage of setup, no MCP servers have been built or connected yet — that happens in Phase 3 build sprints. Running `claude mcp list` now should return an **empty list**, and that's the correct, expected result. This step is only confirming the command itself runs without error — proof the tool's plumbing works — not that anything is connected yet.

---

## 5. Installation (WSL2/Ubuntu) — already done 2026-05-25, reference only

| Step | Command | What it does |
|---|---|---|
| 1. Install (recommended path) | `curl -fsSL https://claude.ai/install.sh \| bash` | Downloads and runs Anthropic's native installer script. Preferred over npm because it handles auto-updates going forward. |
| 1b. Fallback if native installer fails | `npm install -g @anthropic-ai/claude-code` | Installs via npm instead, using the Node.js already set up via nvm. Functionally equivalent, just manual updates instead of automatic. |
| 2. Verify install | `claude --version` | Should print a version number. If `command not found` appears, it's a PATH problem (see §1) — the installer may have put the binary somewhere the shell isn't looking. |
| 3. Run diagnostics | `claude doctor` | A built-in health check — reports installation type (native vs. npm), version, and flags any PATH or configuration issues. Run this even if `--version` worked, since it catches subtler problems. |

If `claude doctor` flags a PATH issue: it will typically identify which directory needs to be added. On Ubuntu/WSL2 this usually means adding a line to `~/.bashrc` (or `~/.zshrc` if using zsh) and then either restarting the terminal or running `source ~/.bashrc` to reload it without restarting.

---

## 6. Authentication — already done 2026-05-25, reference only

Run `claude` inside a project directory (any directory is fine for now, even a scratch one — this is only triggering the login flow, not doing real work yet). This opens a **browser-based login** against the Claude subscription or Console account — the same shape as any OAuth-style "sign in with your existing account" flow. Once authenticated, the credential is stored locally so login doesn't need to repeat each session.

---

## 7. Configuration decisions — what's being locked in and why

| Decision | Setting | Why |
|---|---|---|
| **Editor integration** | CLI only. **Do not install the VS Code extension.** | The VS Code extension's one-click "accept all" diff UX is convenient but works directly against the comprehension gate — it makes it too easy to blast through diffs without actually reading them. The CLI, run in an integrated terminal pane, is deliberately a little more friction. That friction is the point. |
| **Permission mode** | Require approval on every file write (the default — do **not** enable an "accept all" / "yolo" mode) | This is the mechanism from §2. Turning this off silently defeats the entire comprehension-gate policy. |
| **Project instructions file** | Create `CLAUDE.md` at the repo root (full content in §8) | This is how Claude Code gets standing context about *this specific project* — its conventions, constraints, and the code-ownership policy — without restating it every session. |

**Why "CLI only, no extension" is a real decision and not just a preference:** this is the same category of judgment call as choosing which trading system permissions to grant a new hire. The extension isn't *unsafe* in some abstract sense — it's that its UX is optimized for speed of acceptance, which is the opposite of what the policy is trying to protect. The higher-friction tool is being chosen deliberately, because the friction is doing protective work.

---

## 8. `CLAUDE.md` — what it is and its full content

`CLAUDE.md` is a plain markdown file that Claude Code automatically reads at the start of every session when launched inside a directory that contains one. It functions like a standing memo — a new-analyst onboarding packet handed over automatically instead of being re-explained verbally every single time.

Full file content, created at repo root (`ai_investment_platform/CLAUDE.md`):

```markdown
# CLAUDE.md — Project Instructions for Claude Code

## Code-Ownership Policy (effective 2026-07-20)

Default mode: I write code myself first. Your default role is to **review my
diff, flag issues, and suggest refactors** — not to generate implementation
code unprompted.

Full code generation is available ONLY when I explicitly request it in that
instance (e.g., "generate this function," "write this for me"). This is an
opt-in exception per request, not a standing permission. Do not infer
permission to generate code from context alone — ask if unsure.

Whether code is hand-written or AI-generated on request, the gate before
anything merges to main is COMPREHENSION, not authorship: every non-trivial
decision in a diff must be explainable by me without prompting, or it does
not merge.

## Workflow Rules

- Work on a branch. NEVER commit or push directly to `main`.
- Every file write requires my explicit approval via the permission prompt —
  do not suggest or attempt to enable an auto-accept mode for this project.
- Diff review happens with explanation in chat/terminal, not just inline
  tool rationale — if I ask "why," give the real reasoning, not a summary
  of the diff.

## Context

Full project history, architecture decisions, and curriculum tracking live in
CONTEXT.md and curriculum.md in the project root. Read those for context on
where this project is and what's already been decided before making
suggestions that might duplicate or contradict prior decisions.

## Project Summary

AI Investment Platform — two-project portfolio (Factor Research Copilot,
Backtesting Copilot) demonstrating agentic AI patterns (tool-use loop,
planning loop) applied to quantitative investment research. Built as part of
a career pivot toward AI Product Manager roles in financial services.
```

---

## 9. Initial test — proving the loop actually works end to end

Do this in a **scratch/throwaway directory**, not inside the real project repo — the goal is purely to confirm the mechanics work, with nothing at stake if something goes wrong.

**Test sequence:**

| Step | What to do | What this confirms |
|---|---|---|
| 1 | Launch `claude` in the scratch directory | Tool starts, session is authenticated |
| 2 | Ask it to explain what's in a small existing file (any file already lying around) | It can read files and reason about them without needing write access |
| 3 | Ask it to generate one trivial, low-stakes file — a `.gitignore` is the suggested example | Triggers the write path |
| 4 | Watch for the permission prompt before anything is written | This is the guardrail — if a file appears on disk *without* a prompt, something is misconfigured and needs fixing before touching real project code |
| 5 | Review the diff shown, then explicitly approve | Confirms the approve step actually commits the write |
| 6 | Try rejecting a second small suggested edit | Confirms rejection actually blocks the write — don't just test the "yes" path |
| 7 | Run `claude mcp list` | Should return an empty list — confirms the command runs cleanly; no MCP servers expected yet (see §4) |

If steps 4 and 6 both behave correctly — a prompt appears every time, and rejecting genuinely blocks the write — the configuration is sound and it's safe to move on to real project work in P1-Arch-1.

---

## 10. Deliverable checklist

- [x] Claude Code installed and authenticated — already done 2026-05-25 (`claude-code: 2.1.150` via npm, Claude Pro)
- [ ] Confirmed VS Code extension is **not** installed
- [ ] Permission mode confirmed as "approve every write" (no auto-accept enabled)
- [ ] `CLAUDE.md` created at repo root with the content in §8
- [ ] Initial test completed: read-only file explanation works, one file generated with visible permission prompt and diff, one edit explicitly approved, one edit explicitly rejected and confirmed blocked, `claude mcp list` runs and returns empty

Once all six boxes are checked, the next lesson is **P1-Arch-1: System design** — the architecture diagram for Project 1.
