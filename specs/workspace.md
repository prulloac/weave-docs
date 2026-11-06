---
type: specification
title: "Workspace and Source Registry Specification"
description: "Durable, named set of bundle sources with one index database, managed through a manifest and the CLI, and served read-only by the MCP server with runtime re-reconciliation."
tags:
  - "specification"
  - "workspace"
  - "sources"
  - "registry"
  - "mcp"
  - "cli"
  - "post-ga"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-06T00:00:00Z"
status: stable
---

# Specification: Workspace and Source Registry

## 1. Overview

A workspace groups a named set of OKF bundle sources under one index database and gives Weave a
durable, multi-source unit of service. The MCP server serves a workspace read-only and re-reconciles
it at runtime, so bundles can be added or removed without restarting the server.

```text
weave.workspace.yaml          manifest: sources + index
        │
        ├── weave source …    mutate the registry (CLI only)
        ├── weave sync …      reconcile the index
        └── weave mcp …       serve the workspace read-only
```

See [ADR 0007](../architecture/adr/0007-workspace-and-source-registry.md) for the decisions this
contract realizes.

## 2. Goals and Non-Goals

### Goals

- Persist a named set of sources with stable aliases and one index database.
- Add and remove sources through the CLI or manifest edits.
- Let `weave mcp` serve a workspace and re-reconcile sources without a restart.
- Keep MCP read-only and free of arbitrary filesystem access.
- Share one index across the CLI, MCP and future clients with a single writer.

### Non-Goals

- Remote, network or git sources.
- Cross-source graph traversal or link resolution (unchanged from [multi-bundle](multi-bundle.md)).
- A background daemon or mount.
- Source deduplication or merging files.
- Changing the search, privacy, extension or storage contracts.

## 3. Terminology

| Term | Meaning |
| --- | --- |
| Workspace | A manifest plus the index it names; the unit a transport serves |
| Manifest | `weave.workspace.yaml`; the declarative source of truth for sources and index |
| Source | One OKF bundle root registered under an alias |
| Registry | The persisted per-workspace record of sources and their status |
| Active | A source that is indexed and currently served |

## 4. Workspace manifest

### 4.1 Location and discovery

`weave.workspace.yaml` lives at the workspace root. `--workspace` accepts a directory or the file
path. When `--workspace` is omitted, Weave searches the current directory and its ancestors for
`weave.workspace.yaml`; if none is found, commands that require a workspace fail with
`WORKSPACE_NOT_FOUND`.

### 4.2 Schema

```yaml
version: 1
index: ~/.weave/workspaces/project.db   # optional; default <workspace>/.weave/index.db
sources:
  docs: ../weave-docs
  notes: ~/notes
```

Rules:

- `version` is required and must be `1`; unknown versions are `WORKSPACE_INVALID`.
- `index` is optional and defaults to `<manifest-dir>/.weave/index.db`, expanded with the
  [config path rules](configuration.md).
- `sources` is a mapping of alias to path. Relative paths resolve against the manifest directory;
  `~` expands; each root normalizes to an absolute path.
- Aliases match `[a-z0-9][a-z0-9-]*`; `contract`, `weave` and `workspace` are reserved.
- Duplicate aliases, or the same absolute path under two aliases, are `WORKSPACE_INVALID`.

### 4.3 Relationship to global configuration

The manifest is per-workspace and versionable. It is distinct from the global `weave config`
([Configuration](configuration.md)), which holds platform paths and machine-level settings. The
manifest may reference paths or variables but never secrets.

## 5. CLI surface

```sh
weave workspace init [<dir>]
weave workspace show [--workspace <dir>] [--json]
weave workspace path [--workspace <dir>]
weave source add <alias> <path> [--workspace <dir>]
weave source remove <alias> [--workspace <dir>] [--prune]
weave source list [--workspace <dir>] [--json]
weave source show <alias> [--workspace <dir>] [--json]
weave ingest|rebuild|sync --workspace <dir> [flags]
```

Rules:

- `workspace init` writes a minimal manifest and does not overwrite an existing one.
- `source add` and `source remove` rewrite the manifest and then reconcile the registry; `--prune`
  also deletes the removed source's rows from the index.
- `source list` and `source show` print the persisted registry, including status.
- `--workspace` is mutually exclusive with `--bundle`; `--bundle`/`--source` remain as an ephemeral,
  manifest-less single-source workspace.
- `ingest`, `rebuild` and `sync` accept `--workspace` and operate on every active source with the
  multi-bundle report shape.

## 6. Source registry and storage

The index database persists a registry in a `sources` table (schema v8):

| Column | Meaning |
| --- | --- |
| `alias` | Stable source alias (primary key) |
| `path` | Absolute, normalized bundle root |
| `status` | `active`, `indexing`, `degraded` or `removed` |
| `generation` | Incremented on each manifest change |
| `last_synced` | Unix time of the last successful sync |
| `content_hash` | Hash of the manifest sources section |

Documents, edges, embeddings and other rows remain keyed by `bundle_root` (absolute path). The
registry maps `alias` to `bundle_root`; it does not duplicate document data.

Migration from v7:

1. Create `sources`.
2. Backfill from `bundles.bundle_root` using the sanitized directory base name as the alias, with
   `-2`, `-3` suffixes on collisions, and status `active`.
3. Existing documents are untouched.

## 7. Source lifecycle

| Status | Entered | Served by MCP |
| --- | --- | --- |
| `indexing` | Manifest adds a source not yet in the index | no |
| `active` | First sync completes without fatal errors | yes |
| `degraded` | A later sync/watch fails after a successful index | yes, last snapshot with a warning |
| `removed` | `source remove` or manifest removes it | no; data retained unless `--prune` |

Only `active` and `degraded` sources appear in `source list` as served, in MCP tool `source`
arguments, and in `weave://source/<alias>/...` resources.

## 8. MCP mode

```sh
weave mcp --workspace <dir|file> [--db <file>] [--watch] [--stdio|--listen <addr>] [--token <t>] [--allow-sensitive]
```

- `--workspace` is the primary mode. `--db` overrides the manifest `index`; otherwise the manifest
  index is used.
- The server is read-only; it never writes the registry.
- Tools are unchanged, plus one read-only tool:

| Tool | Input | Result |
| --- | --- | --- |
| `weave_sources` | — | Registry entries with `alias`, `path`, `status` |

- Resources add `weave://workspace/sources` (registry JSON) and keep the
  `weave://source/<alias>/...` templates, resolved from persisted aliases.

### 8.1 Re-reconciliation

With `--watch`, the server watches the manifest and every active source root. On a manifest change
it reconciles without restarting:

1. validate the new manifest;
2. diff against the persisted registry;
3. index added sources, then mark them `active`;
4. mark removed sources `removed` and drop them from resources (retain data unless pruned);
5. swap the served source set atomically.

A reconcile failure keeps the previous healthy set and logs to stderr. A source whose watch sync
fails becomes `degraded`; its last snapshot stays served.

### 8.2 Single writer

One process may write the index at a time, enforced by an advisory lock next to the database plus
SQLite WAL. `weave mcp --watch` acquires the writer role when free; otherwise it opens read-only and
observes snapshots. Contention is reported as `INDEX_LOCKED`, not as a silent fallback.

## 9. Validation and errors

| Condition | Code | Behavior |
| --- | --- | --- |
| No manifest found | `WORKSPACE_NOT_FOUND` | Exit `2` |
| Manifest malformed or unknown version | `WORKSPACE_INVALID` | Exit `2` |
| Duplicate alias or path | `WORKSPACE_INVALID` | Exit `2` |
| Reserved or malformed alias | `INVALID_REQUEST` | Exit `2` |
| `--workspace` with `--bundle` | `INVALID_REQUEST` | Exit `2` |
| `source remove` unknown alias | `SOURCE_NOT_FOUND` | Exit `1` |
| Writer lock unavailable | `INDEX_LOCKED` | Exit `1`, names the holder |
| Source not yet indexed | `SOURCE_INDEXING` | Warning; not served |
| Source sync failed | `SOURCE_DEGRADED` | Warning; last snapshot served |
| Sync of an unindexed source | `BUNDLE_NOT_INDEXED` | Exit `1`, alias named |

## 10. Testing

- Manifest parse, discovery, path resolution and validation.
- `workspace init/show/path` and `source add/remove/list/show` round trips.
- Schema v7 to v8 migration and alias backfill with collisions.
- MCP `--workspace` serving a multi-source index with `weave_sources` and registry resources.
- Re-reconciliation: add, remove, alias change, and failed reconcile keeping the healthy set.
- Lifecycle transitions and degraded-source snapshots.
- Single-writer lock: second writer refused, readers unaffected.
- Ephemeral `--bundle`/`--source` parity with existing goldens.
- Race suite and calibration unchanged.

## 11. Acceptance Criteria

- A workspace persists named sources and one index, surviving restarts.
- Sources can be added and removed at runtime without restarting `weave mcp`.
- MCP is read-only and never accepts a client-provided path.
- Exactly one writer holds an index at a time; readers see consistent snapshots.
- Existing single-source and multi-source output is unchanged.
- The full verification gate stays green.

## Related Documents

- [ADR 0007: Workspace and Source Registry](../architecture/adr/0007-workspace-and-source-registry.md)
- [Multiple Bundle Sources](multi-bundle.md)
- [MCP Server](mcp-server.md)
- [Watch Mode](watch-mode.md)
- [Storage & Sync](storage-and-sync.md)
- [Configuration](configuration.md)
- [ROADMAP](../ROADMAP.md)
