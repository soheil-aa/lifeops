# app/triggers/interactive.py
from __future__ import annotations

from app.core.action_bus import ActionBus
from app.core.state import StateStore


def format_pending(state: StateStore) -> str:
    rows = state.pending()
    if not rows:
        return "No pending actions."
    lines = ["Pending actions (approve/deny by id):"]
    for a in rows:
        lines.append(f"  [{a.id}] {a.action} params={a.params}")
    return "\n".join(lines)


def resolve(bus: ActionBus, decisions: dict[str, bool]) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    for action_id, approve in decisions.items():
        if approve:
            bus.approve(action_id)
            outcomes[action_id] = "executed"
        else:
            bus.deny(action_id)
            outcomes[action_id] = "denied"
    return outcomes


def main() -> None:  # pragma: no cover - thin REPL shell
    raise SystemExit(
        "Run via `agents-cli playground` for conversation; use format_pending/resolve "
        "for the approval queue. A full REPL wires these to stdin."
    )
