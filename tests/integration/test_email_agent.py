import itertools

from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.specialists import email_agent as ea


def _bus(tmp_path):
    policy = PolicyServer(load_policy("policy.yaml"))
    state = SqliteStateStore(str(tmp_path / "s.db"))
    email = FakeEmailClient(inbox=[{"from": "a@known.com", "subject": "Hi"}])
    bus = ActionBus(policy, state, Executor(email, FakeCalendarClient()), known_contacts={"a@known.com"})
    return bus, state, email


def test_build_email_agent_exposes_expected_tools(tmp_path):
    bus, _, email = _bus(tmp_path)
    agent = ea.build_email_agent(bus, email)
    assert agent.name == "email_agent"
    tool_names = {t.__name__ for t in agent.tools}
    assert {"read_inbox", "propose_send_email", "propose_save_draft"} <= tool_names


def test_propose_send_tool_routes_through_bus(tmp_path):
    bus, state, email = _bus(tmp_path)
    ids = (f"id{i}" for i in itertools.count())
    agent = ea.build_email_agent(bus, email, id_factory=lambda: next(ids))
    propose_send = next(t for t in agent.tools if t.__name__ == "propose_send_email")
    result = propose_send(to="a@known.com", subject="Hi", body="no pii")
    assert "require_approval" in result.lower()
    assert email.sent == []  # proposing never executes
    assert any(a.action == "email.send" for a in state.pending())


def test_propose_send_to_stranger_is_denied(tmp_path):
    bus, state, email = _bus(tmp_path)
    ids = (f"id{i}" for i in itertools.count())
    agent = ea.build_email_agent(bus, email, id_factory=lambda: next(ids))
    propose_send = next(t for t in agent.tools if t.__name__ == "propose_send_email")
    result = propose_send(to="stranger@evil.com", subject="Hi", body="x")
    assert "deny" in result.lower()
    assert email.sent == []
