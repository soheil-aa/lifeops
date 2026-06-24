from __future__ import annotations

from typing import Callable
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.clients.base import CalendarClient
from app.core.action_bus import ActionBus
from app.core.types import ProposedAction, CALENDAR_CREATE, CALENDAR_ACCEPT


def build_calendar_agent(
    bus: ActionBus,
    client: CalendarClient,
    id_factory: Callable[[], str] = lambda: uuid4().hex,
) -> Agent:
    """Build the Calendar specialist. Tools may only READ or PROPOSE."""

    def list_day(day: str) -> str:
        """List events for a given day (YYYY-MM-DD)."""
        events = client.list_events(day)
        return "\n".join(f"- {e.get('title')}" for e in events) or "(no events)"

    def propose_create_event(title: str, start: str, end: str, attendees: str) -> str:
        """Propose creating a calendar event. Does NOT create; routes to the gate.

        Args:
            title: Event title.
            start: ISO start datetime.
            end: ISO end datetime.
            attendees: Comma-separated attendee emails.
        Returns:
            The policy verdict and its reason.
        """
        action = ProposedAction(
            id=id_factory(), action=CALENDAR_CREATE,
            params={"title": title, "start": start, "end": end,
                    "attendees": [a.strip() for a in attendees.split(",") if a.strip()]},
            origin="calendar_agent",
        )
        v = bus.propose(action)
        return f"{v.decision}: {v.reason} (action_id={action.id})"

    def propose_accept_invite(event_id: str) -> str:
        """Propose accepting a calendar invite. Routes to the gate.

        Args:
            event_id: The invite's event id.
        Returns:
            The policy verdict and its reason.
        """
        action = ProposedAction(
            id=id_factory(), action=CALENDAR_ACCEPT,
            params={"event_id": event_id}, origin="calendar_agent",
        )
        v = bus.propose(action)
        return f"{v.decision}: {v.reason} (action_id={action.id})"

    return Agent(
        name="calendar_agent",
        model=Gemini(model="gemini-flash-latest",
                     retry_options=types.HttpRetryOptions(attempts=3)),
        instruction=(
            "You manage the calendar. You may read events and PROPOSE creating "
            "events or accepting invites. You can never write directly; proposing "
            "routes through a safety gate that may require human approval."
        ),
        tools=[list_day, propose_create_event, propose_accept_invite],
    )
