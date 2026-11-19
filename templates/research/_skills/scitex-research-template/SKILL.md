---
name: scitex-research-template
description: Template for research projects using the SciTeX framework — clone and customize for reproducible experiments, checkable manuscript claims and a live paper. Ships an MNIST showcase that runs literature -> data -> analysis -> statistics -> figures -> claims -> manuscript -> live paper. Use when starting a new SciTeX-based research project.
user-invocable: false
---

# scitex-research-template

Boilerplate research project for the [SciTeX](https://scitex.ai)
framework: the standard directory layout, `@scitex_session.session`
script conventions, and an MNIST showcase that exercises the ecosystem end
to end (scitex-scholar, scitex-dataset, scitex-session/io/config/repro,
scitex-ml, scitex-stats, figrecipe, scitex-notebook, scitex-clew,
scitex-writer, scitex-live-paper).

Upstream reference: [../../README.md](../../README.md) and
[../../CLAUDE.md](../../CLAUDE.md).

## Sub-skills

- [01_quick-start.md](01_quick-start.md) — Create, install, run `make all`, open the live paper
- [02_structure.md](02_structure.md) — Directory layout
- [11_writing-scripts.md](11_writing-scripts.md) — `@scitex_session.session` script conventions
- [12_showcase-flow.md](12_showcase-flow.md) — The MNIST showcase step by step, and how to add a claim
