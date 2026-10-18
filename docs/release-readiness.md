# BioQUBO Studio — Local Release Readiness

## Intended release

BioQUBO Studio is a local-first Streamlit application for coarse-grained HP
lattice experiments, local protein-file inspection, residue-network selection,
and molecular-library prioritization. It requires no cloud QPU, account, or
network connection during normal workflows.

## Automated evidence

- `python -m pytest`: parser, evaluator, BQM, solver, import, and integrated app-load
  smoke tests.
- `ruff check .`: source-quality gate.
- `python -m bioqubo.offline_demo`: provenance/result-envelope smoke test.
- Headless Streamlit load: all five workflow tabs render without an exception.

## Critical local journeys

| Journey | Expected outcome | Automated evidence |
| --- | --- | --- |
| HP folding | Validated local fold, independently recomputed H-H energy, and reproducible JSON/CSV export | Folding and export tests; app smoke test |
| Inverse HP design | Fixed-composition designs with separate re-folding evidence | Inverse-design tests |
| Protein input | Local FASTA/PDB/mmCIF parsing with checksum provenance | Input-parser tests |
| Residue selection | Fixed-size, independently scored local contact-network selection with source-file provenance JSON/CSV export | Residue-selection and export tests |
| Molecule prioritization | Valid local SMILES/CSV/SDF, filtered fixed-size diverse shortlist, and attributed offline demo | Chemistry, import, shortlist, and export tests |

## Browser QA evidence — 2026-10-18

- **Keyboard:** the visible Skip-to-main-content link receives initial focus;
  subsequent Tab navigation reaches the application controls. The Streamlit
  accessibility tree exposes labelled workflow tabs, comboboxes, inputs, and
  upload controls.
- **Compact viewport:** at `375 × 812`, the Molecular prioritization tab and
  bundled HIV-1 protease teaching workflow complete successfully with no
  document-level horizontal overflow (`scrollWidth == innerWidth`).
- **Library input:** new integrated Streamlit tests upload a CSV and an SDF,
  run each through local prioritization, and assert a successful result.
- **Exports:** the completed workflow exposes paired JSON and CSV download
  controls in the integrated app test. Content serialization is independently
  covered by the export tests.

## Known limitations

- Results are research/teaching aids: HP folds are not atomistic predictions;
  molecule shortlists are not docking, affinity, efficacy, or clinical results.
- Default workflows are local. Optional remote retrieval is intentionally not
  included in this release.
- An assistive-technology review with a real screen reader remains required
  before distributing a public binary release. Keyboard and compact-viewport
  browser checks are recorded above. A wheel-install smoke check is part of the
  release commands below.

## Final local release commands

```powershell
python -m pytest
ruff check .
python -m bioqubo.offline_demo
python -m pip wheel . --no-deps --wheel-dir dist
```

Install the generated wheel in a fresh local virtual environment, then run
`streamlit run app.py`. Do not publish a binary release until the manual
keyboard and small-viewport checks have also been recorded.

## Export evidence

All completed workflow downloads are paired JSON and CSV artifacts, also
available again through the current session's local Result history tab. The JSON
artifact is the complete result envelope. The CSV repeats the schema version,
workflow status, timestamp, software version, random seed, and canonical JSON
provenance, configuration, and payload fields on every data row so it remains
reproducible when separated from the JSON artifact. The payload retains the
independently evaluated result and the applicable coarse-grained or
non-clinical limitation.

## Rollback

The application stores no remote state. Roll back by restoring the prior Git
commit and reinstalling that revision's local package dependencies.
