"""Headless Streamlit release smoke test for the integrated local application."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


def _app() -> AppTest:
    return AppTest.from_file(Path(__file__).parents[1] / "app.py")


def test_app_loads_all_local_workflow_tabs_without_exceptions() -> None:
    app = _app()

    app.run(timeout=30)

    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "Protein inputs",
        "HP lattice folding",
        "Inverse HP design",
        "Molecule prioritization",
        "Foundation check",
    ]


def test_default_hp_folding_action_completes_without_exception() -> None:
    app = _app().run(timeout=30)

    app.button[0].click().run(timeout=30)

    assert not app.exception
    assert app.success


def test_default_inverse_design_action_completes_without_exception() -> None:
    app = _app().run(timeout=30)

    app.button[1].click().run(timeout=30)

    assert not app.exception
    assert app.success


def test_default_molecule_prioritization_action_completes_without_exception() -> None:
    app = _app().run(timeout=30)

    app.button[2].click().run(timeout=30)

    assert not app.exception
    assert app.success
