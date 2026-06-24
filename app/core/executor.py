from __future__ import annotations

from app.clients.base import CalendarClient, EmailClient
from app.core.types import (
    ProposedAction, EMAIL_DRAFT_SAVE, EMAIL_SEND,
    CALENDAR_CREATE, CALENDAR_ACCEPT,
)


class Executor:
    """Performs the real client side-effect for an approved/allowed action.

    Only the Action Bus calls this, and only after a policy allow (+ approval
    when required). Specialists never hold a reference to it.
    """

    def __init__(self, email: EmailClient, calendar: CalendarClient):
        self._email = email
        self._calendar = calendar

    def execute(self, action: ProposedAction) -> str:
        p = action.params
        if action.action == EMAIL_SEND:
            return self._email.send(p["to"], p["subject"], p["body"])
        if action.action == EMAIL_DRAFT_SAVE:
            return self._email.save_draft(p["to"], p["subject"], p["body"])
        if action.action == CALENDAR_CREATE:
            return self._calendar.create_event(p["title"], p["start"], p["end"], p.get("attendees", []))
        if action.action == CALENDAR_ACCEPT:
            return self._calendar.accept_invite(p["event_id"])
        raise ValueError(f"Executor cannot execute action: {action.action}")
