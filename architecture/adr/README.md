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

Numbering is contiguous from `0001`. A decision that is replaced keeps its number and is marked
`superseded`; it is never deleted.
