import pytest

from app.core.policy_server import load_policy, PolicyServer
from app.core.types import (
    ProposedAction, EMAIL_READ, EMAIL_SEND, CALENDAR_CREATE,
)


@pytest.fixture
def server():
    policy = load_policy("policy.yaml")
    return PolicyServer(policy)


def _action(name, **params):
    return ProposedAction(id="t", action=name, params=params, origin="test")


def test_read_is_allowed(server):
    v = server.evaluate(_action(EMAIL_READ), context={})
    assert v.decision == "allow"


def test_send_to_known_contact_requires_approval(server):
    ctx = {"known_contacts": {"a@known.com"}, "pii_to_external": False}
    v = server.evaluate(_action(EMAIL_SEND, to=["a@known.com"]), context=ctx)
    assert v.decision == "require_approval"


def test_send_to_unknown_recipient_is_denied(server):
    ctx = {"known_contacts": {"a@known.com"}, "pii_to_external": False}
    v = server.evaluate(_action(EMAIL_SEND, to=["stranger@evil.com"]), context=ctx)
    assert v.decision == "deny"
    assert "recipients_in" in v.violated


def test_send_with_pii_to_external_is_denied(server):
    ctx = {"known_contacts": {"a@known.com"}, "pii_to_external": True}
    v = server.evaluate(_action(EMAIL_SEND, to=["a@known.com"]), context=ctx)
    assert v.decision == "deny"
    assert "no_pii_to_external" in v.violated


def test_too_many_recipients_is_denied(server):
    ctx = {"known_contacts": {f"u{i}@known.com" for i in range(10)}, "pii_to_external": False}
    recips = [f"u{i}@known.com" for i in range(6)]
    v = server.evaluate(_action(EMAIL_SEND, to=recips), context=ctx)
    assert v.decision == "deny"
    assert "max_recipients" in v.violated


def test_unmatched_action_is_denied_by_default(server):
    v = server.evaluate(_action("email.delete_all"), context={})
    assert v.decision == "deny"


def test_calendar_create_requires_approval(server):
    v = server.evaluate(_action(CALENDAR_CREATE, title="Sync"), context={})
    assert v.decision == "require_approval"
