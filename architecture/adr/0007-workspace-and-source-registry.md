---
type: Architecture Decision Record
title: "ADR 0007: Workspace and Source Registry"
description: "Introduces a workspace as the durable unit of sources and index, and makes the MCP server a read-only view over it so bundles can be added and removed without restarting the server."
tags:
  - "architecture"
  - "adr"
  - "workspace"
  - "sources"
  - "mcp"
  - "registry"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-06T00:00:00Z"
status: accepted
---

# ADR 0007: Workspace and Source Registry

## Status

Accepted on 2026-11-06. It builds on
[ADR 0002](0002-config-paths-and-db-location.md) and the
[Multiple Bundle Sources specification](../../specs/multi-bundle.md).

## Context

The MCP server is currently bundle-bound: `weave mcp --bundle <path>` snapshots its sources at
startup and never changes them. Adding a bundle means restarting the process (or changing the
OpenCode configuration that launches it). `--watch` keeps the index current but only watches the
primary bundle root, and additional `--source` roots are not watched at all.

This is a transport owning bundle lifecycle. It makes dynamic bundle loading impossible, duplicates
index and watch responsibility across every client process, and blocks a shared multi-source view
for the CLI, MCP and future clients.

The Multi Bundle Sources specification already models several sources in one invocation, but only as
ephemeral command arguments. The project needs a durable, named set of sources — a workspace — that
a server can serve and re-reconcile without restarting.

## Decision Summary

| ID | Decision |
| --- | --- |
| D1 | A **workspace** is the durable unit: a manifest of named sources plus an index database |
| D2 | `weave.workspace.yaml` is the declarative source of truth; the SQLite index holds a derived source registry |
| D3 | `weave mcp --workspace` becomes the primary MCP mode; the server is a read-only view |
| D4 | The source registry is mutated only by the CLI or by manifest edits; MCP never writes it |
| D5 | The server re-reconciles sources at runtime when the manifest changes, without a restart |
| D6 | Sources have a lifecycle status; only `active` sources are served |
| D7 | One writer owns an index database; MCP `--watch` takes the writer role or reads |
| D8 | `--bundle`/`--source` remain as an ephemeral, manifest-less single-source workspace |
| D9 | Source paths and aliases resolve and validate with the multi-bundle rules |
| D10 | MCP resources and tool `source` arguments derive from persisted aliases |

## D1 — A workspace is the durable unit

### Decision

Introduce a workspace as a named set of sources and one index database. It is represented by a
manifest file, `weave.workspace.yaml`, at the workspace root:

```yaml
version: 1
index: ~/.weave/workspaces/project.db
sources:
  docs: ../weave-docs
  notes: ~/notes
```

### Rationale

Bundles are inputs to indexing; a workspace groups them under stable aliases with one index. It is
the unit a transport serves, so transports stop owning the source set.

## D2 — Manifest is truth; the index holds a derived registry

### Decision

The manifest is the declarative source of truth for source identity. The SQLite index derives and
persists a source registry so runtime state — alias, absolute path, status, generation, last sync and
content hash — survives restarts and is visible to every transport.

### Rationale

Declarative files are reviewable and versionable; the persisted registry gives processes a stable,
concurrent view without re-parsing the manifest on every call.

## D3 — `weave mcp --workspace` is the primary mode

### Decision

`weave mcp --workspace <dir|file>` reads the manifest and the index, serves all active sources, and
remains read-only. `--bundle`/`--source` are retained for one-off or embedded use but are no longer
the default server shape.

### Rationale

MCP is a query transport. Once the workspace is the unit of service, bundle loading is an external
concern and dynamic loading follows from re-reconciliation rather than a special server feature.

## D4 — Registry mutation is out-of-band

### Decision

The registry changes only through `weave source add|remove|list`, `weave workspace init|show`, or a
manual manifest edit. MCP has no tool that adds or removes sources.

### Rationale

A read-only server must not accept arbitrary paths or mutate its own input. Keeping mutation in the
CLI preserves the existing security boundary and makes changes auditable.

## D5 — Runtime re-reconciliation

### Decision

The MCP server watches the manifest and each source root. When the manifest changes it reconciles:

1. validate the new manifest;
2. diff against the persisted registry;
3. index new sources before marking them active;
4. hide removed sources (data retained unless `--prune`);
5. swap the served source set atomically and update resources.

A failed reconcile keeps serving the previous healthy set.

### Rationale

This removes the restart requirement without giving the model any control over paths.

## D6 — Source lifecycle status

| Status | Meaning | Served |
| --- | --- | --- |
| `active` | Indexed and healthy | yes |
| `indexing` | First sync in progress | no |
| `degraded` | Sync/watch failed after a successful index | yes (last snapshot, with warning) |
| `removed` | Unregistered; data retained unless pruned | no |

### Rationale

Only indexed sources are served, but a transient failure must not blank a source the user still
wants. `degraded` preserves availability with a clear signal.

## D7 — One writer per index

### Decision

An index database has a single writer at a time, enforced by an advisory lock next to the database
plus SQLite WAL. `weave mcp --watch` acquires the writer role when free; otherwise it opens
read-only and observes snapshots.

### Rationale

Multiple clients reading one index are the point of a shared workspace. Concurrent writers would
corrupt or thrash the same SQLite database, so writer election is explicit.

## D8 — Ephemeral mode stays

### Decision

`--bundle <path>` with optional `--source` is treated as an implicit, manifest-less workspace for a
single process. It does not create a manifest or persist a registry.

### Rationale

Preserves today's one-shot usage and keeps goldens and existing tests valid.

## D9 — Path and alias rules

### Decision

Aliases match `[a-z0-9][a-z0-9-]*`; `contract`, `weave` and `workspace` are reserved. Relative paths
resolve against the manifest directory; `~` expands; roots normalize to absolute paths. Duplicate
aliases or the same path under two aliases are invalid.

### Rationale

Reuses the vocabulary and rules already established in the Multi Bundle Sources specification.

## D10 — Resources and `source` arguments

### Decision

MCP tool `source` arguments and `weave://source/<alias>/...` resources resolve against persisted
aliases. A `weave://workspace/sources` resource exposes the registry. Removed sources disappear from
resource listings immediately.

### Rationale

Stable aliases are required for multi-source targeting; deriving them from the registry keeps the
CLI, MCP and resources consistent.

## Consequences

- A workspace manifest and a `sources` table (schema v8) are added; existing databases migrate
  without data loss.
- `weave workspace` and `weave source` commands are added.
- `weave mcp` gains `--workspace` and runtime re-reconciliation; `--bundle`/`--source` remain.
- Watch must cover every active source, not only the primary root.
- Multiple MCP clients can share one workspace and index; writer election prevents corruption.
- The Multi Bundle Sources, MCP Server, Watch Mode and Storage & Sync specifications, the roadmap and
  the backlog change.

## Rejected Alternatives

| Alternative | Why rejected |
| --- | --- |
| Hot-reload a sources file inside MCP | Keeps source lifecycle in the transport; duplicates watch/index per client |
| MCP tools that add/remove bundles | Mutates a read-only server; grants the model filesystem control |
| Per-request bundle path argument | Arbitrary filesystem access; unstable resource identity |
| Always-on indexing daemon | Violates the CLI-first, no-daemon invariant |
| Rebuild the whole index on any source change | O(n) churn for a one-source delta |

## Related Documents

- [Workspace and Source Registry specification](../../specs/workspace.md)
- [Multiple Bundle Sources specification](../../specs/multi-bundle.md)
- [MCP Server specification](../../specs/mcp-server.md)
- [Watch Mode specification](../../specs/watch-mode.md)
- [Storage & Sync specification](../../specs/storage-and-sync.md)
- [Configuration specification](../../specs/configuration.md)
- [ADR 0002: Config Paths and Database Location](0002-config-paths-and-db-location.md)
- [ROADMAP](../../ROADMAP.md)
