# BioQUBO Studio

BioQUBO Studio is a free, local-first computational-biology optimization workbench built with D-Wave's Ocean SDK and local solvers.

> **Status: Milestone 1 HP lattice folding.** This version adds a local 2D HP-model folding experiment. It does not provide atomistic protein-structure prediction, structure analysis, molecular prioritization, docking, affinity prediction, efficacy prediction, or clinical decision support.

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

## Project documentation

- [`docs/intent.md`](docs/intent.md): why the product exists and its boundaries.
- [`docs/spec.md`](docs/spec.md): user-facing requirements and acceptance criteria.
- [`docs/plan.md`](docs/plan.md): milestone plan and verification strategy.

## License

Application source is [MIT licensed](LICENSE). Any bundled third-party data will be separately attributed and licensed.
