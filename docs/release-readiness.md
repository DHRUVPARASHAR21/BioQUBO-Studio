# BioQUBO Studio — Local Release Readiness

## Intended release

BioQUBO Studio is a local-first Streamlit application for coarse-grained HP
lattice experiments, local protein-file inspection, residue-network selection,
and molecular-library prioritization. It requires no cloud QPU, account, or
network connection during normal workflows.

## Automated evidence

- `python -m pytest`: parser, evaluator, BQM, solver, and integrated app-load
  smoke tests.
- `ruff check .`: source-quality gate.
- `python -m bioqubo.offline_demo`: provenance/result-envelope smoke test.
- Headless Streamlit load: all five workflow tabs render without an exception.

## Critical local journeys

| Journey | Expected outcome | Automated evidence |
| --- | --- | --- |
| HP folding | Validated local fold and independently recomputed H-H energy | Folding tests and app smoke test |
| Inverse HP design | Fixed-composition designs with separate re-folding evidence | Inverse-design tests |
| Protein input | Local FASTA/PDB/mmCIF parsing with checksum provenance | Input-parser tests |
| Residue selection | Fixed-size, independently scored local contact-network selection | Residue-selection tests |
| Molecule prioritization | Valid local SMILES, filtered fixed-size diverse shortlist | Chemistry and shortlist tests |

## Known limitations

- Results are research/teaching aids: HP folds are not atomistic predictions;
  molecule shortlists are not docking, affinity, efficacy, or clinical results.
- Default workflows are local. Optional remote retrieval is intentionally not
  included in this release.
- Manual accessibility, responsive-browser, and packaged-install checks remain
  required before distributing a public binary release.

## Rollback

The application stores no remote state. Roll back by restoring the prior Git
commit and reinstalling that revision's local package dependencies.
