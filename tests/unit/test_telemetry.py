import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.core.types import ProposedAction, EMAIL_SEND, PENDING

# ---------------------------------------------------------------------------
# OTel provider fixture
#
# OTel's global provider can only be set once (after the initial ProxyTracerProvider).
# We create one module-level provider wired to a shared exporter; each test gets
# a fresh per-function exporter that's swapped in/out of the processor list, so
# spans don't bleed across tests.  The module-scoped provider is registered on
# first use and the prior ProxyTracerProvider is restored on teardown where
# possible (no-op if OTel ignores the re-set, which is fine for the test suite).
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def _otel_provider():
    """Register a single TracerProvider for this module; restore prior on teardown."""
    prior = trace.get_tracer_provider()
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    yield provider
    # best-effort restore; OTel ignores the call if provider was already finalized
    try:
        trace.set_tracer_provider(prior)
    except Exception:
        pass


@pytest.fixture
def otel_exporter(_otel_provider):
    """Fresh InMemorySpanExporter per test, wired into the module-level provider."""
    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)
    _otel_provider.add_span_processor(processor)
    yield exporter
    # clear after test so spans don't leak into the next test's assertions
    exporter.clear()


def test_propose_emits_span(tmp_path, otel_exporter):
    policy = PolicyServer(load_policy("policy.yaml"))
    state = SqliteStateStore(str(tmp_path / "s.db"))
    bus = ActionBus(policy, state, Executor(FakeEmailClient(), FakeCalendarClient()), known_contacts={"a@known.com"})
    bus.propose(ProposedAction(id="t1", action=EMAIL_SEND,
                params={"to": ["a@known.com"], "subject": "s", "body": "b"}, origin="email_agent"))

    spans = otel_exporter.get_finished_spans()
    assert any(s.name == "action_bus.propose" for s in spans)
    propose_span = next(s for s in spans if s.name == "action_bus.propose")
    assert propose_span.attributes["action"] == "email.send"
    assert propose_span.attributes["decision"] == "require_approval"
    assert propose_span.attributes["origin"] == "email_agent"


def test_approve_emits_span(tmp_path, otel_exporter):
    policy = PolicyServer(load_policy("policy.yaml"))
    state = SqliteStateStore(str(tmp_path / "s.db"))
    bus = ActionBus(policy, state, Executor(FakeEmailClient(), FakeCalendarClient()), known_contacts={"a@known.com"})

    # propose an action that requires approval (email.send → require_approval by policy)
    action = ProposedAction(id="t2", action=EMAIL_SEND,
                            params={"to": ["a@known.com"], "subject": "s", "body": "b"}, origin="email_agent")
    bus.propose(action)

    # clear spans captured during propose so we can focus on approve
    otel_exporter.clear()

    bus.approve("t2")

    spans = otel_exporter.get_finished_spans()
    assert any(s.name == "action_bus.approve" for s in spans)
    approve_span = next(s for s in spans if s.name == "action_bus.approve")
    assert approve_span.attributes["action"] == "email.send"
    assert approve_span.attributes["origin"] == "email_agent"
    assert approve_span.attributes["approved"] is True
