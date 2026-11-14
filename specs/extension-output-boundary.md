---
type: specification
title: "Generic Extension Output Boundary"
description: "Defines generic synthetic documents, relations, artifacts, namespaces, relation kinds and opaque options for extension output so core does not encode provider or analyzer domain models."
tags:
  - "specification"
  - "extensions"
  - "contract"
  - "graph"
  - "source"
status: stable
generated:
  by: opencode/deepseek-v4.1-flash
---

# Specification: Generic Extension Output Boundary

## 1. Purpose

Extensions currently return domain models that core interprets: repository, project, package, commit,
code file, code symbol and code external. Core also hardcodes their ID prefixes, export paths and
source options.

This specification replaces those typed bridges with a generic output boundary:

```text
extension role
    -> generic documents + relations + artifacts + metadata
    -> core validation and persistence
    -> graph, search, MCP and export
```

Core owns validation, identity safety, persistence, graph mechanics and export mechanics. Extensions
own domain vocabulary.

## 2. Manifest Declarations

An extension declares its synthetic namespaces and contributed relation kinds in `--describe --json`:

```json
{
  "v": "weave.extension/v1",
  "name": "git",
  "source_providers": ["git"],
  "document_namespaces": ["_repo", "_project/", "_package/", "_commit/"],
  "artifact_namespaces": ["_sources/"],
  "relation_kinds": [
    {"name": "depends_on", "default": true},
    {"name": "parent_of", "default": true}
  ]
}
```

Rules:

- `document_namespaces` and `artifact_namespaces` are prefixes that must start with `_`.
- Namespaces are unique across active extensions; a collision is a protocol error.
- Every synthetic document ID and artifact path must start with a declared prefix.
- `relation_kinds` names match `^[a-z][a-z0-9_]{0,63}$`, are unique and cannot redefine a core kind.
- An extension may declare at most 32 relation kinds.
- `default` controls whether the kind joins default traversal for that active extension.

All fields are additive. Existing manifests without them remain valid but cannot emit descriptors
until they declare namespaces.

## 3. Generic Output Envelope

Roles may return the following additive fields:

```json
{
  "documents": [],
  "relations": [],
  "artifacts": [],
  "source_metadata": {},
  "warnings": []
}
```

- `documents` and `relations` are available to source providers and project analyzers.
- `artifacts` are available to roles that produce export output.
- `source_metadata` is available to source providers and persisted in the source registry.
- `warnings` remain user-visible diagnostics.

Unknown response fields are ignored by core.

## 4. Synthetic Document

```json
{
  "id": "_project/web",
  "path": "_project/web",
  "type": "Project",
  "content_kind": "symbol",
  "media_type": "text/markdown",
  "title": "@acme/web",
  "description": "Web application",
  "keywords": ["project", "npm", "web"],
  "body": "",
  "metadata": {
    "manifest": "web/package.json",
    "ecosystem": "npm"
  },
  "scope": "web"
}
```

| Field | Meaning |
| --- | --- |
| `id` | Required stable document ID; must be inside a declared namespace |
| `path` | Bundle-relative path; defaults to `id` |
| `type` | Required document type chosen by the extension |
| `content_kind` | `blob`, `text` or `symbol`; defaults to `symbol` |
| `media_type` | Optional media type |
| `title`, `description`, `keywords` | Normal document metadata |
| `body` | Optional body text, bounded by the role response limit |
| `metadata` | Extension-owned versioned metadata |
| `scope` | Optional bundle-relative path prefix; omitted means no containment |
| `consumes` | Optional bundle-relative file paths replaced by this synthetic document |

Rules:

- Core does not interpret `type`, `metadata` keys or namespace meanings.
- IDs are unique after all documents are assembled.
- A document may not overwrite a parsed file document.
- `scope` with `""` means the bundle root; an omitted `scope` means no automatic containment.
- `consumes` removes the named parsed file documents because the synthetic document carries their
  content, as a repository document does with the root README.
- For each document with `scope`, core adds generic `contains` edges to every file document under
  that path. The deepest scope owns nested files; the repository/root scope still contains all files.
- Synthetic documents are excluded from the raw file tree but are written to artifact-backed export
  data as described in §7.

## 5. Relations

```json
{"from": "_project/web", "to": "_package/npm/react", "kind": "depends_on"}
{"from": "_project/web", "to_path": "web/app.ts", "kind": "contains"}
```

| Field | Meaning |
| --- | --- |
| `from` | Required source document ID |
| `to` | Target document ID |
| `to_path` | Bundle-relative target path, resolved after file parsing |
| `kind` | Required registered relation kind |
| `raw` | Optional original link text for `link` relations |

Rules:

- Exactly one of `to` or `to_path` is required.
- An unknown explicit `to` ID is a protocol error.
- A missing `to_path` target is a warning and the relation is dropped, because analyzers and ignore
  rules may skip files.
- Relation kinds must be core-reserved or declared by the producing extension.
- Relations are deduplicated by `(from, to, kind)`.
- Relations never create dangling Markdown links; unresolved targets stay metadata or warnings.

## 6. Relation Registry and Defaults

Core reserves:

```text
link, related, contains
```

Core defaults are `link`, `related` and `contains`. `contains` is generic structural containment.

Extension relation kinds such as `imports`, `declares`, `references`, `calls`, `inherits`,
`implements`, `depends_on` and `parent_of` are registered by their owning extensions.

Default traversal for an invocation is:

```text
core defaults + default relation kinds of active extensions
```

Declared defaults are persisted with the bundle when its source is indexed and applied when a read
does not pass an explicit `--relation` filter. `weave graph`, `weave relate` and `weave path` accept
any core or active extension relation kind. Degree and orphan calculations continue to use every
stored edge.

## 7. Artifacts

```json
{
  "path": "_sources/repositories.json",
  "media_type": "application/json",
  "content": []
}
```

| Field | Meaning |
| --- | --- |
| `path` | Required export-relative path inside a declared artifact namespace |
| `media_type` | Optional; defaults to `application/json` |
| `content` | Required JSON value |

Rules:

- Paths are POSIX-relative, may not be absolute, contain `..` or escape the export root.
- Duplicate artifact paths across active extensions are a protocol error.
- Core serializes `content` deterministically as JSON.
- Artifact total count, path length, per-artifact size and total size are bounded.
- Artifacts replace the stored artifact set on ingest, rebuild or sync; raw export writes them.
- Artifacts are JSON documents and are omitted from encrypted export.
- Artifacts replace hardcoded export branches such as `_code/...` and `_sources/...`.

## 8. Source Provider Changes

### 8.1 Snapshot revision

`weave.source/v1` snapshots identify an opaque `revision`:

```json
{
  "path": "/cache/weave/sources/src-8f3c/worktree",
  "source_id": "src-8f3c2a1d4b5e6f7",
  "revision": "8f3c2a1d4b5e6f708192a3b4c5d6e7f8091a2b3c",
  "ref": "main",
  "uri": "https://git.example.com/team/weave.git",
  "read_only": true
}
```

- `revision` is provider-defined and stable for the snapshot.
- Git providers use a full commit SHA; other providers may use a content hash or version ID.
- Legacy `commit` is accepted as an alias and mapped to `revision` during migration.
- Core validates that `revision` is non-empty and stable, not that it looks like a git SHA.

### 8.2 Response

```json
{
  "v": "weave.source/v1",
  "type": "source_response",
  "snapshot": {},
  "source_metadata": {
    "provider": "git",
    "uri": "https://git.example.com/team/weave.git",
    "ref": "main",
    "revision": "8f3c2a1d4b5e6f708192a3b4c5d6e7f8091a2b3c",
    "host_kind": "github",
    "web_url": "https://git.example.com/team/weave"
  },
  "documents": [],
  "relations": [],
  "artifacts": [],
  "warnings": []
}
```

- `source_metadata` is persisted in `sources.metadata_json`.
- MCP exposes `provider` plus the metadata map; host, owner, name and URLs are not typed fields.
- Legacy `repository`, `projects` and `commits` fields remain readable through one adapter and are then
  removed.

### 8.3 Options

The request uses opaque provider options:

```json
{
  "options": {
    "provider_options": {
      "worktree": false,
      "submodules": false,
      "lfs": false,
      "history": true,
      "history_limit": 20,
      "depth": 1
    }
  }
}
```

- Core does not validate or interpret provider option keys.
- The provider validates its own options and returns a protocol error for invalid values.
- CLI and workspace flags remain convenience sugar that populate this map.
- Legacy typed option fields are accepted during migration and mapped to `provider_options`.

## 9. Project Analyzer Changes

`weave.cli/v1` project documents gain the generic descriptor fields:

```json
{
  "id": "src/main.go",
  "type": "Code",
  "content_kind": "blob",
  "title": "main.go",
  "metadata": {},
  "symbol_documents": []
}
```

- Analyzers choose document types and content kinds.
- Core no longer hardcodes `Code`, `CodeSymbol` or `CodeExternal`.
- `external_documents` remains a convenience field for the external-reference threshold; an analyzer
  may instead emit external documents through the generic document list.
- Relation validation uses the registry in §6.

## 10. Validation and Limits

- Descriptor counts, relation counts, artifact counts and sizes are bounded per role.
- IDs, paths and namespaces reject traversal, absolute paths and duplicate claims.
- A document cannot replace a parsed file or another extension's document.
- An unknown relation kind or namespace fails the operation with `EXTENSION_PROTOCOL`.
- A missing `to_path` target is a warning, not a protocol failure.
- No partial graph or artifact tree is committed on failure.
- Credentials and full provider option values never appear in warnings or errors unless the provider
  explicitly returns them.

### 10.1 Behavioral Preservation

The boundary change is internal. Existing extension functionality must remain observable and
equivalent throughout the migration:

| Surface | Preserved behavior |
| --- | --- |
| Git sources | Same repository, project, dependency, commit, provenance and MCP results |
| Code analysis | Same `Code`, `CodeSymbol` and `CodeExternal` documents, relations and `_code` exports |
| Enrichment | Same inferred keywords, metadata and warnings |
| Reranking and scoring | Same candidate selection, blend behavior and scores |
| Codecs | Same codec selection, compression and recovery |
| Crypto providers | Same key resolution, encryption, tokenization and audit behavior |
| AI and image | Same requests, redaction, outputs and fallbacks |
| Extension data | Same list/get/gc and export behavior |
| Multi-source and MCP | Same source scoping, resources, redaction and provenance |

Extensions may change their implementation and wire representation, including moving from legacy
fields to descriptors. They must not change user-visible outcomes.

Migration gate:

1. Generic descriptors and legacy adapters coexist.
2. Every first-party extension publishes descriptor output and passes its existing conformance suite
   plus boundary fixtures.
3. Core regression tests prove legacy and descriptor paths produce equivalent graphs, search results,
   exports, provenance and MCP responses.
4. Only then is the legacy adapter removed in a later minor release.

## 11. Compatibility and Migration

1. **Additive release:** protocol fields, manifest declarations and validation were added.
2. **Dual read:** core translated legacy `repository`/`projects`/`commits` and typed options into
   generic descriptors inside a deprecated adapter.
3. **Producer migration:** `weave-git` emits descriptors, namespaces, artifacts, `source_metadata`
   and provider options; `weave-code` emits typed project documents and artifacts.
4. **Core simplification:** `engine/operations` no longer interprets source or analyzer domain
   models; graph defaults and MCP provenance are policy/data.
5. **Legacy removal:** the adapter and typed source response fields are removed. Core requires
   descriptor-capable extensions.

Minimum supported extension line for this core:

```text
weave >= 0.11.0
weave-git >= 0.11.0
weave-code >= 0.11.0
```

Older extension releases must be upgraded before use. The protocol version remains
`weave.source/v1` and `weave.cli/v1`; the required fields are now the generic descriptors.

## 12. Acceptance Criteria

1. A new provider can contribute documents, relations, artifacts and metadata without changing
   `engine/operations`.
2. A new analyzer can contribute document types and relation kinds without changing core.
3. Core contains no source-provider or analyzer domain IDs, types or export paths.
4. Manifest namespace and relation declarations are enforced.
5. Default traversal is assembled from core defaults plus active extension defaults.
6. Provider options pass through opaquely.
7. MCP source provenance is provider plus metadata, not git-shaped fields.
8. Legacy responses produce identical graphs and exports during the migration release.
9. Full gate, race suite and calibration remain unchanged.
10. Every first-party extension preserves its observable functionality across the migration; the
    legacy adapter is removed only after all conformance and parity tests pass.

## 13. Testing

- Manifest namespace and relation registry validation.
- Duplicate IDs, namespace collisions and attempted file-document overwrite.
- Scope containment, deepest-scope ownership and root scope.
- Explicit ID and path relation targets, missing path warnings and deduplication.
- Artifact path safety, duplicate paths, size limits and deterministic serialization.
- Opaque provider options pass-through and provider-side validation.
- Legacy source response and project response adapters.
- Legacy vs descriptor parity for graph nodes, edges, search, export, provenance and MCP.
- Enrichment, rerank, scoring, codec, crypto, AI, image, code and extension-data regression suites.
- MCP provenance metadata and source registry round-trip.
- A fixture provider that adds a new document type and relation kind without core edits.

## Related Documents

- Decision:
  [ADR 0012](../architecture/adr/0012-extension-owned-documents-and-opaque-options.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [Node Graph Engine](node-graph-engine.md)
- [Workspace and Source Registry](workspace.md)
- [Weave Git Source Extension](weave-git.md)
- [Weave Code Extension](weave-code.md)
