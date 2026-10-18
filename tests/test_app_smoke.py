"""Headless Streamlit release smoke test for the integrated local application."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_loads_all_local_workflow_tabs_without_exceptions() -> None:
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py")

    app.run(timeout=30)

    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "Protein inputs",
        "HP lattice folding",
        "Inverse HP design",
        "Molecule prioritization",
        "Foundation check",
    ]
