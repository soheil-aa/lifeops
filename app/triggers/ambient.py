from __future__ import annotations

from app.clients.base import CalendarClient, EmailClient


def build_briefing(email: EmailClient, calendar: CalendarClient, day: str,
                   inbox_limit: int = 10) -> str:
    """Read-only morning briefing. Emits no proposals — pure read path."""
    msgs = email.read_inbox(inbox_limit)
    events = calendar.list_events(day)
    event_lines = "\n".join(f"  - {e.get('title')}" for e in events) or "  (none)"
    return f"Good morning. {len(msgs)} new messages.\nToday's events:\n{event_lines}"
