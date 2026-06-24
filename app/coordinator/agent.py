from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types


def build_coordinator(email_agent: Agent, calendar_agent: Agent) -> Agent:
    """Coordinator: routes to specialists. Holds no credentials of its own."""
    return Agent(
        name="coordinator",
        model=Gemini(model="gemini-flash-latest",
                     retry_options=types.HttpRetryOptions(attempts=3)),
        instruction=(
            "You are a personal concierge for email and calendar. Delegate email "
            "tasks to email_agent and calendar tasks to calendar_agent. For a 'reply "
            "and book a slot' request, use both. You never take actions yourself; "
            "specialists propose actions that may need the user's approval."
        ),
        sub_agents=[email_agent, calendar_agent],
    )
