---
type: Architecture Decision Record
title: "ADR 0010: Extension-Provided Graph Relations and Project Analysis"
description: "Lets trusted extensions contribute graph relations from a project-wide analysis pass, and reserves calls and references as opt-in traversal."
tags:
  - "architecture"
  - "extensions"
  - "graph"
  - "code"
status: accepted
generated:
  by: opencode/deepseek-v4.1-flash
---

# ADR 0010: Extension-Provided Graph Relations and Project Analysis

## Context

The Weave graph contains Markdown links and frontmatter `related` entries. Extensions can enrich one
document at a time, but they cannot add graph edges. Code knowledge needs relationships that cross
files: imports, declarations, references, calls, inheritance and implementation. Resolving those
relationships one file at a time is not possible because a symbol reference may point into another
file.

The graph edge table already stores an arbitrary `edge_type`, so the storage layer does not need a
schema migration. The missing pieces are the extension protocol, the relation contract, traversal
policy and synthetic document types.

## Decision

1. **Add code relation kinds** to the graph edge vocabulary:
   `imports`, `declares`, `references`, `calls`, `inherits`, `implements`.
2. **Add a project analysis message pair** to `weave.cli/v1`:
   `project_analysis_request` and its response. Core invokes a project-capable extension once per
   ingest, rebuild or sync, passing the bundle root, file list and content hashes. The extension
   returns file documents, optional symbol documents, external dependency documents, relations and
   warnings.
3. **Core validates and persists relations** with the existing `edges` table. A relation is accepted
   only when both endpoints are documents after synthetic documents are materialized.
4. **Default traversal is bounded:** `link`, `related`, `imports`, `declares`, `inherits` and
   `implements`. The `calls` and `references` kinds require an explicit `--relation` filter on
   `weave path` and `weave relate`.
5. **Synthetic documents are first-class search and navigation nodes** but are not source files.
   Raw export writes `_code/symbols.json` and `_code/relations.json` and warns about excluded
   synthetic documents.
6. **External dependencies become documents only when referenced more than once** and only when the
   target is a dependency, import, call target or base type. A single reference stays in metadata.
7. **Project analysis cache lives under `WEAVE_CACHE_DIR`** and never inside the source bundle.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Extension data only, no graph edges | Rejected: `weave path` and `weave relate` could not traverse code structure |
| Separate code graph command | Rejected: duplicates graph, pathfinding and MCP surfaces |
| Per-file analysis | Rejected: cannot resolve cross-file calls, references or inheritance |
| Rescan the bundle per file | Rejected: cost grows with the square of the file count |
| Native tree-sitter with C libraries | Rejected for the first version: breaks static, C-free release builds |

## Consequences

- `weave graph`, `weave relate`, `weave path`, `weave audit`, contract schemas, MCP tool inputs and
  graph goldens must accept the new relation kinds.
- `weave audit` counts code relations for degree and orphan findings; unresolved single references
  do not become dangling links.
- Extension failure in strict mode fails the write; permissive mode warns and keeps file documents.
- Existing Markdown-only output is unchanged when no project analyzer is invoked.
- The 1.0 stability window is unaffected structurally; a confirmed code-extension defect still
  resets it under [ADR 0009](0009-product-versioning-0.7-pre-1.0.md).

## Related Documents

- [Weave Code Extension spec](../../specs/weave-code.md)
- [Extension Subprocess IPC spec](../../specs/extension-ipc.md)
- [Node Graph Engine spec](../../specs/node-graph-engine.md)
- [Generic Blob Assets spec](../../specs/blob-assets.md)
- [ADR 0004](0004-generic-blob-assets-and-content-metadata.md)
