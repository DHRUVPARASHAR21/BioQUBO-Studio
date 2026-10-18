"""Local molecule-prioritization page."""

from __future__ import annotations

from importlib.resources import files
from typing import Any

import streamlit as st

from bioqubo.chemistry import filter_molecules, parse_smiles_lines
from bioqubo.io.molecules import ImportedMoleculeLibrary, parse_csv_library, parse_sdf_library
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
    source = st.selectbox(
        "Library input",
        ["Paste SMILES", "Upload CSV", "Upload SDF", "Bundled HIV-1 protease demo"],
    )
    upload = None
    text = ""
    if source == "Paste SMILES":
        text = st.text_area(
            "SMILES and optional identifier", "CCO ethanol\nc1ccccc1 benzene\nCCCC butane"
        )
    elif source == "Upload CSV":
        upload = st.file_uploader("Choose UTF-8 CSV", type=["csv"])
        st.caption(
            "A SMILES column is required; identifier, ID, name, or molecule_chembl_id is optional."
        )
    elif source == "Upload SDF":
        upload = st.file_uploader("Choose SDF", type=["sdf", "sd"])
        st.caption("The SDF title or ID property is retained as the local identifier.")
    else:
        st.info(
            "Four attributed ChEMBL records associated with HIV-1 protease PDB 1HSG as "
            "teaching context. This is not a biological activity or treatment dataset."
        )
    cols = st.columns(4)
    max_weight = cols[0].number_input(
        "Max molecular weight", 1.0, 2000.0, 1000.0 if source.endswith("demo") else 500.0
    )
    max_logp = cols[1].number_input("Max logP", -10.0, 20.0, 5.0)
    size = cols[2].number_input("Shortlist size", 1, 20, 2)
    solver = cols[3].selectbox("Local solver", ["neal", "tabu"], key="molecule_solver")
    if not st.button("Prioritize locally", type="primary"):
        return
    try:
        imported = _read_library(source, text, upload)
        eligible = filter_molecules(imported.molecules, float(max_weight), float(max_logp))
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
        imported.provenance,
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


def _read_library(
    source: str, text: str, upload: Any | None
) -> ImportedMoleculeLibrary:
    """Resolve an explicitly chosen local library source without network access."""

    if source == "Paste SMILES":
        return ImportedMoleculeLibrary(
            molecules=parse_smiles_lines(text),
            provenance=DataProvenance(
                SourceKind.MANUAL_ENTRY,
                "Manual local SMILES",
                "manual-smiles",
                notes="Local prioritization only; no network access.",
            ),
        )
    if source == "Upload CSV":
        if upload is None:
            raise ValueError("Choose a CSV file before prioritizing")
        return parse_csv_library(upload.getvalue(), upload.name)
    if source == "Upload SDF":
        if upload is None:
            raise ValueError("Choose an SDF file before prioritizing")
        return parse_sdf_library(upload.getvalue(), upload.name)
    data = (
        files("bioqubo.data")
        .joinpath("demo", "hiv1_protease_chembl_subset.csv")
        .read_bytes()
    )
    imported = parse_csv_library(data, "hiv1_protease_chembl_subset.csv")
    return ImportedMoleculeLibrary(
        molecules=imported.molecules,
        provenance=DataProvenance(
            SourceKind.BUNDLED_EXAMPLE,
            "HIV-1 protease ChEMBL teaching subset",
            "PDB:1HSG; ChEMBL subset",
            source_url="https://www.ebi.ac.uk/chembl/",
            license_name="CC BY-SA 3.0",
            checksum=imported.provenance.checksum,
            notes=(
                "Bundled local teaching input; see docs/data-attribution.md. No network access was "
                "used during prioritization."
            ),
            attributes={"pdb_accession": "1HSG", "record_count": len(imported.molecules)},
        ),
    )
