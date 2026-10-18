# Bundled data attribution

## HIV-1 protease molecular-library teaching subset

`src/bioqubo/data/demo/hiv1_protease_chembl_subset.csv` is a four-record
teaching input for the local molecular-prioritization interface. The records
retain ChEMBL identifiers and canonical SMILES retrieved from individual public
ChEMBL molecule records on 2026-10-18. It is associated with the HIV-1
protease PDB accession **1HSG** only as educational context; BioQUBO Studio
does not use the structure for scoring and makes no biological activity,
docking, affinity, efficacy, safety, or clinical claim.

No RCSB PDB coordinate data is bundled. The 1HSG accession is linked to its
[RCSB PDB structure record](https://www.rcsb.org/structure/1HSG) solely to make
the teaching context traceable.

ChEMBL is provided by EMBL-EBI. This bundled derivative dataset is made
available under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).
Please preserve this attribution and the same license for adaptations of the
dataset. The application source code remains [MIT licensed](../LICENSE).

Source and record details are retained beside the CSV in
`hiv1_protease_chembl_subset.json`.
