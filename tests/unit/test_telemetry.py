from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.core.types import ProposedAction, EMAIL_SEND


def test_propose_emits_span(tmp_path):
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    policy = PolicyServer(load_policy("policy.yaml"))
    state = SqliteStateStore(str(tmp_path / "s.db"))
    bus = ActionBus(policy, state, Executor(FakeEmailClient(), FakeCalendarClient()), known_contacts={"a@known.com"})
    bus.propose(ProposedAction(id="t1", action=EMAIL_SEND,
                params={"to": ["a@known.com"], "subject": "s", "body": "b"}, origin="email_agent"))

    spans = exporter.get_finished_spans()
    assert any(s.name == "action_bus.propose" for s in spans)
    propose_span = next(s for s in spans if s.name == "action_bus.propose")
    assert propose_span.attributes["action"] == "email.send"
    assert propose_span.attributes["decision"] == "require_approval"
