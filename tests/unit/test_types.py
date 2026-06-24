# tests/unit/test_types.py
from app.core.types import Verdict, ProposedAction, EMAIL_SEND


def test_verdict_is_frozen_with_defaults():
    v = Verdict(decision="allow", reason="read-only")
    assert v.decision == "allow"
    assert v.violated == ()


def test_proposed_action_defaults_to_pending():
    a = ProposedAction(id="a1", action=EMAIL_SEND, params={"to": ["x@y.com"]}, origin="email_agent")
    assert a.status == "pending"
    assert a.action == "email.send"
