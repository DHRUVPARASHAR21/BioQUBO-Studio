"""Streamlit page for small, local HP lattice-folding experiments."""

from __future__ import annotations

import hashlib

import streamlit as st

from bioqubo.folding_bqm import LatticeBounds, build_folding_bqm
from bioqubo.hp_model import HPSequenceError, parse_hp_sequence
from bioqubo.models import ResultEnvelope, ResultStatus
from bioqubo.offline_demo import software_version
from bioqubo.provenance import DataProvenance, SourceKind
from bioqubo.solvers import solve_folding
from bioqubo.ui.result_history import record_result
from bioqubo.visualization.fold import fold_svg


def render_folding_page() -> None:
    """Render the Milestone 1 HP folding workflow without network access."""

    st.header("HP lattice folding")
    st.warning(
        "This is a coarse-grained 2D HP-model experiment, not an atomistic protein "
        "structure prediction, clinical result, docking calculation, or affinity estimate."
    )
    st.caption(
        "Distributed lattice-site BQM based on Irbäck et al. (2022), "
        "Physical Review Research 4, 043013. All solvers run locally."
    )
    sequence_text = st.text_area(
        "HP sequence", value="HPPH", help="Use H and P only; a FASTA header is allowed."
    )
    controls = st.columns(4)
    with controls[0]:
        width = st.number_input("Lattice width", min_value=2, max_value=8, value=3, step=1)
    with controls[1]:
        height = st.number_input("Lattice height", min_value=2, max_value=8, value=3, step=1)
    with controls[2]:
        solver = st.selectbox("Local solver", options=["neal", "tabu"])
    with controls[3]:
        reads = st.number_input("Reads", min_value=1, max_value=500, value=100, step=10)
    seed = st.number_input("Random seed", min_value=0, value=123, step=1)

    if st.button("Fold locally", type="primary"):
        try:
            sequence = parse_hp_sequence(sequence_text)
            if len(sequence) > 12:
                raise ValueError("The interactive local page is limited to 12 HP residues.")
            encoding = build_folding_bqm(sequence, LatticeBounds(int(width), int(height)))
            result = solve_folding(encoding, solver=solver, reads=int(reads), seed=int(seed))
        except (HPSequenceError, ValueError) as error:
            st.error(str(error))
            return
        if result is None:
            st.error(
                "No valid self-avoiding chain was returned; increase reads or change the lattice."
            )
            return
        st.success("Found and independently validated a self-avoiding lattice chain.")
        metrics = st.columns(4)
        metrics[0].metric("HP contact energy", result.evaluation.energy)
        metrics[1].metric("H–H contacts", len(result.evaluation.contacts))
        metrics[2].metric("Valid samples", result.valid_samples)
        metrics[3].metric("Rejected samples", result.invalid_samples)
        st.html(fold_svg(sequence, result.chain, result.evaluation))
        st.write("Coordinates", result.chain.coordinates)
        st.write("Non-bonded H–H contacts", result.evaluation.contacts or "None")
        with st.expander("Optimization details"):
            st.json(
                {
                    "solver": result.solver,
                    "reads": int(reads),
                    "seed": int(seed),
                    "lattice": {"width": int(width), "height": int(height)},
                    "bqm_variables": len(encoding.bqm.variables),
                    "bqm_energy": result.bqm_energy,
                    "independent_hp_energy": result.evaluation.energy,
                }
            )
        provenance = DataProvenance(
            source_kind=SourceKind.MANUAL_ENTRY,
            source_name="Manual HP sequence",
            identifier="manual-hp-sequence",
            checksum=f"sha256:{hashlib.sha256(sequence.residues.encode()).hexdigest()}",
            notes=(
                "Coarse-grained HP lattice input entered locally; no external retrieval was used."
            ),
        )
        envelope = ResultEnvelope(
            workflow="hp_lattice_folding",
            status=ResultStatus.SUCCESS,
            provenance=provenance,
            configuration={
                "network_access": False,
                "solver": solver,
                "reads": int(reads),
                "lattice": {"width": int(width), "height": int(height)},
                "bqm_variables": len(encoding.bqm.variables),
            },
            payload={
                "hp_sequence": sequence.residues,
                "coordinates": result.chain.coordinates,
                "nonbonded_hydrophobic_contacts": result.evaluation.contacts,
                "independently_evaluated_hp_energy": result.evaluation.energy,
                "bqm_energy": result.bqm_energy,
                "valid_samples": result.valid_samples,
                "invalid_samples": result.invalid_samples,
                "limitation": "Coarse-grained 2D HP-model result; not an atomistic prediction.",
            },
            random_seed=int(seed),
            software_version=software_version(),
        )
        rows = [
            {
                "residue_index": index,
                "residue_type": residue,
                "x": coordinate[0],
                "y": coordinate[1],
                "nonbonded_hydrophobic_contacts": result.evaluation.contacts,
            }
            for index, (residue, coordinate) in enumerate(
                zip(sequence.residues, result.chain.coordinates, strict=True)
            )
        ]
        history_entry = record_result(envelope, rows, "bioqubo_hp_folding")
        json_column, csv_column = st.columns(2)
        json_column.download_button(
            "Download result JSON",
            data=history_entry.exports.json_text,
            file_name="bioqubo_hp_folding.json",
            mime="application/json",
        )
        csv_column.download_button(
            "Download coordinates CSV",
            data=history_entry.exports.csv_text,
            file_name="bioqubo_hp_folding.csv",
            mime="text/csv",
        )
