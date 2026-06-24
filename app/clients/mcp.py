from __future__ import annotations

import os

from app.clients.base import CalendarClient, EmailClient
from app.clients.fake import FakeCalendarClient, FakeEmailClient


class GmailMcpClient:
    """EmailClient backed by the connected Gmail MCP server.

    Methods call the MCP tools exposed to the agents-cli runtime. Wired during
    manual playground testing; see README for MCP server configuration.
    """

    def read_inbox(self, limit: int) -> list[dict]:
        raise NotImplementedError("wire to Gmail MCP search/list tool")

    def save_draft(self, to: list[str], subject: str, body: str) -> str:
        raise NotImplementedError("wire to Gmail MCP create_draft tool")

    def send(self, to: list[str], subject: str, body: str) -> str:
        raise NotImplementedError("wire to Gmail MCP send tool")


class GoogleCalendarMcpClient:
    """CalendarClient backed by the connected Google Calendar MCP server."""

    def list_events(self, day: str) -> list[dict]:
        raise NotImplementedError("wire to Calendar MCP list_events tool")

    def create_event(self, title: str, start: str, end: str, attendees: list[str]) -> str:
        raise NotImplementedError("wire to Calendar MCP create_event tool")

    def accept_invite(self, event_id: str) -> str:
        raise NotImplementedError("wire to Calendar MCP respond_to_event tool")


def build_clients() -> tuple[EmailClient, CalendarClient]:
    if os.environ.get("LIFEOPS_USE_MCP") == "1":
        return GmailMcpClient(), GoogleCalendarMcpClient()
    return FakeEmailClient(), FakeCalendarClient()
