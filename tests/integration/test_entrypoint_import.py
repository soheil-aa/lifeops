"""Integration test: app.agent must be importable without Google ADC credentials.

The entrypoint is credential-safe — it wraps google.auth.default() in a
try/except so that offline/CI environments can import and use the module
without raising DefaultCredentialsError.
"""
import app.agent


def test_root_agent_name():
    assert app.agent.root_agent.name == "coordinator"


def test_root_agent_sub_agents():
    sub_names = {a.name for a in app.agent.root_agent.sub_agents}
    assert sub_names == {"email_agent", "calendar_agent"}


def test_app_is_not_none():
    assert app.agent.app is not None
