# ruff: noqa
# app/agent.py — agents-cli entrypoint. Wires the shared chokepoint + agents.
from __future__ import annotations

import os

import google.auth
import google.auth.exceptions
from google.adk.apps import App

from app.clients.mcp import build_clients
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.coordinator.agent import build_coordinator
from app.specialists.email_agent import build_email_agent
from app.specialists.calendar_agent import build_calendar_agent

try:
    _, project_id = google.auth.default()
    # project_id may be None when ADC credentials exist but have no project set
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
except google.auth.exceptions.DefaultCredentialsError:
    # ADC unavailable → offline/fake mode; real runs need ADC or GOOGLE_API_KEY
    pass

_email, _calendar = build_clients()
_policy = PolicyServer(load_policy("policy.yaml"))
_state = SqliteStateStore(os.environ.get("LIFEOPS_DB", "lifeops.db"))
_bus = ActionBus(_policy, _state, Executor(_email, _calendar), known_contacts=set())

root_agent = build_coordinator(
    build_email_agent(_bus, _email),
    build_calendar_agent(_bus, _calendar),
)
app = App(root_agent=root_agent, name="app")
