# BioQUBO Studio

BioQUBO Studio is a free, local-first computational-biology optimization workbench built with D-Wave's Ocean SDK and local solvers.

> **Status: Milestone 3 input layer in progress.** This version adds local FASTA and PDB/mmCIF input validation alongside the 2D HP-model folding and inverse-design experiments. It does not provide atomistic protein-structure prediction, real-protein design, molecular prioritization, docking, affinity prediction, efficacy prediction, or clinical decision support.

## Local protein inputs

The **Protein inputs** page accepts local UTF-8 FASTA, PDB, and mmCIF files. It validates sequences, retains first-model standard residues with alpha-carbon coordinates, and records a SHA-256 checksum in local provenance. It does not send file contents over the network.

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

The offline demo reads only the bundled JSON example and creates a versioned result envelope. The Streamlit HP page uses local `neal` or `tabu` sampling and independently validates every displayed self-avoiding fold. The HP model is a coarse-grained lattice experiment, not a real-world structure prediction.

## HP lattice folding

The folding page accepts `H`/`P` sequences (or a one-record FASTA-like input), creates a finite 2D square-lattice BQM, and runs a local Ocean solver. The representation follows the distributed lattice-site approach of Irbäck et al., *Folding lattice proteins with quantum annealing*, Phys. Rev. Research 4, 043013 (2022), [DOI: 10.1103/PhysRevResearch.4.043013](https://doi.org/10.1103/PhysRevResearch.4.043013). Independent geometry checks reject invalid sampler outputs; the displayed energy is always recomputed as `-N_HH` from non-bonded nearest-neighbour H–H contacts.

## Inverse HP design

The inverse-design page accepts a valid target lattice chain, holds the H/P composition fixed, optimizes target H-H contacts with `neal` or `tabu`, then re-folds each candidate before reporting exact target-shape recovery. JSON and CSV exports retain the local configuration, seed, provenance, and software version. This follows the two-stage sequence-search/re-folding strategy in Irbäck et al., *Using quantum annealing to design lattice proteins*, Phys. Rev. Research 6, 013162 (2024), [DOI: 10.1103/PhysRevResearch.6.013162](https://doi.org/10.1103/PhysRevResearch.6.013162).

## Project documentation

- [`docs/intent.md`](docs/intent.md): why the product exists and its boundaries.
- [`docs/spec.md`](docs/spec.md): user-facing requirements and acceptance criteria.
- [`docs/plan.md`](docs/plan.md): milestone plan and verification strategy.

## License

Application source is [MIT licensed](LICENSE). Any bundled third-party data will be separately attributed and licensed.
