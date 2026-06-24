from __future__ import annotations

from typing import Any

import yaml

from app.core.types import ProposedAction, Verdict


def load_policy(path: str) -> dict:
    """Load and parse the YAML policy file into a plain dict."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class PolicyServer:
    """Pure function over (action, context) -> Verdict. Deny-by-default."""

    def __init__(self, policy: dict):
        self._default = policy.get("defaults", "deny")
        self._rules = policy.get("rules", [])

    def _match(self, action_name: str) -> dict | None:
        wildcard = None
        for rule in self._rules:
            pattern = rule.get("action")
            if pattern == action_name:
                return rule
            if pattern == "*":
                wildcard = rule
        return wildcard

    def evaluate(self, action: ProposedAction, context: dict[str, Any]) -> Verdict:
        rule = self._match(action.action)
        if rule is None:
            return Verdict(decision="deny", reason="no matching rule (deny-by-default)")

        base = rule.get("verdict", self._default)
        if base == "deny":
            return Verdict(decision="deny", reason=f"rule denies {action.action}")
        if base == "allow":
            return Verdict(decision="allow", reason=f"rule allows {action.action}")

        # base == "require_approval": enforce constraints; any violation downgrades to deny.
        violated = self._check_constraints(rule.get("constraints", {}), action, context)
        if violated:
            return Verdict(
                decision="deny",
                reason=f"{action.action} violates {', '.join(violated)}",
                violated=tuple(violated),
            )
        return Verdict(decision="require_approval", reason=f"{action.action} needs approval")

    def _check_constraints(
        self, constraints: dict, action: ProposedAction, context: dict
    ) -> list[str]:
        violated: list[str] = []
        recipients = action.params.get("to", []) or []

        if "recipients_in" in constraints:
            known = context.get("known_contacts", set())
            if any(r not in known for r in recipients):
                violated.append("recipients_in")

        if "max_recipients" in constraints:
            if len(recipients) > int(constraints["max_recipients"]):
                violated.append("max_recipients")

        if constraints.get("no_pii_to_external") and context.get("pii_to_external"):
            violated.append("no_pii_to_external")

        return violated
