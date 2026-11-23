---
type: Architecture Decision Record
title: "ADR 0017: Generic Source Diff Operation"
description: "Adds a diff operation to the weave.source/v1 provider contract so snapshot comparison is implemented by source providers and exposed as weave source diff."
tags:
  - "architecture"
  - "extensions"
  - "source"
  - "git"
status: accepted
---

# ADR 0017: Generic Source Diff Operation

## Context

Commit-pinned snapshots ([Weave Git §5](../../specs/weave-git.md)) give every ingest a stable commit,
but there is no way to ask what changed between two snapshots. The owner decided that snapshot diff
belongs to the source extension, not core: git history, rename detection and patch generation are
provider knowledge, and [ADR 0012](0012-extension-owned-documents-and-opaque-options.md) already
places source materialization behind `weave.source/v1`. Core must not learn git to compare commits.

The provider already owns the snapshot cache and knows how to resolve refs to commits. A diff that
runs in the provider can reuse that cache and serve providers other than git later.

## Decision

1. **New operation on `weave.source/v1`.** `source_diff_request` and `source_diff_response` join
   `source_request`/`source_response`. The protocol version does not change because the operations are
   distinguished by `type`.
2. **The request names two refs.** `from` and `to` are opaque provider-resolved identifiers: a commit
   SHA, a tag or branch, or a snapshot identifier the provider returned earlier. Core does not
   interpret them. `source_id`, `uri`, `cache_dir` and `options.permissive` keep their meaning from
   §5.1; `options.format` is `changes` or `patch`, and `options.context` bounds unified hunks.
3. **The response is structured.** `changes[]` entries carry `kind` (`added`, `removed`, `modified`,
   `renamed`), bundle-relative POSIX `path`, `previous_path` for renames, `binary` when content is not
   text, and an optional unified `patch`. `from` and `to` echo the resolved commits. `truncated` is
   set when limits cut the result.
4. **Patch is opt-in.** The default format returns paths, kinds and metadata; `--format patch` (or
   `options.format: patch`) adds unified hunks. This keeps large diffs bounded and avoids sending
   protected content when the caller only needs the file list.
5. **Capability declaration.** A provider advertises `"diff"` in its manifest `capabilities`. Core
   refuses a diff request to a provider without it with `SOURCE_UNSUPPORTED`, exit `2`, before any
   process starts. Existing providers remain valid and simply do not support diff.
6. **CLI surface.** `weave source diff <bundle> --from <ref> --to <ref> [--source <id>]
   [--format json|patch] [--path <glob>] [--json]`. A bundle with one source needs no `--source`; a
   bundle with several requires it. Output is deterministic: changes sort by path, then kind, and
   patches sort with their change.
7. **Read-only and bounded.** The operation never writes the bundle, the index or the provider cache
   beyond entries a normal materialization could create. Core bounds response size, hunk count and
   path length, and refuses paths that escape the snapshot root.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Git-only CLI inside `weave-git` | Rejected: core could not offer diff for another provider, and the workspace CLI would not know the operation |
| Diff in core | Rejected: it reverses the source boundary and adds git knowledge to core |
| Patch text only | Rejected: non-git providers and JSON consumers need structured changes |
| Paths only | Rejected: inspecting a change needs optional content |
| A second protocol version | Rejected: `type` already distinguishes operations and old providers reject unknown types |

## Consequences

- `weave-git` implements the operation first and declares the `diff` capability.
- The source protocol, the `weave-git` spec and the conformance fixtures gain the new operation; the
  role descriptor for source providers gains its request and response validators.
- A provider that cannot resolve `from` or `to` fails with a provider-specific error; core reports
  `SOURCE_DIFF_FAILED` and leaves the bundle untouched.
- Snapshot retention becomes user-visible: diffing two old snapshots requires the provider cache to
  still hold them.
