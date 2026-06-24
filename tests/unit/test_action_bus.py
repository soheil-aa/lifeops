import pytest

from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.core.types import (
    ProposedAction, EMAIL_SEND, EMAIL_READ, EXECUTED, PENDING, BLOCKED, DENIED,
)


@pytest.fixture
def bus_setup(tmp_path):
    policy = PolicyServer(load_policy("policy.yaml"))
    state = SqliteStateStore(str(tmp_path / "s.db"))
    email, cal = FakeEmailClient(), FakeCalendarClient()
    executor = Executor(email, cal)
    bus = ActionBus(policy, state, executor, known_contacts={"friend@known.com"})
    return bus, state, email


def test_allow_executes_immediately(bus_setup):
    bus, state, email = bus_setup
    # draft_save is allow; use email.draft_save
    from app.core.types import EMAIL_DRAFT_SAVE
    a = ProposedAction(id="d1", action=EMAIL_DRAFT_SAVE,
                       params={"to": ["friend@known.com"], "subject": "x", "body": "y"}, origin="email_agent")
    v = bus.propose(a)
    assert v.decision == "allow"
    assert state.get("d1").status == EXECUTED
    assert email.drafts  # executed


def test_require_approval_enqueues_and_does_not_execute(bus_setup):
    bus, state, email = bus_setup
    a = ProposedAction(id="s1", action=EMAIL_SEND,
                       params={"to": ["friend@known.com"], "subject": "Hi", "body": "no pii here"}, origin="email_agent")
    v = bus.propose(a)
    assert v.decision == "require_approval"
    assert state.get("s1").status == PENDING
    assert email.sent == []  # NOT executed yet


def test_approve_executes_pending(bus_setup):
    bus, state, email = bus_setup
    a = ProposedAction(id="s2", action=EMAIL_SEND,
                       params={"to": ["friend@known.com"], "subject": "Hi", "body": "ok"}, origin="email_agent")
    bus.propose(a)
    bus.approve("s2")
    assert state.get("s2").status == EXECUTED
    assert email.sent and email.sent[0][0] == ["friend@known.com"]


def test_deny_blocks_send_to_stranger(bus_setup):
    bus, state, email = bus_setup
    a = ProposedAction(id="s3", action=EMAIL_SEND,
                       params={"to": ["stranger@evil.com"], "subject": "Hi", "body": "ok"}, origin="email_agent")
    v = bus.propose(a)
    assert v.decision == "deny"
    assert state.get("s3").status == BLOCKED
    assert email.sent == []


def test_pii_to_external_is_blocked(bus_setup):
    bus, state, email = bus_setup
    # recipient is known, but body leaks an email address to them -> pii_to_external only
    # triggers when a recipient is external; known recipient => not external => allowed-to-approve.
    # Force external by adding an unknown recipient too (also trips recipients_in -> deny).
    a = ProposedAction(id="s4", action=EMAIL_SEND,
                       params={"to": ["stranger@evil.com"], "subject": "Hi", "body": "ssn 4111 1111 1111 1111"}, origin="email_agent")
    v = bus.propose(a)
    assert v.decision == "deny"
    assert email.sent == []


def test_approve_non_pending_raises(bus_setup):
    bus, _, _ = bus_setup
    with pytest.raises(ValueError):
        bus.approve("does-not-exist")


# --- _build_context isolation tests for pii_to_external ---

def test_build_context_pii_to_external_false_when_known_recipient(bus_setup):
    """known recipient + PII body => pii_to_external is False (no external recipient)."""
    bus, _, _ = bus_setup
    a = ProposedAction(id="ctx1", action=EMAIL_SEND,
                       params={"to": ["friend@known.com"], "subject": "x",
                               "body": "ssn 4111 1111 1111 1111"},
                       origin="email_agent")
    ctx = bus._build_context(a)
    assert ctx["pii_to_external"] is False


def test_build_context_pii_to_external_true_when_external_and_pii(bus_setup):
    """external recipient + PII body => pii_to_external is True."""
    bus, _, _ = bus_setup
    a = ProposedAction(id="ctx2", action=EMAIL_SEND,
                       params={"to": ["external@unknown.com"], "subject": "x",
                               "body": "ssn 4111 1111 1111 1111"},
                       origin="email_agent")
    ctx = bus._build_context(a)
    assert ctx["pii_to_external"] is True


def test_build_context_pii_to_external_false_when_external_no_pii(bus_setup):
    """external recipient but body has NO PII => pii_to_external is False."""
    bus, _, _ = bus_setup
    a = ProposedAction(id="ctx3", action=EMAIL_SEND,
                       params={"to": ["external@unknown.com"], "subject": "x",
                               "body": "hello, no sensitive data here"},
                       origin="email_agent")
    ctx = bus._build_context(a)
    assert ctx["pii_to_external"] is False
