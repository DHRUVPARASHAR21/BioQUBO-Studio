"""Streamlit entry point for the BioQUBO Studio foundation."""

from __future__ import annotations

import streamlit as st

from bioqubo.offline_demo import run_offline_check

st.set_page_config(page_title="BioQUBO Studio", page_icon="🧬", layout="wide")

st.title("BioQUBO Studio")
st.caption("Local-first computational-biology optimization — Milestone 0 foundation")

st.info(
    "This foundation verifies local provenance and reproducible-result handling only. "
    "Biological optimization workflows will be added in later milestones."
)

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

st.divider()
st.subheader("Offline foundation check")
st.write("Load the bundled example and create a reproducible result envelope.")

if st.button("Run offline check", type="primary"):
    result = run_offline_check()
    st.success("Offline check completed without network access.")
    st.json(result.to_dict())
