# BioQUBO Studio — Implementation Plan

Implementation begins only after approval of this plan.

## Milestone 0 — Foundation and reproducibility

- Create the Python project, dependency manifest, test configuration, and local example data.
- Define immutable provenance/result schemas and common validation interfaces.
- Verify a clean local install and offline sample execution.

Proposed modules: `src/bioqubo/provenance.py`, `src/bioqubo/models.py`, `tests/`.

## Milestone 1 — HP lattice folding

- Implement HP sequence parsing, lattice coordinates, independent energy evaluation, and self-avoiding-walk validation.
- Implement paper-inspired BQM encoding and local simulated-annealing/tabu solver adapters.
- Add exhaustive small-case ground-truth tests, benchmark fixtures, and fold/contact visualization.

Proposed modules: `hp_model.py`, `folding_bqm.py`, `fold_validation.py`, `solvers.py`, `visualization/fold.py`.

## Milestone 2 — Inverse lattice design

- Implement target-fold editor/import format and target-contact evaluation.
- Implement the H/P sequence-design BQM.
- Re-fold candidates, calculate recovery evidence, and export ranked designs.

Proposed modules: `inverse_design.py`, `target_fold.py`.

## Milestone 3 — Real protein sequence and structure workflows

- Add offline FASTA/PDB/mmCIF import and optional explicit UniProt/RCSB retrieval.
- Build residue-interaction networks from existing structures.
- Implement a documented BQM residue-selection use case and network/result visualizations.

Proposed modules: `io/fasta.py`, `io/structure.py`, `fetch/uniprot.py`, `fetch/rcsb.py`, `residue_network.py`, `residue_selection_bqm.py`.

## Milestone 4 — Molecular-library workflow

- Add SMILES/CSV/SDF import via RDKit and descriptor/fingerprint calculation.
- Implement filtering and a diversity-aware, fixed-cardinality molecular selection BQM.
- Add molecule cards, shortlist explanations, and CSV/JSON export.

Proposed modules: `io/molecules.py`, `chemistry.py`, `molecule_selection_bqm.py`, `visualization/molecules.py`.

## Milestone 5 — Product integration and release readiness

- Build Streamlit pages for the four workflows and a shared result-history/export view.
- Add user documentation, paper citations, limitations, data-source attribution, and example walkthroughs.
- Run functional, regression, offline, and usability checks.

Proposed modules: `app.py`, `ui/`, `docs/`, `tests/integration/`.

## Verification strategy

- Unit tests: parsers, energy functions, BQM constraint terms, provenance serialization.
- Property/invariant tests: valid folds do not overlap; objective/physical energy reconciliation; fixed-cardinality shortlists.
- Integration tests: bundled local FASTA, PDB, and molecule examples complete without network access.
- Manual QA: inspect visual output, error states, and exports in Streamlit.
- Benchmark report: compare local samplers at identical seeds/budgets; report objective and feasibility, not unsupported quantum advantage claims.

## Dependencies

- Python, Streamlit, NumPy, Pandas, Plotly/NetworkX.
- Ocean SDK: `dimod`, `dwave-neal`, `dwave-tabu`, optionally `dwave-hybrid`.
- Biopython and RDKit.
- Optional public-record clients using standard HTTPS; no keys required.

## Principal risks and mitigations

| Risk | Mitigation |
|---|---|
| Coarse models mistaken for real folding/docking | Persistent scoped-result labels; no atomistic/clinical claims. |
| Large BQMs run slowly on laptops | Small default instances, bounded user controls, local solver comparison, graceful limits. |
| Public records change or are unavailable | Offline import remains first-class; provenance captures origin/version/date. |
| Dataset licensing/attribution mistakes | Attribute UniProt/RCSB/ChEMBL in docs and exports; do not bundle bulk databases by default. |
| Solver gives infeasible samples | Independent validation and explicit feasibility reporting. |

## Approval decisions

1. **Approved:** working name **BioQUBO Studio**.
2. **Approved:** local Streamlit is the first delivery format.
3. **Approved:** repository will be public. **Pending:** choose a software license.
4. **Approved:** bundle a small HIV-1 protease demonstration based on RCSB PDB entry `1HSG` and an attributed ChEMBL-derived molecule subset. Keep data attribution/licensing separate from application-source licensing.
