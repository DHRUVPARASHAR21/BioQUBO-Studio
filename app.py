"""Streamlit entry point for the local BioQUBO Studio workflows."""

from __future__ import annotations

import streamlit as st

from bioqubo.offline_demo import run_offline_check
from bioqubo.ui.folding import render_folding_page
from bioqubo.ui.inverse_design import render_inverse_design_page
from bioqubo.ui.molecule_prioritization import render_molecule_prioritization_page
from bioqubo.ui.protein_inputs import render_protein_inputs_page
from bioqubo.ui.result_history import render_result_history_page

st.set_page_config(page_title="BioQUBO Studio", page_icon="🧬", layout="wide")

st.title("BioQUBO Studio")
st.caption("Local-first computational-biology optimization — Milestone 3 input layer")

st.info("No cloud QPU, credentials, or network connection is needed for the available workflows.")

left, right = st.columns(2)
with left:
    st.subheader("Local by default")
    st.write("No cloud QPU, API key, or network connection is needed for the offline check.")
with right:
    st.subheader("Scientific scope")
    st.write(
        "Future workflows are prioritization and coarse-grained research tools. "
        "They will not provide docking, affinity, efficacy, or clinical claims."
    )

inputs_tab, folding_tab, design_tab, molecule_tab, history_tab, foundation_tab = st.tabs(
    [
        "Protein inputs",
        "HP lattice folding",
        "Inverse HP design",
        "Molecule prioritization",
        "Result history",
        "Foundation check",
    ]
)
with inputs_tab:
    render_protein_inputs_page()
with folding_tab:
    render_folding_page()
with design_tab:
    render_inverse_design_page()
with molecule_tab:
    render_molecule_prioritization_page()
with history_tab:
    render_result_history_page()
with foundation_tab:
    st.subheader("Offline foundation check")
    st.write("Load the bundled example and create a reproducible result envelope.")
    if st.button("Run offline check", type="primary"):
        result = run_offline_check()
        st.success("Offline check completed without network access.")
        st.json(result.to_dict())
