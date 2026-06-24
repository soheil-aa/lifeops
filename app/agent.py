# ruff: noqa
# app/agent.py — agents-cli entrypoint. Wires the shared chokepoint + agents.
from __future__ import annotations

import os

import google.auth
from google.adk.apps import App

from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.coordinator.agent import build_coordinator
from app.specialists.email_agent import build_email_agent
from app.specialists.calendar_agent import build_calendar_agent

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Phase 10 swaps these fakes for MCP-backed clients via build_clients().
_email = FakeEmailClient()
_calendar = FakeCalendarClient()
_policy = PolicyServer(load_policy("policy.yaml"))
_state = SqliteStateStore(os.environ.get("LIFEOPS_DB", "lifeops.db"))
_bus = ActionBus(_policy, _state, Executor(_email, _calendar), known_contacts=set())

root_agent = build_coordinator(
    build_email_agent(_bus, _email),
    build_calendar_agent(_bus, _calendar),
)
app = App(root_agent=root_agent, name="app")
