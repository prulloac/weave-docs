---
type: Architecture Decision Record
title: "ADR 0003: Extension Protocol Ownership and weave-ai Extraction"
description: "Extracts weave-ai into its own repository, keeps the weave.cli/v1 JSON envelope as the contract, and defers a shared Go protocol module until a concrete trigger."
tags:
  - "architecture"
  - "adr"
  - "extensions"
  - "weave-ai"
  - "release"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-02T00:00:00Z"
status: accepted
---

# ADR 0003: Extension Protocol Ownership and weave-ai Extraction

## Status

Accepted on 2026-11-02. It complements [ADR 0002](0002-config-paths-and-db-location.md) and the
[Extension Subprocess IPC specification](../../specs/extension-ipc.md).

## Context

`weave-ai` is the reference AI extension. It currently lives in the `weave` repository at
[`cmd/weave-ai`](https://github.com/prulloac/weave/blob/main/cmd/weave-ai/main.go), imports no
`github.com/prulloac/weave` packages, and depends only on the standard library and
`gopkg.in/yaml.v3`. It speaks `weave.cli/v1` over stdin/stdout like any other `weave-<name>`
extension.

Four facts make its current location awkward:

- It is not part of the `weave` release archives, so users must build it from a source checkout.
- It has an independent release cadence: model names, provider endpoints and prompt behavior change
  more often than the core index format.
- The protocol types are duplicated three ways: `engine/extensions` owns the Go structs,
  `cmd/weave-ai` re-declares a subset, and the specification documents a third shape.
- Core already sends `doc_path`, `bundle_root` and `workspace`, which the specification does not
  describe. The extension ignores them.

The workspace policy prefers the published CLI/envelope contract over imports of `weave` engine
internals. Extensions are separate processes and may be written in any language, so the Go API is
not the extension boundary.

## Decision Summary

| ID | Decision |
| --- | --- |
| D1 | Extract `weave-ai` to its own repository as a behavior-neutral move |
| D2 | Extract first; do not require a shared Go protocol module |
| D3 | Keep `weave.cli/v1` JSON as the authoritative contract and add a schema plus fixtures |
| D4 | Defer a standalone Go protocol module until a concrete trigger |
| D5 | Give `weave-ai` independent tags, CI and release artifacts |
| D6 | Split BDD ownership between core behavior and extension behavior |

## D1 — Extract weave-ai

### Decision

- Move `cmd/weave-ai` to the new repository `prulloac/weave-ai`, module
  `github.com/prulloac/weave-ai`.
- Keep the binary name `weave-ai`, the `weave.cli/v1` envelopes and all current behavior unchanged.
- Core discovers and invokes it through the existing `weave-<name>` mechanism
  (`--with-enricher ai`, `--rerank ai`); no core code path changes.
- `weave` must not import `weave-ai`. `weave-ai` must not import `weave` engine or storage packages.

### Rationale

The move is a pure relocation today: zero core imports, roughly 15 KiB of source plus tests. It
keeps the core binary free of model-provider code and keeps an HTTP client surface that only an
optional extension needs out of the core dependency graph.

### Consequences

- `weave/README.md` links to the new repository instead of documenting a local build.
- The release archive for `weave` remains `weave` only; `weave-ai` gains its own archive.
- Existing users keep the same binary name, configuration and flags.

## D2 — Extraction before a shared module

### Decision

Do not create a shared Go protocol module as a prerequisite for the extraction. Keep the current
local structs during the move and replace them later only if D4 triggers.

### Rationale

- The extraction is behavior-neutral. Creating the module first turns it into a refactor of the
  exported `engine/extensions` types used by `engine/operations` and its tests.
- The module boundary depends on fields that are currently undocumented, so designing it first
  would freeze an accidental shape.
- A nested module adds tooling and release costs to a repository whose `verify.sh` assumes one
  module: extra CI steps, a second tag stream and a local `replace` during development.
- The avoided follow-up migration is small: replacing roughly 40 lines of structs with imports in
  one file.

### Consequences

If the module is adopted later, `weave-ai` takes one small migration instead of the extraction
taking a large one.

## D3 — Wire contract, schema and fixtures

### Decision

- The `weave.cli/v1` JSON envelope remains the authoritative contract.
- Add `contract/v1/schema/extension-ipc.schema.json` and deterministic request/response fixtures
  for enrichment and reranking.
- Core and `weave-ai` both test against the fixtures. Changes stay additive inside v1.
- Document the optional `doc_path`, `bundle_root` and `workspace` request fields in the
  [Extension Subprocess IPC specification](../../specs/extension-ipc.md).

### Rationale

A shared Go module would give compile-time convenience but not wire compatibility. Two builds can
use the same struct version and still emit incompatible JSON. Fixtures cover every implementation
language and expose undocumented fields.

### Consequences

The schema becomes part of the contract checks (`cmd/contract-export`, `cmd/schema-diff`). Fixture
values must be deterministic so both repositories can compare bytes or decoded objects.

## D4 — Deferred Go protocol module

### Decision

Introduce a standalone Go protocol module only when at least one trigger holds:

1. a second first-party Go extension needs the same types;
2. the core runner and `weave-ai` drift in a way fixtures did not catch;
3. third-party Go extensions need shared types.

When triggered, prefer a nested module at `github.com/prulloac/weave/protocol/v1` with its own
`protocol/vX.Y.Z` tag stream. Use a separate repository only if independence outweighs the extra
release coordination. The module contains envelopes, payloads and `ProtocolVersion` only; it must
not contain validation, behavior or engine imports.

### Rationale

A module is the right end state, but two consumers and a small payload do not justify the release
and tooling overhead yet. Defining triggers keeps the decision reversible and prevents a dormant
module from becoming a third source of truth.

### Consequences

If adopted, `verify.sh`, CI and release automation gain explicit nested-module steps, and core
must tag the submodule before releasing a `weave` version that requires it.

## D5 — Independent release

### Decision

- `weave-ai` gets its own semantic-version tags, CI, checksums and platform archives.
- The `weave` release workflow continues to build and package only `weave`.
- `weave-ai` names the `weave` versions it has been tested against in its release notes or README.

### Rationale

Provider and model updates should not wait for a core release, and a core release should not block
on a model endpoint. The compatibility surface is the protocol version, not a shared module.

### Consequences

The release checklist and documentation ownership split across two repositories. Both releases
keep the existing verification gates.

## D6 — BDD ownership

### Decision

- Core-side scenarios stay in `weave/docs/bdd/ai-plugin.md` and `cmd/weave/ai_bdd_test.go`:
  redaction, per-document consent, fallback behavior and envelope validation.
- Extension-side scenarios move with the code: provider shapes, configuration, protocol responses
  and error hygiene belong to `weave-ai`.
- Both BDD indexes link to each other with absolute GitHub URLs.

### Rationale

A behavior scenario should live with the executable test that proves it. Keeping core redaction
tests in `weave` preserves the privacy boundary; moving provider tests avoids testing an external
binary through a fake.

### Consequences

`weave/docs/bdd/README.md` and the new repository's BDD index need reciprocal links. `testing.md`
in this repository names the new owner for extension tests.

## Delivery Sequence

| Step | Repository | Outcome |
| --- | --- | --- |
| 1 | `weave-docs` | Accept this ADR and add the backlog row |
| 2 | `weave-ai` | Scaffold the repository, move code and tests, add CI and release automation |
| 3 | `weave` and `weave-ai` | Add the IPC schema and fixtures, then run conformance tests on both sides |
| 4 | `weave` | Remove `cmd/weave-ai`, update README, BDD links and test mapping; release `weave-ai` |
| 5 | Conditional | Adopt the Go protocol module when a D4 trigger holds |

## Rejected Alternatives

| Alternative | Why rejected |
| --- | --- |
| Shared module first | Refactors exported core types and adds nested-module tooling, tags and release ordering before the split is validated |
| Separate `weave-protocol` repository now | Adds a third member and cross-repo release ordering for two consumers and a small payload |
| `weave-ai` imports `weave/contract/v1` | Ties the extension to the `weave` module graph and release cadence; the wire schema is the contract |
| Keep `weave-ai` in the `weave` repository | No independent release, core builds an optional binary, and users still build from source |
| In-process extension or engine import | Breaks subprocess isolation, bounded timeouts, the privacy boundary and the polyglot reference model |

## Consequences

- Core stays free of AI provider code; `weave-ai` owns model integration and its release cadence.
- The extraction must not change behavior. If it does, it needs its own specification change.
- Contract drift is mitigated by schema and fixtures, not by a shared Go module.
- Documentation changes span `weave`, `weave-ai` and `weave-docs`, so the extraction PR links the
  spec and ADR in all three.
- A proposed ADR can be rejected without code changes; no core code moves until it is accepted.

## Related Documents

- [Extension Subprocess IPC specification](../../specs/extension-ipc.md)
- [Weave AI Extension specification](../../specs/weave-ai-plugin.md)
- [Privacy & Extensions architecture](../privacy-and-extensions.md)
- [ROADMAP](../../ROADMAP.md)
- [Backlog](../../backlog.md)
