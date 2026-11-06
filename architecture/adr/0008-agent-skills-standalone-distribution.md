---
type: Architecture Decision Record
title: "ADR 0008: Agent Skills as a Standalone Distribution"
description: "Publishes user-facing agent skills for CLI-only Weave workflows from a standalone weave-skills repository that consumes the published CLI contract."
tags:
  - "architecture"
  - "adr"
  - "skills"
  - "agents"
  - "cli"
  - "distribution"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-06T00:00:00Z"
status: accepted
---

# ADR 0008: Agent Skills as a Standalone Distribution

## Status

Accepted on 2026-11-06. It complements
[ADR 0007](0007-workspace-and-source-registry.md) and the
[Workspace and Source Registry specification](../../specs/workspace.md).

## Context

Weave exposes two surfaces: a full CLI and a read-only MCP server. MCP covers query and retrieval,
but workspace creation, bundle registration, ingest, sync, export and maintenance remain CLI-only.
Agents therefore need procedural knowledge that the MCP tool list cannot provide.

The `weave` repository already has `.agents/skills/` for **contributor** skills: spec writing, BDD,
TDD, review and debugging. Those skills describe how to change Weave, not how to operate an installed
Weave. Mixing product-usage skills into that directory would confuse both audiences, and shipping
them inside the core repository leaves installation, versioning and multi-harness packaging
undefined.

Agent skills are executable instructions. They depend on CLI flags and output contracts, so they can
drift from the binary. They need independent distribution and compatibility checks, similar to the
existing extension repositories.

## Decision Summary

| ID | Decision |
| --- | --- |
| D1 | Product agent skills live in a standalone `weave-skills` repository |
| D2 | `weave/.agents/skills/` remains contributor-only |
| D3 | `weave-docs` owns the ADR/spec; it does not host skills |
| D4 | Skills consume only the published CLI and envelope contract |
| D5 | The repository is versioned independently and declares CLI compatibility |
| D6 | CI runs documented commands against a pinned Weave build |
| D7 | Start with one `weave-cli` skill and progressive-disclosure references |
| D8 | Skills route reads to MCP and lifecycle work to the CLI |
| D9 | Installers are user-level and support project or global skill directories |
| D10 | CLI changes land in `weave` before the matching skill change |

## D1 — Standalone `weave-skills` repository

### Decision

Create `weave-skills` as a workspace member. It owns the canonical product skills, installers,
compatibility metadata and conformance tests.

### Rationale

Separating "how to use Weave" from "how to build Weave" gives skills their own release cadence and
keeps the core binary and release archives focused. It also follows the existing integration
pattern: consumers depend on the published contract rather than core internals.

## D2 — Contributor skills stay in `weave`

### Decision

`weave/.agents/skills/` keeps only repository-development skills. Product skills are not added there.

### Rationale

The two audiences have different triggers and permissions. A contributor skill should load while
editing the Go repository; a product skill should load while an agent operates a user's workspace.

## D3 — `weave-docs` owns the decision, not the artifact

### Decision

The ADR and any behavioral contract live in `weave-docs`. The skills tree, installers and tests live
in `weave-skills`.

### Rationale

`weave-docs` is project documentation, not a distribution channel. Skills are executable artifacts
that need CI against a binary.

## D4 — Contract-only dependency

### Decision

Skills may reference documented CLI commands, flags, envelope fields and MCP tools. They must not
import Weave packages, read engine internals or depend on repository layout.

### Rationale

A skill that depends on internals breaks on refactors. The CLI/envelope and MCP contracts are the
stable integration boundary.

## D5 — Independent versioning and compatibility

### Decision

`weave-skills` uses its own semantic version. Each skill declares the minimum Weave version and
contract it targets:

```yaml
compatibility:
  weave: ">= 1.1.0"
  contract: "weave.contract/v1"
```

A breaking CLI change or a skill-behavior break requires a major skill version. Additive commands
and examples are minor.

### Rationale

Skills can be installed without upgrading the binary and vice versa. Compatibility must be explicit
so an old skill does not silently teach a removed flag.

## D6 — Conformance CI

### Decision

CI installs a pinned Weave build and runs the commands documented by the skill against temporary
workspaces and bundles. The check covers workspace lifecycle, source changes, ingest/sync, and the
MCP stdio handshake.

### Rationale

Documentation drift is the main risk. Executable checks turn the skill into a tested artifact.

## D7 — One skill first, references per workflow

### Decision

Ship one `weave-cli` skill with focused reference files for workspace, ingest/sync, search,
export/maintenance and troubleshooting. Split into multiple skills only when an agent must choose
between distinct triggers.

### Rationale

One entry point keeps discovery predictable. Progressive disclosure keeps the main prompt small
while preserving detail for each workflow.

## D8 — Route reads to MCP, lifecycle to CLI

### Decision

The skill explicitly tells the agent:

- use MCP tools for search, explain, relate, audit, list, show, backlinks, path and resources;
- use the CLI for workspace, source, ingest, rebuild, sync, export, embeddings and configuration.

### Rationale

This preserves the read-only MCP boundary and prevents the agent from trying to mutate a workspace
through tools that cannot.

## D9 — User-level installers

### Decision

Provide shell and PowerShell installers that copy skills into an OpenCode project or global skill
directory. They never require `sudo` or administrator rights.

### Rationale

Matches the existing Weave installer policy and works on managed machines.

## D10 — Contract owner first

### Decision

When a CLI behavior changes, update `weave` first, then `weave-skills`, then bump the skill version
and compatibility range as needed.

### Rationale

Skills must describe shipped behavior, not aspirational flags.

## Consequences

- A new workspace member, `weave-skills`, is created with its own AGENTS.md and CI.
- `weave` README/docs link to the skills repository for agent usage.
- Core release archives and the MCP server stay free of agent-specific packaging.
- A compatibility matrix becomes part of the skills release process.
- The product has one more independently versioned member to maintain.

## Rejected Alternatives

| Alternative | Why rejected |
| --- | --- |
| Put product skills in `weave/.agents/skills` | Mixes contributor and operator audiences; no install story |
| Put skills in `weave-docs` | Docs repository is not a distribution artifact and has no CLI conformance tests |
| Bundle skills in the MCP server | MCP is read-only and protocol-focused; skills cover CLI-only work |
| Generate skills from `--help` | Help text lacks workflows, safety rules and failure handling |
| One skill per CLI command | Discovery noise; agents need a workflow entry point |
| Pin skills to the Weave binary version | Forces lockstep upgrades and blocks independent fixes |

## Related Documents

- [Workspace and Source Registry specification](../../specs/workspace.md)
- [MCP Server specification](../../specs/mcp-server.md)
- [CLI reference](https://github.com/prulloac/weave/blob/main/README.md)
- [ADR 0007: Workspace and Source Registry](0007-workspace-and-source-registry.md)
- [ROADMAP](../../ROADMAP.md)
