from __future__ import annotations


class FakeEmailClient:
    def __init__(self, inbox: list[dict] | None = None):
        self._inbox = inbox or []
        self.sent: list[tuple] = []
        self.drafts: list[tuple] = []

    def read_inbox(self, limit: int) -> list[dict]:
        return self._inbox[:limit]

    def save_draft(self, to: list[str], subject: str, body: str) -> str:
        self.drafts.append((to, subject, body))
        return f"draft-{len(self.drafts)}"

    def send(self, to: list[str], subject: str, body: str) -> str:
        self.sent.append((to, subject, body))
        return f"sent-{len(self.sent)}"


class FakeCalendarClient:
    def __init__(self, events: list[dict] | None = None):
        self._events = events or []
        self.created: list[tuple] = []
        self.accepted: list[str] = []

    def list_events(self, day: str) -> list[dict]:
        return [e for e in self._events if e.get("day") == day]

    def create_event(self, title: str, start: str, end: str, attendees: list[str]) -> str:
        self.created.append((title, start, end, attendees))
        return f"event-{len(self.created)}"

    def accept_invite(self, event_id: str) -> str:
        self.accepted.append(event_id)
        return f"accepted-{event_id}"
