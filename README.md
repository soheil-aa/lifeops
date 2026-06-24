# LifeOps — Privacy-First Personal Concierge

> Kaggle AI Agents Intensive Capstone — **Track: Concierge Agents** — Deadline: July 6, 2026

A personal email + calendar concierge built on Google ADK with a security-first architecture.
The trust and safety patterns are the real deliverable; the assistant is the vehicle that
demonstrates them. Nothing essential is mocked.

---

## Problem Statement

Personal AI assistants that touch email and calendar need write access to sensitive data.
Most architectures give the agent a broad credential and let it act freely, with no auditable
record of what was done or why it was allowed. LifeOps is the opposite: every external write
passes through a single, observable chokepoint that enforces a declarative policy, a PII
guard, and (where required) explicit human approval — before any credential is used.

## Why the Concierge Track

End-to-end personal productivity workflows (triage → draft → schedule → send) are the natural
killer app for agentic AI, but they require the highest trust. LifeOps proves that the trust
story can be made rigorous and auditable without sacrificing usability.

---

## Architecture

### Component Map

| Unit | Responsibility | Note |
|------|----------------|------|
| **Coordinator** | Routes requests to specialists; assembles results; owns the conversation | Holds **no** Google credentials |
| **Email specialist** | Gmail read / classify / draft / send; proposes actions only | Uses Gmail MCP client (fake by default; real with `LIFEOPS_USE_MCP=1`) |
| **Calendar specialist** | Calendar read / conflict-check / create / accept; proposes actions only | Uses Calendar MCP client (fake by default; real with `LIFEOPS_USE_MCP=1`) |
| **Action Bus** | Single chokepoint: every proposed write passes through PII filter → Policy Server → approval queue | `app/core/action_bus.py` |
| **Policy Server** | Pure function: `evaluate(action, context) → allow / require_approval / deny` | Driven by `policy.yaml` |
| **PII Filter** | Tokenizes sensitive fields before content reaches the model or an external tool | `app/core/pii_filter.py` |
| **Token Broker** | JIT single-scope least-privilege credential interface (built + unit-tested) | `app/core/token_broker.py` — not yet wired into the live execute path (planned follow-up) |
| **State Store** | SQLite: encrypted tokens, proposal queue, sessions | `app/core/state.py` |
| **Trigger layer** | Interactive (CLI/playground) + ambient (schedule / new-mail poll) — both emit identical request objects | `app/triggers/` |
| **Telemetry** | OpenTelemetry spans on every hop, verdict, redaction, and executed/denied action | `app/app_utils/telemetry.py` |

### Data Flow

```
Trigger (user asks  OR  ambient event)
        │
        ▼
   Coordinator ──ADK sub-agents──► Specialist (Email / Calendar)
        │                               │ reads via MCP client (fake default; real with LIFEOPS_USE_MCP=1)
        │                               ▼
        │                      proposes world-changing action ──► Action Bus
        │                               │
        │                               ▼
        │                      PII filter → Policy Server verdict
        │                          ├─ allow ............ execute now
        │                          ├─ require_approval .. enqueue → show Vibe Diff → user approves/denies
        │                          └─ deny ............. blocked, logged with reason
        ▼
   Result assembled, returned to user; every step traced (OpenTelemetry)
```

### Safety Model

**Core invariant:** specialists never execute an external write directly — they can only
*propose* to the Action Bus. The Action Bus is the single chokepoint where all three defenses
are enforced in sequence:

1. **PII filter** — sensitive fields (email addresses, phone numbers, account numbers) are
   tokenized into placeholders before content crosses a trust boundary.
2. **Policy Server** (`policy.yaml`) — a deny-by-default declarative YAML policy. Unknown
   actions default to `require_approval`. The wildcard rule `"*": deny` is the backstop.
3. **Human-in-the-loop (HITL)** — actions that return `require_approval` are enqueued and
   shown as a "Vibe Diff" for the user to approve or deny before any credential is used.

The chokepoint is proven by `tests/integration/test_safety_invariant.py`.

**Token Broker (v1 status):** The `TokenBroker` provides the JIT single-scope least-privilege
*interface* (built and unit-tested in `app/core/token_broker.py`); wiring it into the live
execute path is a planned follow-up. In v1 the Confused-Deputy / least-privilege defense is
delivered by the architecture itself: the Coordinator holds no credentials, specialists can
only *propose* (never execute), and the Action Bus enforces deny-by-default policy + human
approval before any write is performed.

### Policy File (`policy.yaml`)

```yaml
defaults: require_approval          # unknown = ask, not execute
rules:
  - action: email.read              # read-only: allow
    verdict: allow
  - action: calendar.read
    verdict: allow
  - action: email.draft_save        # reversible / internal: allow
    verdict: allow
  - action: calendar.hold_tentative
    verdict: allow
  - action: email.send              # external write: require approval
    verdict: require_approval
    constraints:
      recipients_in: ["@known-contacts"]
      max_recipients: 5
      no_pii_to_external: true
  - action: calendar.create
    verdict: require_approval
  - action: calendar.accept_invite
    verdict: require_approval
  - action: "*"                     # anything unmatched: deny
    verdict: deny
```

A reader can open this file and understand — or change — what the agent is allowed to do
without touching code.

---

## Setup

### 1. Install dependencies

```bash
uv sync --dev
```

### 2. Google credentials (for real Gemini + Gmail/Calendar)

Option A — Application Default Credentials (recommended for local dev):

```bash
gcloud auth application-default login
```

Option B — API key (Gemini only, no Gmail/Calendar writes):

```bash
export GOOGLE_API_KEY=your_key_here
```

If neither is present the agent starts in **offline/fake mode** — all tests pass and the
playground runs with fake clients.

### 3. Enable real Gmail and Calendar MCP servers (optional)

```bash
export LIFEOPS_USE_MCP=1
```

Without this flag the agent uses in-process fake clients (safe default for demos and tests).

---

## Running

### Interactive playground

```bash
uv run agents-cli playground
```

### Unit and integration tests

```bash
uv run pytest tests/unit tests/integration
```

### Eval suite (requires ADC)

```bash
agents-cli eval generate   # run agent on the golden dataset
agents-cli eval grade      # score with LLM-as-judge (safety-gate precision/recall)
agents-cli eval compare    # regression diff between two grade-result files
```

The eval dataset lives at `tests/eval/datasets/safety-gate.json`; config at
`tests/eval/eval_config.yaml`. Grading requires a live Gemini model — run manually before
submission.

---

## Capstone Alignment

**Track:** Concierge Agents — **Deadline:** July 6, 2026

| Course Concept | Where | How |
|----------------|-------|-----|
| **Multi-agent (ADK)** | `app/coordinator/agent.py`, `app/specialists/` | Coordinator + Email + Calendar as ADK `sub_agents` (A2A split documented as next step) |
| **MCP Server** | `app/clients/mcp.py`, `app/clients/fake.py` | MCP client interface + selector wired in; fake clients run by default — real Gmail/Calendar calls activate with `LIFEOPS_USE_MCP=1` during `agents-cli playground` |
| **Security features** | `app/core/` + `policy.yaml` + `tests/integration/test_safety_invariant.py` | Policy Server, PII filter, HITL gate — all enforced at the Action Bus chokepoint; Coordinator holds no credentials; Token Broker interface built + unit-tested (live wiring is a follow-up) |
| **Deployability** | `Dockerfile`, `agents-cli-manifest.yaml`, `pyproject.toml` | Deploy-ready interfaces; `agents-cli deploy` path; containerized via Dockerfile |

---

## Security Notes

**No API keys or secrets are committed to this repository.**

- `policy.yaml` is the only external configuration; it contains no credentials.
- `.env` is in `.gitignore`.
- The Token Broker interface uses a local encrypted secret store; no cloud KMS is required for v1 (live wiring to the execute path is a planned follow-up).
- Use a dedicated test Google account for demos to avoid personal-data exposure.

---

## Repo Layout

```
app/
  coordinator/agent.py          # routing, conversation, planning
  specialists/
    email_agent.py              # ADK sub-agent; Gmail tools; proposes only
    calendar_agent.py           # ADK sub-agent; Calendar tools; proposes only
  core/
    action_bus.py               # single chokepoint
    policy_server.py            # pure evaluate() function
    pii_filter.py               # detect / tokenize / restore
    token_broker.py             # JIT downscoped credentials
    state.py                    # SQLite backend
    executor.py                 # performs writes after allow/approval
    types.py                    # ProposedAction, Verdict, action/status constants
  clients/
    base.py                     # EmailClient / CalendarClient protocol
    fake.py                     # in-process fakes (default)
    mcp.py                      # real Gmail + Calendar via MCP (LIFEOPS_USE_MCP=1)
  triggers/
    interactive.py              # CLI/playground channel
    ambient.py                  # schedule / new-mail poll
  app_utils/telemetry.py        # OpenTelemetry spans
  agent.py                      # agents-cli entrypoint
policy.yaml                     # tiered-risk policy (deny-by-default)
tests/
  unit/                         # Policy Server, PII filter, Action Bus, etc.
  integration/                  # chokepoint invariant, coordinator↔specialist flows
  eval/                         # golden dataset + eval config
```

---

## License

Apache 2.0
