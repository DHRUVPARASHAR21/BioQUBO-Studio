"""Streamlit page for offline FASTA and PDB/mmCIF input inspection."""

from __future__ import annotations

import streamlit as st

from bioqubo.io.fasta import parse_fasta_text
from bioqubo.io.structure import parse_structure_text


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
