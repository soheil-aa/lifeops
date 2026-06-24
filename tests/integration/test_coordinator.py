from app.clients.fake import FakeEmailClient, FakeCalendarClient
from app.core.action_bus import ActionBus
from app.core.executor import Executor
from app.core.policy_server import PolicyServer, load_policy
from app.core.state import SqliteStateStore
from app.coordinator.agent import build_coordinator
from app.specialists.email_agent import build_email_agent
from app.specialists.calendar_agent import build_calendar_agent


def test_coordinator_wires_two_subagents(tmp_path):
    policy = PolicyServer(load_policy("policy.yaml"))
    state = SqliteStateStore(str(tmp_path / "s.db"))
    email, cal = FakeEmailClient(), FakeCalendarClient()
    bus = ActionBus(policy, state, Executor(email, cal), known_contacts=set())
    coord = build_coordinator(build_email_agent(bus, email), build_calendar_agent(bus, cal))
    assert coord.name == "coordinator"
    sub_names = {a.name for a in coord.sub_agents}
    assert sub_names == {"email_agent", "calendar_agent"}
