import pytest

from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.executor import Executor
from app.core.types import ProposedAction, EMAIL_SEND, CALENDAR_CREATE


def _exec():
    email, cal = FakeEmailClient(), FakeCalendarClient()
    return Executor(email, cal), email, cal


def test_execute_email_send_calls_client():
    ex, email, _ = _exec()
    action = ProposedAction(id="a1", action=EMAIL_SEND,
                            params={"to": ["x@y.com"], "subject": "Hi", "body": "Yo"}, origin="e")
    ex.execute(action)
    assert email.sent == [(["x@y.com"], "Hi", "Yo")]


def test_execute_calendar_create_calls_client():
    ex, _, cal = _exec()
    action = ProposedAction(id="a2", action=CALENDAR_CREATE,
                            params={"title": "Sync", "start": "2026-06-26T15:00", "end": "2026-06-26T15:30", "attendees": []}, origin="c")
    ex.execute(action)
    assert cal.created and cal.created[0][0] == "Sync"


def test_execute_unknown_action_raises():
    ex, _, _ = _exec()
    with pytest.raises(ValueError):
        ex.execute(ProposedAction(id="a3", action="email.delete_all", params={}, origin="e"))
