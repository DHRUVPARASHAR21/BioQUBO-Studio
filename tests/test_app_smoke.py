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
        "Result history",
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
    assert {button.label for button in app.get("download_button")} >= {
        "Download JSON",
        "Download CSV",
    }


def test_csv_molecule_upload_can_be_prioritized_locally() -> None:
    app = _app().run(timeout=30)
    library_input = next(item for item in app.selectbox if item.label == "Library input")

    library_input.set_value("Upload CSV").run(timeout=30)
    upload = next(item for item in app.file_uploader if item.label == "Choose UTF-8 CSV")
    upload.upload(
        "library.csv",
        b"identifier,smiles\nethanol,CCO\nbenzene,c1ccccc1\n",
        "text/csv",
    ).run(timeout=30)
    next(item for item in app.button if item.label == "Prioritize locally").click().run(timeout=30)

    assert not app.exception
    assert app.success


def test_sdf_molecule_upload_can_be_prioritized_locally() -> None:
    app = _app().run(timeout=30)
    library_input = next(item for item in app.selectbox if item.label == "Library input")

    library_input.set_value("Upload SDF").run(timeout=30)
    shortlist_size = next(item for item in app.number_input if item.label == "Shortlist size")
    shortlist_size.set_value(1).run(timeout=30)
    upload = next(item for item in app.file_uploader if item.label == "Choose SDF")
    data = (Path(__file__).parent / "fixtures" / "ethanol.sdf").read_bytes()
    upload.upload("ethanol.sdf", data, "chemical/x-mdl-sdfile").run(timeout=30)
    next(item for item in app.button if item.label == "Prioritize locally").click().run(timeout=30)

    assert not app.exception
    assert app.success
