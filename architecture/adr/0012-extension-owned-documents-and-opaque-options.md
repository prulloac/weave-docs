---
type: Architecture Decision Record
title: "ADR 0012: Extension-Owned Synthetic Documents and Opaque Provider Options"
description: "Moves source-provider and analyzer semantics out of core operations by making synthetic documents, relations, artifacts, namespaces and provider options generic extension data."
tags:
  - "architecture"
  - "extensions"
  - "contract"
  - "graph"
  - "source"
  - "generic"
status: accepted
generated:
  by: opencode/deepseek-v4.1-flash
---

# ADR 0012: Extension-Owned Synthetic Documents and Opaque Provider Options

## Context

Core currently interprets extension-specific models in `engine/operations`:

- source providers produce `Repository`, `Project`, `ExternalPackage` and `Commit` fields;
- core hardcodes `_repo`, `_project`, `_package` and `_commit`;
- project analysis hardcodes `Code`, `CodeSymbol` and `CodeExternal`;
- raw export hardcodes `_code/...` and `_sources/...`;
- the source-provider wire options contain git fields such as `worktree`, `submodules`, `lfs` and
  `history`;
- graph default traversal contains extension relation kinds.

This works for one source provider and one code analyzer, but it means every new provider or analyzer
requires edits in core operations, contract types, graph defaults, export and MCP. The engine is
generic in its parsing, graph mechanics and search, but its extension boundary is not generic.

The source-provider contract is declared as a generic role, but behaves like a git-specific role. The
project-analysis contract is likewise shaped around `weave-code`.

## Decision

1. **Extensions return data, not domain models.** Every extension output may contain:
   - synthetic documents;
   - relations between documents or file paths;
   - artifacts to write into export output;
   - source metadata as an opaque map.

2. **Core applies and validates data; it does not know extension domain types.** Core must not know
   `Repository`, `Project`, `ExternalPackage`, `Commit`, `Code`, `CodeSymbol`, `CodeExternal`,
   `_repo`, `_project`, `_package`, `_commit`, `_code` or git option names.

3. **Extensions declare their namespaces and relation kinds in `--describe --json`:**
   - `document_namespaces` lists allowed synthetic ID prefixes;
   - `relation_kinds` lists contributed relation names and whether they join default traversal;
   - core reserves the core relation vocabulary and rejects namespace collisions.

4. **Provider options are opaque.** `weave.source/v1` passes a `provider_options` map that core does
   not interpret. CLI and workspace flags remain convenience sugar that populate the map.

5. **Default traversal is assembled as policy.** Core defaults are `link`, `related` and `contains`;
   extension-declared default relations are added per active extension. `engine/graph` no longer
   hardcodes provider or analyzer kinds.

6. **Exports are artifacts.** Extensions emit artifact paths and structured content. Core validates
   paths, sizes and collisions and writes them; it does not branch on `_code` or repository types.

7. **MCP provenance is generic.** Source provenance is `provider` plus metadata; git host, owner and
   name are metadata keys, not typed core fields.

8. **Legacy fields are adapted, then removed.** Existing `repository`, `projects`, `commits` and
   typed option fields remain readable during a migration release. After first-party extensions move
   to descriptors and the minimum supported extension version rises, the legacy path is removed.

9. **Behavior preservation is a release gate.** First-party extensions may change their wire output
   and implementation, but their user-visible behavior must remain identical: enrichment, reranking,
   scoring, codecs, crypto, AI, image analysis, code analysis, git ingestion, extension data, export
   and MCP surfaces. Generic descriptors are adopted only when their conformance tests pass; the
   legacy path is not removed before that gate.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Keep the coupled model and rename the role to `weave.git/v1` | Rejected if the role is intended to support more than git; accepted only as a deliberate git-only protocol |
| Add more typed fields for each provider or analyzer | Rejected: repeats the same coupling and requires core changes per extension |
| Load extension plugins in-process through a Go interface | Rejected: static binaries, subprocess isolation and language independence are core extension properties |
| Let extensions write the database directly | Rejected: breaks transactional validation, ownership and storage boundaries |
| Use arbitrary unvalidated document IDs and relation strings | Rejected: namespace and relation registries are required for safety and determinism |
| Keep git-specific options but hide them behind a generic wrapper | Rejected: core still owns and interprets provider semantics |

## Consequences

- `engine/operations` loses most source/analyzer-specific code and becomes a generic document
  application layer.
- `weave-git` and `weave-code` own their document types, ID namespaces, relation kinds and artifact
  paths.
- The contract gains generic descriptor types and manifest declarations.
- `RelationKind` must allow validated extension-defined names instead of a closed hardcoded enum.
- Source snapshots should expose an opaque `revision` rather than a git-specific `commit`; `commit`
  remains a deprecated alias during migration.
- Default traversal becomes active-extension policy; graph degree and orphan calculations remain
  independent of filtering.
- New conformance tests are needed for namespaces, relation registration, descriptor validation,
  artifact safety and legacy adapters.
- The migration gates on behavioral equivalence across core and every first-party extension. Existing
  extension functionality is allowed to change implementation, but not observable outcomes.
- The first-party git and code extensions must ship compatible descriptors before core removes the
  legacy path.
- The legacy path is removed in the 0.11 line: core requires descriptor-capable `weave-git` and
  `weave-code` builds.

## Related Documents

- Specification:
  [Generic Extension Output Boundary](../../specs/extension-output-boundary.md)
- [ADR 0010](0010-extension-provided-graph-relations-and-project-analysis.md)
- [ADR 0011](0011-git-repositories-as-source-providers.md)
