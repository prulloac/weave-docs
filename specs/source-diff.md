---
type: specification
title: "Source Snapshot Diff"
description: "A weave.source/v1 diff operation and weave source diff command that compare two provider-resolved refs and return structured changes with an optional patch."
tags:
  - "source"
  - "git"
  - "extensions"
  - "diff"
status: draft
---

# Source Snapshot Diff

## 1. Overview

`weave source diff` compares two snapshots of one source and reports added, removed, modified and
renamed documents. The comparison runs in the source provider, which already owns the cache and knows
how to resolve refs. Core validates and renders the result. The decision is
[ADR 0017](../architecture/adr/0017-generic-source-diff-operation.md).

## 2. Contract

### 2.1 Capability

A provider advertises `"diff"` in its manifest `capabilities`. A provider without it is
`SOURCE_UNSUPPORTED`, exit `2`, before any process starts. `weave-git` declares the capability in the
first implementation.

### 2.2 CLI

```sh
weave source diff <bundle> --from <ref> --to <ref> [--source <id>] [--format json|patch] [--path <glob>] [--json]
```

- `--from` and `--to` are required and are opaque provider-resolved refs: a commit, tag, branch or a
  snapshot id the provider returned earlier.
- A bundle with one registered source needs no `--source`; a bundle with several requires it.
- `--format json` is the default and returns the standard envelope. `--format patch` writes a unified
  patch to stdout or `--out`.
- `--path` filters changes by bundle-relative glob; it never changes what the provider computes.
- `--json` with `--format patch` is `INVALID_REQUEST`, exit `2`.

### 2.3 Request

```json
{
  "v": "weave.source/v1",
  "type": "source_diff_request",
  "source_id": "w8f3c2a1d4b5e6f7",
  "uri": "git+https://git.example.com/team/weave.git",
  "cache_dir": "/home/user/.cache/weave",
  "from": "3f2a1c9",
  "to": "9b7e4d0",
  "options": {
    "format": "changes",
    "context": 3,
    "permissive": false
  }
}
```

- `source_id`, `uri` and `cache_dir` have the meaning defined in [Weave Git §5.1](weave-git.md).
- `options.format` is `changes` or `patch`; `options.context` bounds unified hunks and defaults to `3`.
- `options.permissive` allows a cached ref to be used when a remote cannot be reached.

### 2.4 Response

```json
{
  "v": "weave.source/v1",
  "type": "source_diff_response",
  "from": "3f2a1c9",
  "to": "9b7e4d0",
  "truncated": false,
  "changes": [
    {"kind": "added", "path": "docs/new.md"},
    {"kind": "modified", "path": "docs/adr-004.md", "patch": "@@ -1,3 +1,4 @@\n ..."},
    {"kind": "renamed", "path": "docs/guide.md", "previous_path": "docs/old.md", "binary": false}
  ]
}
```

| Field | Meaning |
| --- | --- |
| `from`, `to` | Resolved commits or snapshot ids, echoed |
| `kind` | `added`, `removed`, `modified` or `renamed` |
| `path` | Bundle-relative POSIX path |
| `previous_path` | Old path for a rename |
| `binary` | Content is not text; `patch` is omitted |
| `patch` | Unified hunks, present only in `patch` format |
| `truncated` | Limits cut the result |

### 2.5 Determinism and bounds

- Changes sort by `path`, then `kind`; a rename sorts by `path`.
- The same refs, provider and options produce byte-identical output.
- Core bounds change count, patch bytes, path length and hunk count. A provider that exceeds a bound
  is `EXTENSION_PROTOCOL`; no partial output is rendered.
- Paths must be bundle-relative and must not escape the snapshot root; a violating path is
  `EXTENSION_PROTOCOL`.

## 3. Behavior

- Diff is read-only: it never writes the bundle, the index or the database. The provider may populate
  its snapshot cache exactly as a materialization would.
- `--format json` returns `changes[]`; `--format patch` concatenates the per-file patches in change
  order with `a/` and `b/` prefixes.
- A ref that the provider cannot resolve is `EXTENSION_FAILED` with a message naming the ref, exit
  `1`; core does not guess another ref.
- Snapshot retention is the provider's: diffing a snapshot the cache no longer holds fails with
  `EXTENSION_FAILED`.

## 4. Errors

| Condition | Code | Exit |
| --- | --- | --- |
| Provider does not declare `diff` | `SOURCE_UNSUPPORTED` | `2` |
| Missing or malformed `--from`/`--to` | `INVALID_REQUEST` | `2` |
| Source id missing or ambiguous | `INVALID_REQUEST` | `2` |
| Requirement unmet | `EXTENSION_REQUIREMENT_UNMET` | `1` |
| Ref not found or cache miss | `EXTENSION_FAILED` | `1` |
| Timeout | `EXTENSION_TIMEOUT` | `1` |
| Malformed or oversized response | `EXTENSION_PROTOCOL` | `1` |

## 5. Testing

- Added, removed, modified and renamed files, with and without patches.
- A binary file reports `binary` and no patch.
- The same refs produce identical JSON and patch bytes across runs.
- A provider without the capability exits `2` without invoking it.
- A missing ref, a timeout, a malformed response and an oversized response each map to their code.
- A path that escapes the snapshot root is refused.
- The bundle and database are unchanged after a diff.
- `weave-git` and a non-git fixture provider both pass the same request/response validation.

## 6. Acceptance Criteria

1. A user can compare two snapshots of a git source without a git command.
2. The operation is provider-owned and another provider can implement it.
3. Output is deterministic and bounded; patches are opt-in.
4. Diff never changes the bundle or its index.

## Related Documents

- [ADR 0017](../architecture/adr/0017-generic-source-diff-operation.md)
- [Weave Git](weave-git.md)
- [Extension Subprocess IPC](extension-ipc.md)
