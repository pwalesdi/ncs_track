"""Headless-browser check of the built dashboard (see scripts/checks/dashboard_browser.py)."""

import importlib.util
import sys

import pytest

from ncs_track import paths

HTML = paths.ROOT / "dashboard" / "index.html"
pytestmark = pytest.mark.skipif(importlib.util.find_spec("playwright") is None or not HTML.exists(),
                                reason="needs playwright (+ chromium) and dashboard/index.html")


def test_dashboard_in_browser():
    sys.path.insert(0, str(paths.ROOT / "scripts" / "checks"))
    import dashboard_browser
    try:
        results = dashboard_browser.run()
    except Exception as e:                      # browser binary missing etc.
        pytest.skip(f"browser unavailable: {e}")
    for width, r in results.items():
        assert r["problems"] == [], (width, r["problems"])
        assert r["blocked_network_requests"] == [], (width, r["blocked_network_requests"])
