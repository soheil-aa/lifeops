import importlib

from app.clients.fake import FakeEmailClient, FakeCalendarClient


def test_build_clients_defaults_to_fakes(monkeypatch):
    monkeypatch.delenv("LIFEOPS_USE_MCP", raising=False)
    from app.clients import mcp
    importlib.reload(mcp)
    email, cal = mcp.build_clients()
    assert isinstance(email, FakeEmailClient)
    assert isinstance(cal, FakeCalendarClient)
