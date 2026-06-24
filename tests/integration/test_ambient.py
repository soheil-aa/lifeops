from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.triggers.ambient import build_briefing


def test_briefing_summarizes_inbox_and_day():
    email = FakeEmailClient(inbox=[{"from": "a", "subject": "x"}, {"from": "b", "subject": "y"}])
    cal = FakeCalendarClient(events=[{"day": "2026-06-26", "title": "Standup"}])
    text = build_briefing(email, cal, day="2026-06-26")
    assert "2" in text  # two messages
    assert "Standup" in text
