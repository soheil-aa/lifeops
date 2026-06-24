# Coding Agent Guide

## Prerequisites

Install the CLI (one-time):
```bash
uv tool install google-agents-cli
```

Install project dependencies:
```bash
uv sync --dev
```

---

## Development Phases

### Phase 1: Understand Requirements
Before writing any code, understand the project's requirements, constraints, and success criteria.
Read `README.md` for the architecture overview and `policy.yaml` for the trust model.

### Phase 2: Build and Implement
Implement agent logic in `app/`. The key seams are:

- `app/core/types.py` — `ProposedAction`, `Verdict`, action and status constants (source of truth)
- `app/core/action_bus.py` — `ActionBus(policy, state, executor, known_contacts)` — the single chokepoint
- `app/core/policy_server.py` — `PolicyServer.evaluate(action, context) -> Verdict`
- `app/specialists/email_agent.py` — `build_email_agent(bus, client, id_factory?)`
- `app/specialists/calendar_agent.py` — `build_calendar_agent(bus, client, id_factory?)`
- `app/coordinator/agent.py` — `build_coordinator(email_agent, calendar_agent)`

Use `uv run agents-cli playground` for interactive testing. Iterate based on user feedback.

**Core invariant:** specialists never execute an external write directly — they can only
*propose* to the Action Bus, which enforces PII filter → Policy Server → HITL in sequence.
This invariant is proven by `tests/integration/test_safety_invariant.py`.

### Phase 3: The Evaluation Loop (Main Iteration Phase)
Start with 1-2 eval cases, run `agents-cli eval generate`, then `agents-cli eval grade`.
Iterate by making changes and rerunning both commands until satisfied. The headline metric
is **safety-gate precision/recall** — the agent must never auto-execute something that
should have needed approval.

Once you have a baseline:
- `agents-cli eval compare` — regression diffs between grade-result files
- `agents-cli eval analyze` — cluster failure modes
- `agents-cli eval optimize` — auto-tune prompts

The golden dataset is at `tests/eval/datasets/safety-gate.json`; config at
`tests/eval/eval_config.yaml`. Grading requires ADC (live Gemini model).

### Phase 4: Pre-Deployment Tests
Run `uv run pytest tests/unit tests/integration`. Fix issues until all tests pass.
Expected: 53+ tests passing. All tests run offline (no Google credentials required).

### Phase 5: Deploy to Dev
**Requires explicit human approval.** Run `agents-cli deploy` only after user confirms.
See the **Deployment Guide** for details.

### Phase 6: Production Deployment
Ask the user: Option A (simple single-project) or Option B (full CI/CD pipeline with
`agents-cli infra cicd`).

---

## Development Commands

| Command | Purpose |
|---------|---------|
| `uv run agents-cli playground` | Interactive local testing (fake clients by default) |
| `LIFEOPS_USE_MCP=1 uv run agents-cli playground` | Interactive testing with real Gmail/Calendar MCP |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests (offline) |
| `agents-cli eval generate` | Run agent on eval dataset, produce traces |
| `agents-cli eval grade` | Score traces with LLM-as-judge (requires ADC) |
| `agents-cli eval compare` | Compare two grade-results files (regression check) |
| `agents-cli eval analyze` | Cluster failure modes from grade results |
| `agents-cli eval metric list` | List built-in metrics available in the SDK |
| `agents-cli eval optimize` | Auto-tune agent prompts using eval data |
| `agents-cli lint` | Check code quality |
| `agents-cli infra single-project` | Set up project infrastructure (Terraform) |
| `agents-cli deploy` | Deploy to dev |
| `agents-cli scaffold enhance` | Add deployment target or CI/CD to project |
| `agents-cli scaffold upgrade` | Upgrade project to latest version |

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `LIFEOPS_USE_MCP` | Set to `1` to use real Gmail + Calendar MCP servers | unset (fake clients) |
| `LIFEOPS_DB` | Path to SQLite state file | `lifeops.db` |
| `GOOGLE_API_KEY` | Gemini API key (alternative to ADC) | unset |
| `GOOGLE_CLOUD_PROJECT` | GCP project for Vertex AI | set from ADC |

---

## Operational Guidelines for Coding Agents

- **Code preservation**: Only modify code directly targeted by the user's request. Preserve all surrounding code, config values (e.g., `model`), comments, and formatting.
- **NEVER change the model** unless explicitly asked.
- **Model 404 errors**: Fix `GOOGLE_CLOUD_LOCATION` (e.g., `global` instead of `us-east1`), not the model name.
- **ADK tool imports**: Import the tool instance, not the module: `from google.adk.tools.load_web_page import load_web_page`
- **Run Python with `uv`**: `uv run python script.py`. Run `uv sync --dev` first.
- **Stop on repeated errors**: If the same error appears 3+ times, fix the root cause instead of retrying.
- **Terraform conflicts** (Error 409): Use `terraform import` instead of retrying creation.
- **Policy changes**: Edit `policy.yaml`, not Python code, to change what actions are allowed.
- **Safety invariant**: Any change that allows a write to bypass the Action Bus chokepoint
  is a bug. Run `uv run pytest tests/integration/test_safety_invariant.py` after any core change.
- **No secrets in code**: Credentials are managed via ADC or the Token Broker. Never
  hardcode API keys, OAuth tokens, or passwords in source files.
