# BioQUBO Studio — Intent

## Problem

Students and early-stage computational-biology researchers need a free, reproducible way to explore real protein and compound data through optimization models that can run locally with D-Wave's Ocean SDK. Existing molecular-design tools either obscure the optimization formulation, require paid compute, or make claims beyond what a coarse-grained model supports.

## Target users

- Students learning quantum annealing, QUBO/BQM modelling, and computational biology.
- Researchers who want an inspectable local workflow for small-scale sequence, structure, and molecular-library prioritization experiments.

## Intended outcome

A local-first desktop web application that imports public biological data or local files, formulates selected tasks as binary quadratic optimization problems, runs free local Ocean-compatible solvers, and exports reproducible, clearly scoped results.

## Product constraints

- Must run without a D-Wave Leap account, cloud QPU access, paid datasets, or paid APIs.
- Must use D-Wave Ocean tooling for optimization (`dimod`, with local samplers such as `neal` and `tabu`).
- Must accept real inputs: FASTA protein sequences, PDB/mmCIF structures, and SMILES/CSV/SDF molecular libraries.
- Must preserve provenance for imported data and generated results.
- Must make no clinical, binding-affinity, atomistic-folding, or drug-efficacy claims.

## Non-goals for the first release

- Atomistic protein-structure prediction.
- Molecular docking, molecular dynamics, laboratory validation, or clinical decision support.
- Mandatory internet access or hosting.
- Direct QPU use; a user-supplied Leap backend may be considered after the local product is complete.

## Research basis

- Irbäck et al. (2022), *Folding lattice proteins with quantum annealing* — HP lattice folding formulation.
- Irbäck et al. (2024), *Using quantum annealing to design lattice proteins* — inverse lattice-protein design.
- Perdomo-Ortiz et al. (2012), *Finding low-energy conformations of lattice protein models by quantum annealing* — small-instance and historical benchmark context.

## Assumptions recorded for planning

- Working name: **BioQUBO Studio**.
- Initial delivery is a local Streamlit application for Windows/Python users.
- The source repository will be public.
- Application source is licensed under the MIT License. Bundled third-party data keeps its own attribution and license terms.
- Online retrieval is optional; users can instead upload previously downloaded public files.
- Public-source integrations will target UniProt (FASTA), RCSB PDB (PDB/mmCIF), and user-selected ChEMBL exports rather than bulk-downloading entire databases.
- The first bundled demonstration will use HIV-1 protease, RCSB PDB entry `1HSG`, with a small separately licensed, attributed ChEMBL-derived compound subset.

## Open questions

- Whether UI language, branding, or a university rubric imposes requirements.
