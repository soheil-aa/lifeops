from __future__ import annotations

from app.core import pii_filter
from app.core.executor import Executor
from app.core.policy_server import PolicyServer
from app.core.state import StateStore
from app.core.types import (
    ProposedAction, Verdict, PENDING, EXECUTED, BLOCKED, DENIED,
)


class ActionBus:
    """The single chokepoint: every world-changing action passes through here.

    propose() runs PII + policy; only allow (now) or approve (later) reach the
    Executor. Specialists call propose() and nothing else.
    """

    def __init__(self, policy: PolicyServer, state: StateStore,
                 executor: Executor, known_contacts: set[str]):
        self._policy = policy
        self._state = state
        self._executor = executor
        self._known = known_contacts

    def _build_context(self, action: ProposedAction) -> dict:
        recipients = action.params.get("to", []) or []
        has_external = any(r not in self._known for r in recipients)
        body = action.params.get("body", "") or ""
        pii_to_external = has_external and pii_filter.contains_pii(body)
        return {"known_contacts": self._known, "pii_to_external": pii_to_external}

    def propose(self, action: ProposedAction) -> Verdict:
        verdict = self._policy.evaluate(action, self._build_context(action))
        if verdict.decision == "allow":
            self._executor.execute(action)
            self._state.enqueue(action)
            self._state.update_status(action.id, EXECUTED)
        elif verdict.decision == "require_approval":
            self._state.enqueue(action)
        else:  # deny
            self._state.enqueue(action)
            self._state.update_status(action.id, BLOCKED)
        return verdict

    def approve(self, action_id: str) -> str:
        action = self._state.get(action_id)
        if action is None or action.status != PENDING:
            raise ValueError(f"action {action_id} is not pending approval")
        result = self._executor.execute(action)
        self._state.update_status(action_id, EXECUTED)
        return result

    def deny(self, action_id: str) -> None:
        """Mark action as DENIED. Silently no-ops on unknown ids (no error contract in v1)."""
        self._state.update_status(action_id, DENIED)
