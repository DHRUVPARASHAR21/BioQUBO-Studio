# BioQUBO Studio

BioQUBO Studio is a free, local-first computational-biology optimization workbench built with D-Wave's Ocean SDK and local solvers.

> **Status: Milestone 4 core workflow complete; release readiness in progress.** This version adds local FASTA/PDB/mmCIF inspection, 2D HP-model folding, inverse design, and SMILES-based molecular-library prioritization. It does not provide atomistic protein-structure prediction, real-protein design, docking, affinity prediction, efficacy prediction, or clinical decision support.

## Local protein inputs

The **Protein inputs** page accepts local UTF-8 FASTA, PDB, and mmCIF files. It validates sequences, retains first-model standard residues with alpha-carbon coordinates, and records a SHA-256 checksum in local provenance. It does not send file contents over the network.

For a local structure, the same page can build a non-sequential alpha-carbon contact network at a user-selected cutoff and use a fixed-cardinality local BQM to select high-connectivity residues. This is an inspectable network-analysis experiment, not structural prediction or a biological importance claim. HP-folding and residue-selection result downloads include paired JSON and CSV exports; both preserve source provenance, configuration, seed, software version, and the independently evaluated result.

## Principles

- No cloud QPU, paid API, or account is required for default workflows.
- User data remains local; future online retrieval will always be explicit and optional.
- Each result records its source, configuration, random seed where applicable, and software version.
- Third-party data keeps its own license and attribution requirements.

## Setup

Python 3.11 or newer is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Install future biology file-format support only when needed:

```powershell
python -m pip install -e ".[biology]"
```

## Verify the offline foundation

```powershell
python -m pytest
python -m bioqubo.offline_demo
streamlit run app.py
```

The offline demo reads only the bundled JSON example and creates a versioned result envelope. The Streamlit HP page uses local `neal` or `tabu` sampling and independently validates every displayed self-avoiding fold. Its JSON/CSV downloads record the manual-input checksum, local solver configuration and seed, lattice settings, BQM measurements, independently evaluated energy, and coarse-grained limitation. The HP model is a coarse-grained lattice experiment, not a real-world structure prediction.

## HP lattice folding

The folding page accepts `H`/`P` sequences (or a one-record FASTA-like input), creates a finite 2D square-lattice BQM, and runs a local Ocean solver. The representation follows the distributed lattice-site approach of Irbäck et al., *Folding lattice proteins with quantum annealing*, Phys. Rev. Research 4, 043013 (2022), [DOI: 10.1103/PhysRevResearch.4.043013](https://doi.org/10.1103/PhysRevResearch.4.043013). Independent geometry checks reject invalid sampler outputs; the displayed energy is always recomputed as `-N_HH` from non-bonded nearest-neighbour H–H contacts.

## Inverse HP design

The inverse-design page accepts a valid target lattice chain, holds the H/P composition fixed, optimizes target H-H contacts with `neal` or `tabu`, then re-folds each candidate before reporting exact target-shape recovery. JSON and CSV exports retain the local configuration, seed, provenance, and software version. This follows the two-stage sequence-search/re-folding strategy in Irbäck et al., *Using quantum annealing to design lattice proteins*, Phys. Rev. Research 6, 013162 (2024), [DOI: 10.1103/PhysRevResearch.6.013162](https://doi.org/10.1103/PhysRevResearch.6.013162).

## Molecular-library prioritization

The **Molecule prioritization** page accepts a small, locally entered SMILES library with optional identifiers. It calculates local descriptors, applies molecular-weight and logP filters, and uses a fixed-size diversity-aware BQM solved by `neal` or `tabu` to select a shortlist. The page displays all eligible inputs and provides JSON/CSV result downloads with solver configuration and local provenance.

This workflow is a transparent library-prioritization experiment. It is not molecular docking, binding-affinity prediction, efficacy assessment, or clinical advice. CSV/SDF library import and an attributed bundled ChEMBL demonstration set remain planned release-completion work.

## Project documentation

- [`docs/intent.md`](docs/intent.md): why the product exists and its boundaries.
- [`docs/spec.md`](docs/spec.md): user-facing requirements and acceptance criteria.
- [`docs/plan.md`](docs/plan.md): milestone plan and verification strategy.
- [`docs/release-readiness.md`](docs/release-readiness.md): local release gates and limitations.

## License

Application source is [MIT licensed](LICENSE). Any bundled third-party data will be separately attributed and licensed.
