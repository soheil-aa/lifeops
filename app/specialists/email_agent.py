from __future__ import annotations

from typing import Callable
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.clients.base import EmailClient
from app.core.action_bus import ActionBus
from app.core.types import ProposedAction, EMAIL_SEND, EMAIL_DRAFT_SAVE


def build_email_agent(
    bus: ActionBus,
    client: EmailClient,
    id_factory: Callable[[], str] = lambda: uuid4().hex,
) -> Agent:
    """Build the Email specialist. Tools may only READ or PROPOSE — never send."""

    def read_inbox(limit: int) -> str:
        """Read the most recent inbox messages.

        Args:
            limit: How many recent messages to return.
        Returns:
            A formatted string of recent messages.
        """
        msgs = client.read_inbox(limit)
        return "\n".join(f"- {m.get('from')}: {m.get('subject')}" for m in msgs) or "(empty)"

    def propose_send_email(to: str, subject: str, body: str) -> str:
        """Propose sending an email. Does NOT send; routes to the approval gate.

        Args:
            to: Comma-separated recipient email addresses.
            subject: Email subject line.
            body: Email body text.
        Returns:
            The policy verdict (allow / require_approval / deny) and its reason.
        """
        action = ProposedAction(
            id=id_factory(), action=EMAIL_SEND,
            params={"to": [r.strip() for r in to.split(",") if r.strip()],
                    "subject": subject, "body": body},
            origin="email_agent",
        )
        v = bus.propose(action)
        return f"{v.decision}: {v.reason} (action_id={action.id})"

    def propose_save_draft(to: str, subject: str, body: str) -> str:
        """Propose saving a draft reply (reversible, usually auto-allowed).

        Args:
            to: Comma-separated recipient email addresses.
            subject: Email subject line.
            body: Email body text.
        Returns:
            The policy verdict and its reason.
        """
        action = ProposedAction(
            id=id_factory(), action=EMAIL_DRAFT_SAVE,
            params={"to": [r.strip() for r in to.split(",") if r.strip()],
                    "subject": subject, "body": body},
            origin="email_agent",
        )
        v = bus.propose(action)
        return f"{v.decision}: {v.reason} (action_id={action.id})"

    return Agent(
        name="email_agent",
        model=Gemini(model="gemini-flash-latest",
                     retry_options=types.HttpRetryOptions(attempts=3)),
        instruction=(
            "You manage email. You may read the inbox and PROPOSE drafts or sends. "
            "You can never send directly — proposing routes the action through a "
            "safety gate that may require human approval. Never invent recipients."
        ),
        tools=[read_inbox, propose_send_email, propose_save_draft],
    )
