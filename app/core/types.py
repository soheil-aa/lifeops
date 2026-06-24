from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Decision = Literal["allow", "require_approval", "deny"]

# Action names — the vocabulary policy.yaml and tools agree on.
EMAIL_READ = "email.read"
EMAIL_DRAFT_SAVE = "email.draft_save"
EMAIL_SEND = "email.send"
CALENDAR_READ = "calendar.read"
CALENDAR_HOLD = "calendar.hold_tentative"
CALENDAR_CREATE = "calendar.create"
CALENDAR_ACCEPT = "calendar.accept_invite"

# Proposal lifecycle statuses.
PENDING = "pending"
APPROVED = "approved"
DENIED = "denied"
EXECUTED = "executed"
BLOCKED = "blocked"


@dataclass(frozen=True)
class Verdict:
    decision: Decision
    reason: str
    violated: tuple[str, ...] = ()


@dataclass
class ProposedAction:
    id: str
    action: str
    params: dict[str, Any]
    origin: str
    status: str = PENDING
