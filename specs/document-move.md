---
type: specification
title: "Document Move with Link Rewriting"
description: "One explicit write command that moves a bundle document and rewrites the relative Markdown links, images and related ids that point at it."
tags:
  - "cli"
  - "bundle"
  - "links"
status: draft
---

# Document Move with Link Rewriting

## 1. Overview

`weave mv` moves or renames one document inside a bundle and repairs the references that name its old
path, so a rename does not leave broken links or dangling graph edges. It is the only command that
writes bundle content besides ingest-adjacent metadata. The decision is
[ADR 0019](../architecture/adr/0019-document-move-with-link-rewriting.md).

## 2. Contract

### 2.1 Syntax

```sh
weave mv <bundle> <old-path> <new-path> [--dry-run] [--json]
```

- Both paths are bundle-relative POSIX paths and must end in `.md`.
- Exactly one document moves. Directories, assets, symlinks and cross-bundle moves are
  `INVALID_REQUEST`, exit `2`.
- An existing destination is `DESTINATION_EXISTS`, exit `1`; there is no overwrite flag.
- A case-only rename is allowed when both paths resolve to the same file.
- `--dry-run` reports the planned move and rewrites and changes nothing.

### 2.2 What is rewritten

| Location | Rewrite |
| --- | --- |
| Inline Markdown link or image whose target resolves to the old path | New relative or root-relative target that resolves to the new path; fragment and title preserved |
| Reference definition used by a link or image | Same rewrite as the inline form |
| `related` value that resolves to the old document | New id, in the same style as the original (bare or relative) |
| Link that already points at the destination | Unchanged |
| External URL, absolute URL, anchor-only link | Unchanged |
| Fenced code, inline code, HTML comment | Unchanged |

- A root-relative target stays root-relative; a relative target stays relative to the referencing
  document.
- The document's own id changes with its path; references to the old id are updated in every document
  that contains one.
- Prose, frontmatter other than `related`, asset bytes and encrypted content are not changed.

### 2.3 Result

```json
{
  "from": "notes/old.md",
  "to": "notes/new.md",
  "dry_run": false,
  "rewritten": [
    {"path": "notes/index.md", "references": 2},
    {"path": "notes/old.md", "references": 0}
  ]
}
```

- `rewritten` is sorted by path and counts the references changed in each file.
- Human output prints the move and one line per rewritten file.
- Exit is `0` on success, `1` on a refused or failed move and `2` on a usage error.

### 2.4 Index and failure

- When a database exists, the index update runs in one transaction after the file operation.
- If the index update fails, the file and every rewritten file are restored and the command reports
  `MOVE_FAILED`, exit `1`.
- Without a database the move succeeds and the next `ingest` or `sync` indexes it.
- A protected document whose links cannot be read is `PRIVACY_DIRECTIVE_INVALID`; no partial move is
  performed.

## 3. Errors

| Condition | Code | Exit |
| --- | --- | --- |
| Missing path, wrong extension, directory, symlink or cross-bundle target | `INVALID_REQUEST` | `2` |
| Destination exists | `DESTINATION_EXISTS` | `1` |
| Source document missing | `CONCEPT_NOT_FOUND` | `1` |
| Link or id rewrite cannot be applied safely | `MOVE_FAILED` | `1` |
| Protected content blocks inspection | `PRIVACY_DIRECTIVE_INVALID` | `1` |

## 4. Testing

- Move within a directory, to a parent and into a child; every relative link still resolves.
- Fragments (`old.md#section`) and link titles survive the rewrite.
- Root-relative links and references used by images are rewritten.
- Links in fenced code, inline code and HTML comments are untouched.
- External URLs and links that already point at the destination are untouched.
- `related` entries in bare and relative form are rewritten; other frontmatter is unchanged.
- Destination exists, directory, symlink and non-Markdown inputs are refused.
- `--dry-run` changes no file and no database row.
- An index failure restores the original tree and reports `MOVE_FAILED`.
- A case-only rename works on a case-insensitive filesystem.

## 5. Acceptance Criteria

1. After a move, every relative link and `related` id in the bundle still resolves.
2. No content outside links and `related` ids changes.
3. A refused or failed move leaves the bundle and index unchanged.
4. `--dry-run` is a complete preview and writes nothing.

## Related Documents

- [ADR 0019](../architecture/adr/0019-document-move-with-link-rewriting.md)
- [OKF Bundle Parser](okf-bundle-parser.md)
- [Node Graph Engine](node-graph-engine.md)
