from __future__ import annotations

from opentelemetry import trace


def get_tracer():
    return trace.get_tracer("lifeops")
