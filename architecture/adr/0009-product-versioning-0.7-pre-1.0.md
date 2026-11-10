---
type: Architecture Decision Record
title: "ADR 0009: Product Versioning Is 0.7.0 Pre-1.0"
description: "Renumbers the current product line to 0.7.0 across all five repositories and reserves 1.0.0 for the stability milestone."
tags:
  - "architecture"
  - "release"
  - "versioning"
status: accepted
generated:
  by: opencode/deepseek-v4.1-flash
---

# ADR 0009: Product Versioning Is 0.7.0 Pre-1.0

## Context

The current feature set was published as `v1.0.0` for `weave`, `weave-ai`,
`weave-codec-lz4` and `weave-image`. In practice it is still evolving: contract fields and behavior
are additive, ranking budgets are not closed, watch event delivery is pending, and the API surface
has not met a 1.0 stability bar. Calling it 1.0.0 makes the compatibility promise stronger than the
project can keep.

## Decision

- The current product line is **0.7.0** for `weave`, `weave-ai`, `weave-codec-lz4`,
  `weave-image` and `weave-skills`.
- The published `v1.0.0` releases and tags are removed and replaced by `v0.7.0` tags at the same
  `main` heads.
- `weave.contract/v1` and `weave.cli/v1` remain authoritative. They may evolve in place until
  1.0.0; after 1.0.0, breaking changes require a new contract/CLI major.
- 1.0.0 is reserved for the stability milestone: frozen contracts, closed release gates and
  documented compatibility guarantees.
- Version floors follow the product line: `weave-image` requires `weave >= 0.7.0` and
  `weave-ai >= 0.7.0`, and `weave-ai` vision/embeddings require `weave >= 0.7.0`.

## Consequences

- New behavior may ship in 0.x releases with additive changes; only 1.0.0 freezes the contract.
- Documentation, installers, manifests and tests use 0.7.0 and must not describe 0.7 as GA.
- Users of the removed `v1.0.0` artifacts must install `v0.7.0` explicitly.
- The next stability review decides when the 1.0.0 gate opens.

## Related Documents

- [Roadmap](../../ROADMAP.md)
- [Release checklist](../../release-checklist.md)
- [Contract layer](../layers/contract.md)
- [ADR 0002](0002-config-paths-and-db-location.md)
