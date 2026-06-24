"""Live LifeOps run — drives the REAL Coordinator (multi-agent, Gemini) through
the ADK Runner. Uses the safe fake email/calendar clients by default.

Requires a Gemini API key in the environment:
    GOOGLE_API_KEY=<google-ai-studio-key> python examples/live.py
"""
from __future__ import annotations

import os


def main() -> None:
    if not os.environ.get("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY not set -> skipping live run.")
        return
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")

    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.agents.run_config import RunConfig, StreamingMode
    from google.genai import types

    from app.agent import root_agent  # import-safe; fake clients by default

    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="demo", app_name="lifeops")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="lifeops")
    msg = types.Content(role="user", parts=[types.Part.from_text(
        text=("Draft a short reply to sarah@example.com confirming Friday lunch, "
              "then tell me whether sending it needs my approval and why."))])
    try:
        for event in runner.run(new_message=msg, user_id="demo", session_id=session.id,
                                run_config=RunConfig(streaming_mode=StreamingMode.SSE)):
            if event.content and event.content.parts:
                for p in event.content.parts:
                    if getattr(p, "text", None):
                        print(p.text, end="")
        print()
    except Exception as e:  # model / quota / network
        print(f"Live run error: {e}")


if __name__ == "__main__":
    main()
