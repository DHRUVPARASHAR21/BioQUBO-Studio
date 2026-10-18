# BioQUBO Studio

BioQUBO Studio is a free, local-first computational-biology optimization workbench built with D-Wave's Ocean SDK and local solvers.

> **Status: Milestone 0 foundation.** This version establishes reproducibility and offline verification infrastructure. It does not yet implement protein folding, structure analysis, molecular prioritization, docking, affinity prediction, efficacy prediction, or clinical decision support.

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

The offline demo reads only the bundled JSON example and creates a versioned result envelope. It makes no network request and does not perform biological optimization.

## Project documentation

- [`docs/intent.md`](docs/intent.md): why the product exists and its boundaries.
- [`docs/spec.md`](docs/spec.md): user-facing requirements and acceptance criteria.
- [`docs/plan.md`](docs/plan.md): milestone plan and verification strategy.

## License

Application source is [MIT licensed](LICENSE). Any bundled third-party data will be separately attributed and licensed.
