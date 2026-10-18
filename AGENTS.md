# BioQUBO Studio Agent Guide

## Project intent

Build a free, local-first computational-biology optimization application using D-Wave Ocean SDK models and local solvers. Read `docs/intent.md`, `docs/spec.md`, and `docs/plan.md` before implementation work.

The repository is public and application source is licensed under MIT. Preserve separate attribution and licensing for bundled third-party data.

## Required boundaries

- No paid service, cloud/QPU credential, or network connection may be required for default workflows.
- Treat protein-folding results as coarse-grained HP-model experiments, not atomistic predictions.
- Treat molecular ranking as prioritization only, not docking, affinity prediction, efficacy, or clinical advice.
- Keep all user data local. Network retrieval must be explicit and optional.
- Preserve provenance, configuration, seeds, and software version in exports.

## Planned stack

- Python and Streamlit.
- `dimod`, `dwave-neal`, `dwave-tabu`; `dwave-hybrid` only when justified.
- Biopython and RDKit for public-format parsing and local chemistry operations.

## Quality expectations

- Add tests alongside every encoder, parser, and evaluator.
- Independently validate solver outputs; never rely on BQM energy alone as a biological result.
- Prefer clear, small modules and typed data models.
- Do not introduce online dependencies without documenting fallback behavior and attribution.

## Commands

Create and activate a virtual environment before working locally:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run quality checks:

```powershell
python -m pytest
ruff check .
python -m bioqubo.offline_demo
streamlit run app.py
```
