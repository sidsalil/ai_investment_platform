# P1-LA14: Deployment Basics

**Track:** AI/Agentic (14 of 17)
**Date:** 2026-07-16
**Estimated time:** 2 hours

---

## 1. What "deployment" actually means, and why it's a different problem than "the code works"

Everything you've built so far — the tool-use loop, the subagents, the validator, the observability layer — has run in one place: your laptop, under your VS Code terminal, with you sitting there watching it. That's a **prototype environment**. You are simultaneously the developer, the operator, and the only user.

Deployment is the set of decisions and mechanics that let your system run **somewhere else, for someone else, without you standing behind it**.

Think about the difference between a trading desk analyst's personal Excel model and that same model becoming an approved, IT-supported tool other desks rely on. The math doesn't change. What changes is everything around the math: where does it run, who can access it, what happens if it crashes at 2am, how do credentials get managed, how do you update it without breaking everyone currently using it. That surrounding apparatus *is* deployment. Product managers usually experience this as "the thing engineering says takes six more weeks after the demo already worked" — this lesson is about why that six weeks is real work, not padding.

For Project 1, deployment matters concretely because your polish-phase goal (per CONTEXT.md / curriculum.md's Portfolio Completion & Application Readiness section) is a **live, hosted demo** — a link an interviewer can click, not a screen-share of your laptop.

---

## 2. The core problem deployment solves: "it works on my machine"

Before containerization makes sense, you need to feel the problem it solves.

**Worked example — the problem:**

| | Your laptop | A random hosting server |
|---|---|---|
| Python version | 3.11.9 (via pyenv) | Maybe 3.9, maybe 3.12 — whatever came pre-installed |
| Installed packages | Whatever's in your virtualenv right now, exact versions | Nothing, or different versions |
| OS | Windows 11 + WSL2 Ubuntu | Some Linux distro, possibly different |
| Environment variables (API keys) | In your shell / `.env` file | Not present at all |
| File paths | `/home/sidsa/...` | Different user, different paths |

If you just copy your Python files to that server and run `python app.py`, it will very likely break — wrong Python version, missing packages, missing API keys, wrong paths. This is the "works on my machine" problem: your code's behavior depends on an entire invisible environment around it, not just the code itself.

The traditional fix — write a setup doc, have the ops team install the right Python version and packages by hand — is slow, error-prone, and drifts out of date. Containerization is the modern fix.

---

## 3. Containerization intuition (Docker)

**The analogy:** A shipping container. Before standardized shipping containers existed, loading a cargo ship meant manually handling every irregularly-shaped crate, barrel, and sack — slow, and every port needed different equipment for different cargo. The shipping container standardized the *box*: any crane, any ship, any truck can move a standard container without caring what's inside it. The contents are still different every time; the interface is now identical every time.

A **container image** is the software equivalent: a frozen, self-contained package that includes your code *and* the exact Python version, *and* the exact package versions, *and* the OS-level dependencies it needs. A **container** is a running instance of that image — an isolated process that behaves identically whether it's running on your laptop, a colleague's laptop, or an AWS server, because the entire environment travels with it instead of depending on whatever's already installed on the host.

**Key terms, defined:**

| Term | What it is | Analogy |
|---|---|---|
| **Image** | A frozen snapshot: OS layer + Python + packages + your code, saved as a file | The sealed shipping container, packed and locked |
| **Container** | A running instance of an image | The container actually on the ship, in motion |
| **Dockerfile** | A text file listing the steps to build the image (install Python, copy files, install packages, set the startup command) | The packing instructions — what goes in the container and in what order |
| **Docker Hub / registry** | Where built images are stored and pulled from | The shipping yard where containers wait between ports |

**Worked example — a Dockerfile, read line by line:**

```dockerfile
FROM python:3.11-slim          # Start from a pre-built "Python 3.11 already installed" image
WORKDIR /app                    # Everything below happens inside /app in the container
COPY requirements.txt .         # Copy just the dependency list first
RUN pip install -r requirements.txt   # Install exact versions specified
COPY . .                        # Copy the rest of your code
CMD ["streamlit", "run", "app.py"]    # What to run when the container starts
```

Notice `requirements.txt` is copied and installed *before* the rest of the code. That's not arbitrary — Docker caches each step, so if only your application code changes (not your dependencies), rebuilding skips the slow `pip install` step and just re-copies code. That's a real engineering detail worth being able to explain, not decoration.

**What this buys you, concretely:** you build the image once, on your laptop or in CI. That exact image — same Python version, same package versions, down to the patch number — is what runs in every environment: your laptop, a teammate's laptop, and the production server. "Works on my machine" becomes "works in this image," and the image is identical everywhere.

**What it does NOT solve:** secrets (API keys), and anything that's supposed to differ between environments (a dev database vs. a production database). That's the next concept, deliberately kept separate from the image itself.

---

## 4. Environment configuration: separating config from code

**The core principle:** code should be identical across dev, staging, and production. *Configuration* — API keys, database URLs, feature flags, which environment you're pointing at — should be **injected at runtime**, not baked into the image or hardcoded in your files.

This is worth pausing on because it's a real security and portability requirement, not a style preference:

- **Security:** if your Anthropic API key is hardcoded in a `.py` file and that file gets committed to your GitHub repo (even a private one, even briefly, even in git history after you "remove" it), the key is compromised. Keys belong in environment variables or a secrets manager — never in source code.
- **Portability:** the exact same container image should be deployable to a "staging" environment with test credentials and to "production" with live credentials, without rebuilding the image. If credentials were baked into the image, you'd need a different image per environment — defeating the point of containerization (identical artifact everywhere).

**Worked example — env vars in practice:**

| Variable | Local dev value | Hosted demo value |
|---|---|---|
| `ANTHROPIC_API_KEY` | your personal dev key, in a local `.env` file (never committed — `.env` is in `.gitignore`) | a separate key, set as a secret in the hosting platform's dashboard |
| `DATA_SOURCE` | `yfinance` | `yfinance` (same, for P1) |
| `LOG_LEVEL` | `DEBUG` (verbose, for your own debugging) | `INFO` (quieter, for a production-facing demo) |
| `ENVIRONMENT` | `development` | `production` |

The code that reads `ANTHROPIC_API_KEY` doesn't change between rows — it just does `os.environ["ANTHROPIC_API_KEY"]`. What changes is *where that value comes from*: a local `.env` file loaded by a library like `python-dotenv` in dev, versus a secret injected by the hosting platform in production. This pattern — read config from the environment, never hardcode it — is sometimes called the "twelve-factor app" config principle (https://12factor.net/config); you don't need the whole methodology, just this one piece of it.

---

## 5. Two separate deployment questions people conflate

This is the part most people new to this — including plenty of engineers — get muddled on, so it's worth being explicit:

**Question A: Where does your *application* run?** (Your Streamlit UI, your FastAPI backend, your orchestrator loop, your MCP server — the code you wrote.)

**Question B: Where does *model inference* come from?** (Whichever service actually runs the Claude model and returns a completion.)

These are independent decisions. You could run your application on a $5/month box and call the Anthropic API directly. You could run your application on AWS and call Bedrock. You could run your application on AWS and *still* call the Anthropic API directly (Bedrock is not required just because you're on AWS). The two questions get conflated because "AWS Bedrock" sounds like a deployment platform for your whole app — it isn't. It's specifically a model-inference option.

---

## 6. AWS Bedrock: what it actually is

**What Bedrock is:** a managed AWS service that hosts foundation models — including Anthropic's Claude models — behind AWS's own infrastructure, identity/access system (IAM, Identity and Access Management), networking (VPC, Virtual Private Cloud), and billing. When you call Bedrock, you're calling an AWS endpoint that proxies to (effectively) the same underlying Claude model you'd get from Anthropic's own API — but the request path, authentication, logging, and billing all stay inside AWS's perimeter.

**Why it exists / why an enterprise like Fidelity would use it instead of calling Anthropic directly:**

| Consideration | Calling Anthropic API directly | Calling via Bedrock |
|---|---|---|
| Authentication | Anthropic API key | AWS IAM credentials (same system used for everything else at the firm) |
| Data path | Request leaves to Anthropic's infrastructure | Stays within AWS's network boundary (relevant for firms with strict data-residency/compliance requirements) |
| Billing | Separate Anthropic invoice | Rolled into existing AWS bill |
| Procurement | New vendor contract needed | Often already covered under existing AWS enterprise agreement |
| Model availability | Newest models fastest | Slight lag possible; subset of models |

This is exactly the kind of thing that matters more to a large regulated financial firm than to a solo builder — data residency, existing vendor relationships, and unified IAM are compliance/procurement concerns, not technical ones. It's genuinely relevant to your AI PM positioning at a firm like Fidelity, which is presumably why it's in your curriculum, but it is not something P1 needs for its own hosted demo.

**The honest scoping decision for P1:** you do not need Bedrock to ship a live demo. Bedrock adds AWS account setup, IAM permission configuration, and a second layer of request/response wiring — real complexity — for a benefit (compliance/procurement fit) that only matters inside an enterprise, not for a portfolio project calling the Anthropic API from a hosted container. The concept is worth understanding and being able to discuss in an interview; the *build* doesn't need to route through it.

---

## 7. Application hosting options for the actual P1 demo

Setting Bedrock aside, here's what "make the app itself reachable by a URL" looks like, roughly ordered from simplest to most control:

| Option | What it is | Effort | Good fit for P1? |
|---|---|---|---|
| **Streamlit Community Cloud** | Free hosting purpose-built for Streamlit apps; connects directly to a GitHub repo | Lowest — push to GitHub, click deploy | Good for a fast, low-effort demo link |
| **Render / Railway / Fly.io** | General-purpose app hosting platforms; take a Dockerfile or a repo and run it | Low-medium — some config, but handles containers cleanly | Good middle ground; more control, still simple |
| **AWS App Runner** | AWS's simplest "give me a container, I'll run it" service | Medium — needs an AWS account, container registry (ECR, Elastic Container Registry) setup | Reasonable if you want AWS on the resume story specifically |
| **AWS ECS/Fargate** | Full container orchestration on AWS | Medium-high — more moving pieces (task definitions, networking) | More than P1 needs; more relevant to P2's "production-grade" framing |

**The decision that matters for your resume story:** since your stack already commits to AWS Bedrock "from Project 3 onward" per CONTEXT.md, P1's demo doesn't need to prove AWS competency yet — that's explicitly a later-project goal. For P1, optimize for *actually shipping a working link*, not maximum infrastructure sophistication. Streamlit Community Cloud or Render are the pragmatic choice here; save the AWS container-orchestration story for when it's actually load-bearing in the curriculum.

---

## 8. What a deployed P1 looks like end to end

```
Browser (interviewer clicks your link)
   │
   ▼
Hosted Streamlit app (Render / Streamlit Community Cloud)
   │  reads ANTHROPIC_API_KEY from platform's secret store, not from code
   ▼
Your orchestrator loop + subagents (P1-LA1, LA7)
   │
   ▼
Anthropic API (direct call — no Bedrock needed for P1)
   │
   ▼
MCP server (P1-Build) → yfinance data
```

Every box in this diagram is something you've already designed conceptually in earlier lessons (the loop in LA1, subagents in LA7, MCP as the tool layer). Deployment doesn't change any of that logic — it just answers "where does this run, and how does it get its secrets" for the whole chain.

---

## Concepts Learned — Summary

1. **Deployment defined:** the mechanics that let a system run reliably somewhere else, for someone else, without the builder present to fix it live. Distinct from "the code works" on a local machine.
2. **"Works on my machine" problem:** local environments (Python version, package versions, OS, env vars, file paths) differ from hosting environments; copying code alone doesn't transfer the environment it depends on.
3. **Containerization (Docker):** an **image** is a frozen snapshot of OS + Python + packages + code; a **container** is a running instance of that image; a **Dockerfile** is the recipe that builds the image. Shipping-container analogy: standardizes the box, not the contents, so any host can run it identically. Docker's layer caching means dependency-install steps are skipped on rebuilds when only application code changes.
4. **Environment configuration:** config (secrets, endpoints, environment flags) must be separated from code and injected at runtime via environment variables, never hardcoded or committed to git. This is what allows one identical container image to run correctly across dev/staging/production with different credentials in each.
5. **Two independent deployment questions:** (A) where the *application* runs vs. (B) where *model inference* comes from. These are commonly conflated but are separate decisions — an app can run anywhere and call any inference provider independently.
6. **AWS Bedrock:** a managed AWS service that hosts foundation models (including Claude) behind AWS's own IAM, VPC, and billing — relevant for enterprise data-residency, procurement, and compliance reasons, not a general application-hosting platform. Not required for P1's demo.
7. **P1 hosting decision:** Streamlit Community Cloud or Render/Railway/Fly.io are the pragmatic choice for P1's live demo — AWS container orchestration is explicitly deferred to later in the curriculum (Bedrock scoped in from Project 3 onward per CONTEXT.md stack decisions), not needed to prove AWS competency at this stage.
8. **End-to-end deployed architecture for P1** mapped: browser → hosted Streamlit app (reading secrets from the platform, not code) → orchestrator loop + subagents → Anthropic API directly (no Bedrock) → MCP server → yfinance.

## Decisions Logged This Lesson

- P1's live hosted demo will call the Anthropic API directly, not AWS Bedrock. Bedrock is understood conceptually (enterprise data-residency/IAM/procurement fit) and is real interview material, but is not part of P1's build — deferred to Project 3 onward per existing stack decisions in CONTEXT.md.
- P1's application hosting platform choice deferred to P1-Build/P1-Polish (deployment sprint), but Streamlit Community Cloud or Render/Railway/Fly.io are the recommended default over AWS App Runner/ECS given P1's scope — optimize for shipping a working link, not infrastructure sophistication.

## Carried-Forward Action Items

- At the actual P1 deployment build step (P1-Build-12 per curriculum.md / P1-Polish "Live, hosted demo"): write the real Dockerfile, choose the specific hosting platform, and set up the actual secrets injection (platform dashboard, not `.env` in git). This lesson covered the concepts; the hands-on build is still ahead.
- If Fidelity-internal AI PM conversations ever require discussing Bedrock specifically, the compliance/procurement framing in Section 6 (IAM, VPC, unified billing, data residency) is the relevant talking point — not a technical superiority claim over the direct API.
