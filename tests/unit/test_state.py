from app.core.state import SqliteStateStore
from app.core.types import ProposedAction, EMAIL_SEND, PENDING, APPROVED


def _store(tmp_path):
    return SqliteStateStore(str(tmp_path / "state.db"))


def test_enqueue_and_get_roundtrip(tmp_path):
    store = _store(tmp_path)
    action = ProposedAction(id="a1", action=EMAIL_SEND, params={"to": ["x@y.com"]}, origin="email_agent")
    store.enqueue(action)
    got = store.get("a1")
    assert got is not None
    assert got.action == EMAIL_SEND
    assert got.params == {"to": ["x@y.com"]}
    assert got.status == PENDING


def test_pending_lists_only_pending(tmp_path):
    store = _store(tmp_path)
    store.enqueue(ProposedAction(id="a1", action=EMAIL_SEND, params={}, origin="e"))
    store.enqueue(ProposedAction(id="a2", action=EMAIL_SEND, params={}, origin="e"))
    store.update_status("a2", APPROVED)
    pending_ids = {a.id for a in store.pending()}
    assert pending_ids == {"a1"}


def test_get_missing_returns_none(tmp_path):
    assert _store(tmp_path).get("nope") is None
