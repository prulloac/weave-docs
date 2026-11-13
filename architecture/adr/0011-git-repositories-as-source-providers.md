---
type: Architecture Decision Record
title: "ADR 0011: Git Repositories as Source-Provider Extensions"
description: "Adds source-provider extensions that resolve local or remote git URIs into commit-pinned snapshots, with weave-git as the first implementation and repository nodes as graph hubs."
tags:
  - "architecture"
  - "extensions"
  - "git"
  - "source"
  - "repository"
  - "graph"
status: accepted
generated:
  by: opencode/deepseek-v4.1-flash
---

# ADR 0011: Git Repositories as Source-Provider Extensions

## Context

Weave currently ingests local bundle roots. A workspace source is a filesystem path, and `weave
ingest`, `rebuild` and `sync` assume the source already exists on disk. There is no protocol role
for resolving a remote location, fetching it, pinning a revision or materializing a read-only
snapshot.

Git repositories are the main source of code knowledge, but they should not be treated as a bag of
files. A graph knowledge database needs reproducible inputs, provenance and a repository-level node.
Core is local-first and must not gain implicit network access. Project analyzers such as
`weave-code` should receive a local snapshot and should not know how it was obtained.

Existing extension roles do not fit:

- document enrichers run after documents are scanned;
- project analyzers run on already-known files;
- codecs, rerankers, scorers and embedders operate on stored content or search results.

Git ingestion must happen before asset discovery. It therefore needs a new extension role.

## Decision

1. **Add a source-provider extension role.** A provider accepts a stable `source_id`, a source URI and
   options, resolves the source to an immutable snapshot and returns the snapshot path plus
   repository metadata. The contract is `weave.source/v1`; the manifest declares the role with
   `source_providers`.
2. **Implement `weave-git` as the first source provider.** It supports local repositories and
   remote git URIs, resolves a branch, tag or commit to a commit SHA and materializes a read-only
   worktree under `WEAVE_CACHE_DIR`.
3. **Keep source identity stable across commits.** Core derives `source_id` from the workspace/source
   identity and canonical URI, excluding ref and commit. The provider materializes into a real
   `worktree` directory whose path remains the bundle root as commits and refs change.
4. **Commit-pinned by default.** The canonical input is a commit tree. A local `--worktree` mode may
   ingest uncommitted changes explicitly, but the default is reproducible committed state.
5. **Core orchestrates; extensions stay partners.** Core resolves the source, invokes the provider,
   then runs the existing Markdown and project analyzers on the snapshot. `weave-git` does not embed
   or import `weave-code`, and `weave-code` does not know about git.
6. **Create a repository node.** Each ingested repository gets one synthetic graph hub with
   `doc_type: Repository`, ID `_repo`, a Markdown body taken from the root README, and provenance
   metadata.
7. **Use generic git, not hosting APIs.** Basic ingestion uses the git protocol and local files.
   Host-specific APIs for issues, releases or merge requests are optional later enrichments.
8. **Keep history out of the first slice.** Ingest the selected commit as the current snapshot.
   Commit-history graphs and historical snapshots are deferred.
9. **Make network access explicit.** Core never clones implicitly. Remote URIs are opt-in source
   specifications handled by the trusted provider, with bounded time, size and credential rules.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Make `weave-git` an enricher | Rejected: enrichers run after discovery, too late to materialize source files |
| Build git acquisition into `weave-code` | Rejected: couples fetching with language analysis and prevents pairing with other analyzers |
| Clone directly in core | Rejected: breaks local-first defaults and adds network/credential surface to core |
| Use GitHub/GitLab APIs for basic ingestion | Rejected: not generic and unnecessary; git already exposes refs, trees and blobs |
| Ingest the mutable worktree by default | Rejected: results would not be reproducible or commit-addressable |
| Use a `current` symlink as the bundle root | Rejected: `filepath.WalkDir` does not follow a symlink root; a real worktree keeps scanning and watchers unchanged |
| Key the bundle root by commit | Rejected: every update would create a new source and leave stale graph rows |
| Store materialized snapshots inside the bundle | Rejected: writes into the source bundle and mixes cache with knowledge data |
| Graph every commit immediately | Rejected for the first slice: graph size and query value do not justify it |
| A standalone CLI that only calls `weave ingest` | Accepted as an MVP fallback, but not the long-term architecture |

## Consequences

- `weave.contract/v1` gains an additive source-provider request/response pair, a repository document
  type, source provenance metadata and a `contains` relation from repository to files. `contains`
  joins the default traversal set; `calls` and `references` remain opt-in.
- Manifest discovery adds `Project` and `ExternalPackage` documents plus `depends_on` edges, also
  traversable by default.
- The workspace manifest source value gains an object form for providers and refs while retaining
  the existing string path form.
- The source registry gains schema v9 with an explicit `provider` column and versioned
  `metadata_json` for `uri`, `ref_name`, `commit_sha` and provider-specific fields.
- Core source resolution runs the provider before asset scanning; analyzers remain unchanged.
- The source bundle root is stable across commits and refs, so updates replace the graph
  transactionally instead of creating new roots.
- `weave-git` becomes a standalone repository and release artifact, independently testable.
- Remote ingestion introduces explicit network, credential, size, submodule, LFS and symlink
  policy. Defaults are conservative.
- Existing Markdown-only and local-code behavior is unchanged when no git source is configured.
- The 1.0 stability window is unaffected structurally; a confirmed git-source defect still resets
  it under [ADR 0009](0009-product-versioning-0.7-pre-1.0.md).

## Related Documents

- [Weave Git Source Extension](../../specs/weave-git.md)
- [Extension Subprocess IPC](../../specs/extension-ipc.md)
- [Workspace and Source Registry](../../specs/workspace.md)
- [Weave Code Extension](../../specs/weave-code.md)
- [ADR 0007](0007-workspace-and-source-registry.md)
- [ADR 0010](0010-extension-provided-graph-relations-and-project-analysis.md)
