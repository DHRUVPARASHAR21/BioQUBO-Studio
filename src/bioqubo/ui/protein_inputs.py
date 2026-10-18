"""Streamlit page for offline FASTA and PDB/mmCIF input inspection."""

from __future__ import annotations

import streamlit as st

from bioqubo.exports import build_result_exports
from bioqubo.io.fasta import parse_fasta_text
from bioqubo.io.structure import parse_structure_text
from bioqubo.models import ResultEnvelope, ResultStatus
from bioqubo.offline_demo import software_version
from bioqubo.residue_network import build_residue_network
from bioqubo.residue_selection_bqm import build_residue_selection_bqm, solve_residue_selection


def render_protein_inputs_page() -> None:
    """Render local-only protein file upload and validation summaries."""

    st.header("Protein inputs")
    st.info("Files are parsed locally in this session. No upload to a remote service is performed.")
    fasta_upload, structure_upload = st.columns(2)
    with fasta_upload:
        st.subheader("FASTA sequence")
        fasta_file = st.file_uploader("Choose FASTA", type=["fasta", "fa", "faa", "fas"])
        if fasta_file is not None:
            try:
                records = parse_fasta_text(fasta_file.getvalue().decode("utf-8"), fasta_file.name)
            except (UnicodeDecodeError, ValueError) as error:
                st.error(str(error))
            else:
                st.success(f"Validated {len(records)} local FASTA record(s).")
                st.dataframe(
                    [
                        {
                            "identifier": record.identifier,
                            "length": len(record.sequence),
                            "description": record.description,
                            "checksum": record.provenance.checksum,
                        }
                        for record in records
                    ],
                    hide_index=True,
                    width="stretch",
                )
    with structure_upload:
        st.subheader("PDB or mmCIF structure")
        structure_file = st.file_uploader("Choose structure", type=["pdb", "ent", "cif", "mmcif"])
        if structure_file is not None:
            try:
                parsed = parse_structure_text(
                    structure_file.getvalue().decode("utf-8"), structure_file.name
                )
            except (UnicodeDecodeError, ValueError) as error:
                st.error(str(error))
            else:
                st.success("Validated local structure file.")
                st.write(
                    {
                        "format": parsed.format,
                        "chains": parsed.chain_ids,
                        "residues_with_ca": len(parsed.residues),
                        "checksum": parsed.provenance.checksum,
                    }
                )
                cutoff = st.number_input("CA contact cutoff (Å)", 2.0, 20.0, 8.0, 0.5)
                network = build_residue_network(parsed, float(cutoff))
                st.caption(f"Local residue network: {len(network.edges)} non-sequential contacts.")
                count = st.number_input(
                    "Residues to select", 1, len(network.residues), min(3, len(network.residues))
                )
                selection_controls = st.columns(3)
                solver = selection_controls[0].selectbox(
                    "Local solver", ["neal", "tabu"], key="residue_selection_solver"
                )
                reads = selection_controls[1].number_input(
                    "Selection reads", 1, 500, 100, 10, key="residue_selection_reads"
                )
                seed = selection_controls[2].number_input(
                    "Selection random seed", 0, value=123, step=1, key="residue_selection_seed"
                )
                if st.button("Select connected residues locally"):
                    encoding = build_residue_selection_bqm(network, int(count))
                    result = solve_residue_selection(
                        encoding, solver=solver, reads=int(reads), seed=int(seed)
                    )
                    if result is None:
                        st.error("No valid fixed-size residue selection was returned.")
                    else:
                        st.success("Selected residues after independent cardinality verification.")
                        st.dataframe(
                            [
                                {
                                    "chain": network.residues[index].chain_id,
                                    "residue": network.residues[index].residue_name,
                                    "number": network.residues[index].residue_number,
                                    "network_degree": network.degree(index),
                                }
                                for index in result.selected_indices
                            ],
                            hide_index=True,
                            width="stretch",
                        )
                        rows = [
                            {
                                "selected_index": index,
                                "chain": network.residues[index].chain_id,
                                "residue": network.residues[index].residue_name,
                                "residue_number": network.residues[index].residue_number,
                                "insertion_code": network.residues[index].insertion_code,
                                "coordinate": network.residues[index].coordinate,
                                "network_degree": network.degree(index),
                            }
                            for index in result.selected_indices
                        ]
                        envelope = ResultEnvelope(
                            workflow="residue_network_selection",
                            status=ResultStatus.SUCCESS,
                            provenance=parsed.provenance,
                            configuration={
                                "network_access": False,
                                "contact_cutoff_angstrom": float(cutoff),
                                "selection_count": int(count),
                                "solver": solver,
                                "reads": int(reads),
                                "cardinality_strength": encoding.cardinality_strength,
                                "bqm_variables": len(encoding.bqm.variables),
                            },
                            payload={
                                "structure_id": parsed.structure_id,
                                "structure_format": parsed.format,
                                "residue_count": len(network.residues),
                                "network_edges": network.edges,
                                "selected_indices": result.selected_indices,
                                "independently_evaluated_degree_score": result.objective_score,
                                "bqm_energy": result.bqm_energy,
                                "valid_samples": result.valid_samples,
                                "invalid_samples": result.invalid_samples,
                                "limitation": (
                                    "Residue-network selection is a local contact-network "
                                    "analysis, "
                                    "not structural prediction or a biological importance claim."
                                ),
                            },
                            random_seed=int(seed),
                            software_version=software_version(),
                        )
                        exports = build_result_exports(envelope, rows)
                        json_column, csv_column = st.columns(2)
                        json_column.download_button(
                            "Download selection JSON",
                            data=exports.json_text,
                            file_name="bioqubo_residue_selection.json",
                            mime="application/json",
                        )
                        csv_column.download_button(
                            "Download selected residues CSV",
                            data=exports.csv_text,
                            file_name="bioqubo_residue_selection.csv",
                            mime="text/csv",
                        )
