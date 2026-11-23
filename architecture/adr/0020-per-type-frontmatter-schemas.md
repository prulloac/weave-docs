---
type: Architecture Decision Record
title: "ADR 0020: Per-Type Frontmatter Schemas"
description: "Lets a bundle opt in to a JSON Schema per document type under .weave/types, validated at ingest and audit while the base Weave profile still applies."
tags:
  - "architecture"
  - "bundle"
  - "schema"
  - "ingest"
status: accepted
---

# ADR 0020: Per-Type Frontmatter Schemas

## Context

The Weave profile requires `type` and `keywords` and nothing else, so every bundle uses the same
frontmatter contract even when a team has strict fields for ADRs, tickets or runbooks. Ingest accepts
typos and missing required fields, and `audit` can only check the base profile. The owner approved
per-type schemas as an opt-in bundle feature, keeping the default profile unchanged.

## Decision

1. **Opt-in by directory.** A bundle may add `.weave/types/<type>.schema.json`. Presence of the
   directory does not change anything until a document's `type` has a matching file. Bundles without
   the directory behave exactly as today.
2. **JSON Schema, local only.** Schema files use JSON Schema 2020-12 as implemented by the existing
   `jsonschema/v6` dependency. `$ref` may point inside the same file or another file under
   `.weave/types`; remote `$ref` and network access are refused with `TYPE_SCHEMA_UNSUPPORTED`.
3. **Type names are file names.** A type maps to its file directly; names are limited to
   `[a-z0-9][a-z0-9._-]*`. A schema file that does not parse, a type name that cannot map, or a
   dangling local `$ref` is `TYPE_SCHEMA_INVALID` at load, before any document is processed.
4. **The base profile still applies.** `type` and `keywords` remain required, and the document must
   still be valid OKF. A type schema refines frontmatter; it cannot remove the base requirements or
   change body handling.
5. **Strict ingest, permissive opt-out.** A document that violates its type schema fails the write
   with `TYPE_SCHEMA_INVALID`, exit `1`, naming the document and each violation. `--permissive`
   downgrades violations to warnings and indexes the document. A failing schema load is never
   downgraded.
6. **Audit agrees.** `weave audit` reports the same violations with severity `error`, so a bundle can
   be gated before ingest. The finding code is `TYPE_SCHEMA_INVALID`; `--fail-on` applies unchanged.
7. **Nothing is fetched or written.** Schemas are bundle content read at ingest and audit; Weave never
   downloads, generates or edits them. Extension-synthetic documents and analyzer content kinds are
   not validated by this mechanism.
8. **Additive contract.** The new behavior adds the error code and audit findings; existing envelopes,
   exit codes and default output are unchanged when the directory is absent.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| One `.weave/types.json` mapping | Rejected: one file per type is easier to review and diff |
| Warnings only | Rejected: the point is to catch typos before ingest |
| Audit-only validation | Rejected: invalid documents would still enter the index |
| Remote schema registry | Rejected for now: it breaks local-first and adds supply-chain risk |
| Extend the base profile for everyone | Rejected: it changes every existing bundle |

## Consequences

- `weave` gains schema discovery, validation, two error codes and an audit finding.
- Ingest fails by default in opted-in bundles; `--permissive` keeps the old forgiving behavior.
- Documentation must state that a type schema cannot relax the base profile.
- A new spec and BDD scenarios are required; `audit` and ingest share one validator so their results
  cannot drift.
