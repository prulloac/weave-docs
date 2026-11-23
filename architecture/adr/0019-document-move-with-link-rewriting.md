---
type: Architecture Decision Record
title: "ADR 0019: Document Move with Link Rewriting"
description: "Reverses the no-writes-to-source-bundles non-goal for one explicit command that moves a document and rewrites the relative links and related ids that point at it."
tags:
  - "architecture"
  - "cli"
  - "bundle"
  - "links"
status: accepted
---

# ADR 0019: Document Move with Link Rewriting

## Context

Renaming a document by hand breaks every relative link and every `related` id that names its path.
The non-goal "No writes to source bundles" kept Weave read-only, so authors used `mv` and repaired
links themselves. The owner approved one narrow write command: move a document and repair the
references that point at it. Everything else stays read-only.

## Decision

1. **One command, one document.** `weave mv <bundle> <old-path> <new-path> [--dry-run] [--json]`
   moves or renames exactly one document. Directories, assets, symlinks and cross-bundle moves are
   out of scope for the first release.
2. **Destination must be free.** An existing destination is `DESTINATION_EXISTS`, exit `1`; there is
   no overwrite flag. A case-only rename is allowed when the source and destination resolve to the
   same file on the current filesystem.
3. **Relative links are rewritten.** Markdown links and images whose target resolves to the old path
   are rewritten to keep resolving, preserving the link style (relative or root-relative), the
   fragment and the title. Links inside fenced code, inline code and HTML comments are left alone, as
   are absolute URLs and links that already point at the destination.
4. **Ids are rewritten.** The document's own id changes with its path; `related` entries and any
   stored relation that names the old id are updated. Keyword, tag and title values are untouched.
5. **Preview first.** `--dry-run` reports the move and every rewrite without touching disk, the index
   or the database. Human output is one line per rewrite; JSON uses the standard envelope.
6. **Atomic where possible.** The file move and the link rewrites complete before the index update;
   the index update runs in one transaction. If the index update fails, the command restores the file
   and the rewritten content and reports `MOVE_FAILED`. A missing database is not an error: the move
   still runs and the next ingest indexes it.
7. **No content rewrite beyond references.** Frontmatter values other than `related` ids, body prose
   and asset bytes are not changed. Encrypted or tokenized bodies are never decrypted; a protected
   document whose links cannot be inspected is refused with `PRIVACY_DIRECTIVE_INVALID`.
8. **Output.** The result reports `from`, `to`, `rewritten` (path and count per document) and
   `dry_run`. Exit is `0` on success, `1` on a refused or failed move, `2` on a usage error.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Move only, leave links | Rejected: it reproduces the problem the command exists to solve |
| Rewrite absolute GitHub URLs | Rejected for now: it needs repository identity and can rewrite links outside the bundle |
| Keep all bundles read-only | Rejected by the owner in favour of one explicit command |
| A general `weave edit` | Rejected: it is a much larger write surface |
| Rewrite ids in every frontmatter field | Rejected: only `related` ids name documents |

## Consequences

- The roadmap non-goal is marked reversed; the remaining bundle writes stay limited to this command.
- The index can be stale between the move and the next sync; the command updates it when present.
- Watchers observe a removal and an addition; incremental sync must not treat them as unrelated.
- A new spec, BDD scenarios and a link-rewriting test matrix (fragments, spaces, code blocks,
  root-relative links) are required before implementation.
