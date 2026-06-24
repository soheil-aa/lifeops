"""Integration test: app.fast_api_app must expose a FastAPI `app` object.

The import is deferred to test-function scope (via importlib) so that
pytest collection does not trigger the ADK OTel setup before other test
modules' fixtures can install their own TracerProvider.
"""
import importlib


def test_app_is_not_none():
    mod = importlib.import_module("app.fast_api_app")
    assert mod.app is not None
