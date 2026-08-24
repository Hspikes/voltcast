# Project lineage

VoltCast has two related but distinct stages: a collaborative modeling study and a later open-source engineering reconstruction.

## Stage 1: collaborative modeling study

From 2026-02-01 through 2026-02-03, Hspikes, HYQ, and LMY collaborated on a smartphone battery-endurance model under a time-bounded mathematical-modeling brief. The working project combined:

- an equivalent-circuit account of state of charge, polarization, and voltage sag;
- device-level power components and time-varying usage scenarios;
- numerical simulation, sensitivity analysis, and aging comparisons;
- visualization, technical writing, citation work, and iterative review.

The original working history contains 118 commits—53 attributed to Hspikes, 39 to HYQ, and 26 to LMY. Commit subjects and changed paths substantiate participation across modeling, computation, figures, and manuscript work. Counts include merges and rapid editorial iterations and therefore must not be treated as percentages of ownership.

## Stage 2: VoltCast reconstruction

On 2026-08-24, Hspikes reconstructed the useful research core as VoltCast. This was a productization pass, not a claim that the competition tree itself was release-ready. The reconstruction:

- replaced the monolithic working tree with a dependency-free Python package and CLI;
- made the two-RC equations, constant-power constraint, cutoff conditions, and RK4 integration inspectable;
- replaced ambiguous working data with clearly labeled synthetic scenarios and demonstration parameters;
- added behavioral tests, reproducible baseline outputs, bilingual documentation, and open-source governance files;
- removed private email addresses, a team control number, operating-system metadata, redundant generated files, and other personal traces;
- stopped redistributing the official problem PDF, third-party papers, and competition template material.

The current source code and documentation were substantially rewritten during this stage. The collaborative foundation is credited to all three original contributors; the open-source implementation and release engineering are recorded as Hspikes's later work.

## Why the raw history was not imported

A mechanical history rewrite would preserve 118 timestamps while silently changing their content and context. It would also risk retaining personal metadata or copyrighted blobs. VoltCast instead uses a compact, auditable history:

1. a co-authored research-foundation record;
2. a separate open-source productization commit.

The complete pre-migration repository is held in a private offline archive with its Git object database intact. It can support provenance review without becoming part of the distributable project.

## Evidence boundary

This lineage establishes collaboration and intellectual provenance. It does not claim hardware validation, commercial deployment, or endorsement by the organization that published the original modeling brief. Numerical claims in VoltCast remain limited to the synthetic and demonstration evidence described in [Reproducibility and evidence](reproducibility.md).
