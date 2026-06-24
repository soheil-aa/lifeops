import itertools

from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.specialists import calendar_agent as ca


def _bus(tmp_path):
    policy = PolicyServer(load_policy("policy.yaml"))
    state = SqliteStateStore(str(tmp_path / "s.db"))
    cal = FakeCalendarClient(events=[{"day": "2026-06-26", "title": "Standup"}])
    bus = ActionBus(policy, state, Executor(FakeEmailClient(), cal), known_contacts=set())
    return bus, state, cal


def test_build_calendar_agent_exposes_tools(tmp_path):
    bus, _, cal = _bus(tmp_path)
    agent = ca.build_calendar_agent(bus, cal)
    assert agent.name == "calendar_agent"
    tool_names = {t.__name__ for t in agent.tools}
    assert {"list_day", "propose_create_event", "propose_accept_invite"} <= tool_names


def test_propose_create_requires_approval_and_does_not_execute(tmp_path):
    bus, state, cal = _bus(tmp_path)
    ids = (f"c{i}" for i in itertools.count())
    agent = ca.build_calendar_agent(bus, cal, id_factory=lambda: next(ids))
    propose_create = next(t for t in agent.tools if t.__name__ == "propose_create_event")
    result = propose_create(title="Sync", start="2026-06-26T15:00", end="2026-06-26T15:30", attendees="a@known.com")
    assert "require_approval" in result.lower()
    assert cal.created == []
    assert any(a.action == "calendar.create" for a in state.pending())
