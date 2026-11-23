# Architecture Decision Records

ADRs record decisions that cannot be inferred from the current code or specifications. Accepted
ADRs are immutable; a later decision supersedes them with a new number.

| ADR | Status | Decision |
| --- | --- | --- |
| [0001](0001-keyword-fuzzy-search-and-ui-retirement.md) | accepted | Mandatory keywords, weighted fuzzy search, hybrid ranking and retirement of the browser UI |
| [0002](0002-config-paths-and-db-location.md) | accepted | Platform config/cache paths, the v1.0 database location and additive machine output |
| [0003](0003-extension-protocol-ownership-and-weave-ai-extraction.md) | accepted | Extract `weave-ai`, keep `weave.cli/v1` as the contract and defer a shared Go protocol module |
| [0004](0004-generic-blob-assets-and-content-metadata.md) | accepted | Generic blob documents with `content_kind`, `media_type`, `body_raw`/`body_compressed` and versioned `content_metadata` |
| [0005](0005-embeddings-and-cgo-free-vec0-index.md) | accepted | Durable embeddings, per-space `vec0` indexes and CGo-free semantic search |
| [0006](0006-codec-extensions-and-zstd-only-core.md) | accepted | zstd-only core, LZ4 as a codec extension and raw-byte codec extensions |
| [0007](0007-workspace-and-source-registry.md) | accepted | Workspace and source registry; MCP becomes a read-only view with runtime source re-reconciliation |
| [0008](0008-agent-skills-standalone-distribution.md) | accepted | Agent skills for CLI-only workflows live in a standalone `weave-skills` repository |
| [0009](0009-product-versioning-0.7-pre-1.0.md) | accepted | Renumber the current product line to 0.7.0 and reserve 1.0.0 for the stability milestone |
| [0010](0010-extension-provided-graph-relations-and-project-analysis.md) | accepted | Extensions contribute graph relations from a project-wide analysis pass; calls and references are opt-in traversal |
| [0011](0011-git-repositories-as-source-providers.md) | accepted | Git repositories are source-provider extensions that produce commit-pinned snapshots and repository graph nodes |
| [0012](0012-extension-owned-documents-and-opaque-options.md) | accepted | Extension output moves to generic synthetic documents, relations, artifacts, namespaces, relation registries and opaque provider options |
| [0013](0013-role-descriptor-registry.md) | accepted | One descriptor per extension role drives discovery, invocation, validation and limits; wire formats do not change |
| [0014](0014-extension-requirement-enforcement.md) | accepted | Extensions with unsatisfied version requirements are refused at selection with an explicit error; installation rules deferred |
| [0015](0015-bundle-local-extension-trust-gate.md) | accepted | Bundle-local extensions run only after a per-user, hash-pinned trust entry; untrusted ones are skipped unless selected explicitly |
| [0016](0016-opt-in-parallel-extension-invocation.md) | accepted | Invocation stays sequential unless `--extension-parallelism` raises the bound; results merge in input order |
| [0017](0017-generic-source-diff-operation.md) | accepted | `weave.source/v1` gains a diff operation; providers advertise it and return structured changes with an optional patch |
| [0018](0018-pluggable-tokenizer-role.md) | accepted | An opt-in tokenizer role supplies stems and query expansions; the index records its identity and a change requires a rebuild |
| [0019](0019-document-move-with-link-rewriting.md) | accepted | `weave mv` moves one document and rewrites the relative links and related ids that point at it |
| [0020](0020-per-type-frontmatter-schemas.md) | accepted | A bundle may opt in to JSON Schema per document type under `.weave/types`, validated at ingest and audit |

Numbering is contiguous from `0001`. A decision that is replaced keeps its number and is marked
`superseded`; it is never deleted.

An accepted ADR's decision text is immutable. Corrections use a dated `## Errata (YYYY-MM-DD)`
section; extensions that do not reverse the decision use a dated
`## Amendment (YYYY-MM-DD): <topic>` section. Neither changes the decision text. Reversing a decision
needs a new ADR.
