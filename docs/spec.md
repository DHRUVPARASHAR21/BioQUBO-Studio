# BioQUBO Studio — Product Specification

## User flows

### 1. Protein sequence experiment

1. The user pastes or uploads FASTA data, or supplies a UniProt accession when online retrieval is enabled.
2. The app validates and records sequence provenance.
3. The user selects an HP coarse-graining rule and solver settings.
4. The app builds a lattice-protein BQM, solves it locally, validates returned folds, and displays energy, contacts, coordinates, and limitations.

### 2. Protein structure analysis

1. The user uploads PDB/mmCIF or enters a PDB identifier when online retrieval is enabled.
2. The app parses chains/residues and builds a residue-interaction network with user-visible distance/contact settings.
3. The user chooses a residue-selection objective and constraints.
4. The app formulates a BQM for selecting a bounded set of informative/central residues and presents the selected residues and objective breakdown.

### 3. Molecular-library prioritization

1. The user uploads SMILES, CSV, or SDF data, optionally with a user-provided activity column.
2. The app uses RDKit to validate molecules and calculate locally available descriptors/fingerprints.
3. The user specifies a shortlist size and filters such as molecular-weight and Lipinski-style bounds.
4. The app formulates a diversity-aware, constraint-aware BQM and returns a reproducible shortlist with descriptor and objective explanations.

### 4. Inverse lattice-protein design

1. The user selects or defines a valid target lattice fold.
2. The app generates H/P sequences using the inverse-design BQM.
3. The app re-folds candidates, reports target recovery, and exports candidates with evidence.

## Functional requirements

- Validate input formats and give actionable errors.
- Support offline file import for all three data types.
- Store source identifiers, URLs where applicable, retrieval timestamp, model/solver parameters, random seed, and software version in every export.
- Build BQMs with `dimod` and solve with local `neal` and `tabu` backends at minimum.
- Offer solver comparison under a shared budget.
- Render sequence/fold, residue-network, and molecular-shortlist results interactively.
- Export result bundles as JSON and CSV; export figures where practical.
- Include built-in paper-style HP benchmarks and tests independent of solver output.

## Quality and safety requirements

- Local-first: input data must not be uploaded by the application.
- Scientific boundaries must be visible near results and exports.
- Results must distinguish a BQM objective from physical binding affinity, experimental activity, or clinical usefulness.
- Deterministic controls (random seeds/configuration) must support reproduction where solvers allow it.
- Invalid BQM samples must be detected, counted, and never represented as valid folds/designs.

## Acceptance criteria

- A user can run a complete sequence, structure, and molecule workflow offline using local example files.
- The application starts without cloud credentials and all default solver paths work without a network connection.
- Fold validity rules detect overlapping, disconnected, and non-adjacent chains.
- On short built-in HP cases with exhaustive ground truth, independently evaluated energy equals the accepted BQM result energy.
- Every export contains source/provenance and solver configuration.
- Molecular shortlist obeys the requested count and all enabled filters.
- The UI shows a non-clinical/non-atomistic limitation notice for each respective workflow.

## Architecture and data outline

```text
Streamlit UI
  -> input adapters (FASTA, PDB/mmCIF, SMILES/CSV/SDF)
  -> domain models and provenance records
  -> optimization encoders (lattice fold, inverse design, residue selection, molecular shortlist)
  -> local Ocean samplers
  -> validators/evaluators
  -> visualizations and versioned result exports
```

Data stays on the local filesystem. Optional fetchers retrieve a requested public record only; they do not silently transmit user-provided data.
