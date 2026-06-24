# tests/integration/test_interactive.py
from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.core.types import ProposedAction, EMAIL_SEND, EXECUTED, DENIED
from app.triggers.interactive import format_pending, resolve


def _bus(tmp_path):
    policy = PolicyServer(load_policy("policy.yaml"))
    state = SqliteStateStore(str(tmp_path / "s.db"))
    email = FakeEmailClient()
    bus = ActionBus(policy, state, Executor(email, FakeCalendarClient()), known_contacts={"a@known.com"})
    return bus, state, email


def test_format_pending_lists_ids(tmp_path):
    bus, state, _ = _bus(tmp_path)
    bus.propose(ProposedAction(id="p1", action=EMAIL_SEND,
                               params={"to": ["a@known.com"], "subject": "s", "body": "b"}, origin="e"))
    text = format_pending(state)
    assert "p1" in text


def test_resolve_approves_and_denies(tmp_path):
    bus, state, email = _bus(tmp_path)
    bus.propose(ProposedAction(id="p1", action=EMAIL_SEND,
                               params={"to": ["a@known.com"], "subject": "s", "body": "b"}, origin="e"))
    bus.propose(ProposedAction(id="p2", action=EMAIL_SEND,
                               params={"to": ["a@known.com"], "subject": "s2", "body": "b2"}, origin="e"))
    out = resolve(bus, {"p1": True, "p2": False})
    assert state.get("p1").status == EXECUTED
    assert state.get("p2").status == DENIED
    assert len(email.sent) == 1
