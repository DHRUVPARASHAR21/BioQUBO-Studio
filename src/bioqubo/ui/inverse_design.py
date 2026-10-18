"""Streamlit page for local inverse HP lattice-protein design."""

from __future__ import annotations

import csv
import json
from io import StringIO

import streamlit as st

from bioqubo.fold_energy import ContactEvaluation
from bioqubo.hp_model import HPSequence
from bioqubo.inverse_design import (
    build_sequence_design_bqm,
    design_sequences,
    refold_candidates,
)
from bioqubo.models import ResultEnvelope, ResultStatus
from bioqubo.offline_demo import software_version
from bioqubo.provenance import DataProvenance, SourceKind
from bioqubo.target_fold import TargetFold, parse_target_coordinates
from bioqubo.visualization.fold import fold_svg

DEFAULT_TARGET = """0, 0
1, 0
1, 1
0, 1"""


def _csv_export(rows: list[dict[str, object]]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def render_inverse_design_page() -> None:
    """Render the two-stage sequence-design and local re-folding workflow."""

    st.header("Inverse HP lattice design")
    st.warning(
        "This creates coarse-grained H/P lattice-model candidates only. It does not design "
        "real proteins or establish biological activity, stability, efficacy, or clinical value."
    )
    st.caption(
        "Two stages: optimize a fixed-composition sequence on the target contacts, then re-fold "
        "it locally. Based on Irbäck et al. (2024), Phys. Rev. Research 6, 013162."
    )
    target_text = st.text_area(
        "Target fold coordinates", value=DEFAULT_TARGET, help="One x, y pair per residue in order."
    )
    controls = st.columns(4)
    with controls[0]:
        hydrophobic_count = st.number_input("Hydrophobic residues", min_value=1, value=2, step=1)
    with controls[1]:
        solver = st.selectbox("Local solver", options=["neal", "tabu"], key="design_solver")
    with controls[2]:
        reads = st.number_input(
            "Reads", min_value=1, max_value=500, value=100, step=10, key="design_reads"
        )
    with controls[3]:
        candidate_count = st.number_input("Candidates", min_value=1, max_value=10, value=5, step=1)
    seed = st.number_input("Random seed", min_value=0, value=123, step=1, key="design_seed")

    if not st.button("Design and re-fold locally", type="primary"):
        return
    try:
        target = TargetFold(parse_target_coordinates(target_text))
        if target.length < 3 or target.length > 10:
            raise ValueError(
                "The interactive design page supports target folds of 3 to 10 residues."
            )
        if int(hydrophobic_count) >= target.length:
            raise ValueError("Hydrophobic residues must be smaller than the target-fold length.")
        encoding = build_sequence_design_bqm(target, int(hydrophobic_count))
        search = design_sequences(
            encoding,
            solver=solver,
            reads=int(reads),
            seed=int(seed),
            max_candidates=int(candidate_count),
        )
        evidence = refold_candidates(
            target, search.candidates, solver=solver, reads=int(reads), seed=int(seed)
        )
    except ValueError as error:
        st.error(str(error))
        return

    target_sequence = HPSequence("P" * target.length)
    st.html(fold_svg(target_sequence, target.chain, ContactEvaluation(target.contacts)))
    st.write("Target non-bonded contacts", target.contacts or "None")
    rows = [
        {
            "sequence": item.candidate.sequence.residues,
            "target_energy": item.candidate.target_evaluation.energy,
            "target_hh_contacts": len(item.candidate.target_evaluation.contacts),
            "refold_energy": (
                item.folding_result.evaluation.energy if item.folding_result is not None else None
            ),
            "target_shape_recovered": item.target_recovered,
        }
        for item in evidence
    ]
    st.success("Designed sequences and recorded independent local re-folding evidence.")
    st.dataframe(rows, hide_index=True, width="stretch")
    if not rows:
        st.info("No valid fixed-composition sequence was returned; increase reads and try again.")
        return
    payload = {
        "target_coordinates": target.chain.coordinates,
        "target_contacts": target.contacts,
        "candidates": rows,
        "valid_design_samples": search.valid_samples,
        "invalid_design_samples": search.invalid_samples,
    }
    result = ResultEnvelope(
        workflow="inverse_hp_lattice_design",
        status=ResultStatus.SUCCESS,
        provenance=DataProvenance(
            source_kind=SourceKind.MANUAL_ENTRY,
            source_name="Manual 2D lattice target fold",
            identifier="manual-target-fold",
            notes="Coarse-grained HP lattice design input; no external retrieval was used.",
        ),
        configuration={
            "network_access": False,
            "solver": solver,
            "reads": int(reads),
            "hydrophobic_count": int(hydrophobic_count),
            "bqm_variables": len(encoding.bqm.variables),
        },
        payload=payload,
        random_seed=int(seed),
        software_version=software_version(),
    )
    export_columns = st.columns(2)
    export_columns[0].download_button(
        "Download result JSON",
        data=json.dumps(result.to_dict(), indent=2),
        file_name="bioqubo_inverse_design.json",
        mime="application/json",
    )
    export_columns[1].download_button(
        "Download candidate CSV",
        data=_csv_export(rows),
        file_name="bioqubo_inverse_design_candidates.csv",
        mime="text/csv",
    )
