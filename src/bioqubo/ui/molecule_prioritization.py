"""Local molecule-prioritization page."""

from __future__ import annotations

import streamlit as st

from bioqubo.chemistry import filter_molecules, parse_smiles_lines
from bioqubo.models import ResultEnvelope, ResultStatus
from bioqubo.molecule_selection_bqm import build_molecule_selection_bqm, solve_molecule_selection
from bioqubo.offline_demo import software_version
from bioqubo.provenance import DataProvenance, SourceKind
from bioqubo.ui.result_history import record_result


def render_molecule_prioritization_page() -> None:
    st.header("Molecular-library prioritization")
    st.warning(
        "This is local chemical prioritization only—not docking, binding-affinity prediction, "
        "efficacy assessment, or clinical advice."
    )
    text = st.text_area(
        "SMILES and optional identifier", "CCO ethanol\nc1ccccc1 benzene\nCCCC butane"
    )
    cols = st.columns(4)
    max_weight = cols[0].number_input("Max molecular weight", 1.0, 2000.0, 500.0)
    max_logp = cols[1].number_input("Max logP", -10.0, 20.0, 5.0)
    size = cols[2].number_input("Shortlist size", 1, 20, 2)
    solver = cols[3].selectbox("Local solver", ["neal", "tabu"], key="molecule_solver")
    if not st.button("Prioritize locally", type="primary"):
        return
    try:
        eligible = filter_molecules(parse_smiles_lines(text), float(max_weight), float(max_logp))
        selected = solve_molecule_selection(
            build_molecule_selection_bqm(eligible, int(size)), solver=solver
        )
        if selected is None:
            raise ValueError("No valid fixed-size shortlist was returned")
    except ValueError as error:
        st.error(str(error))
        return
    rows = [
        {
            "identifier": m.identifier,
            "smiles": m.smiles,
            "molecular_weight": m.molecular_weight,
            "logp": m.logp,
            "hbd": m.hbd,
            "hba": m.hba,
            "selected": m in selected,
        }
        for m in eligible
    ]
    st.success(
        f"Selected {len(selected)} locally prioritised molecules from {len(eligible)} "
        "eligible inputs."
    )
    st.dataframe(rows, hide_index=True, width="stretch")
    envelope = ResultEnvelope(
        "molecular_prioritization",
        ResultStatus.SUCCESS,
        DataProvenance(
            SourceKind.MANUAL_ENTRY,
            "Manual local SMILES",
            "manual-smiles",
            notes="Local prioritization only; no network access.",
        ),
        {
            "network_access": False,
            "solver": solver,
            "max_weight": max_weight,
            "max_logp": max_logp,
            "shortlist_size": int(size),
        },
        {"selected": [m.identifier for m in selected]},
        random_seed=123,
        software_version=software_version(),
    )
    history_entry = record_result(envelope, rows, "bioqubo_molecule_priority")
    a, b = st.columns(2)
    a.download_button(
        "Download JSON",
        history_entry.exports.json_text,
        "bioqubo_molecule_priority.json",
        "application/json",
    )
    b.download_button(
        "Download CSV",
        history_entry.exports.csv_text,
        "bioqubo_molecule_priority.csv",
        "text/csv",
    )
