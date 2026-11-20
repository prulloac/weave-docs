---
type: specification
title: "Enrichment Caching Specification"
description: "Reuses stored per-document enrichment when the enricher, its version and the document content are unchanged, with --force to bypass the cache."
tags:
  - "specification"
  - "extensions"
  - "enrichment"
  - "cache"
status: draft
---

# Specification: Enrichment Caching

## 1. Overview

Per-document enrichment runs an extension once for each document on every ingest, rebuild or sync. For
large bundles most documents have not changed. This specification lets Weave reuse a stored enrichment
when nothing that affects its output has changed. The stored result is the one the extension already
returned; reuse changes no output.

Non-goals:

- Caching project analysis, reranking, scoring or embeddings.
- Caching failed responses. Failures keep the previous enrichment, as extension IPC §2.3 requires.
- Cross-bundle or cross-machine caches.

## 2. Contract

### 2.1 Cache key

The key is the SHA-256 of canonical JSON containing:

- the enricher name;
- the enricher `version` from `--describe --json`, or the literal `unversioned` when absent;
- `doc_id`, `doc_path`, `media_type`, `title`, `frontmatter` and `body`, as sent in the request.

The key excludes `bundle_root` and `workspace`, which change between machines and invocations.

### 2.2 Storage

- No schema change. The key and a `has_files` flag are stored inside the existing `enrichments` row, in
  `data_json`, next to the response that is already stored there.
- `has_files` is `true` when the extension wrote files into its workspace on that run.

### 2.3 Reuse rules

- A stored enrichment is reused only when its key equals the newly computed key, and its `has_files` is
  `false`.
- An enrichment with `has_files` `true` is never reused. Extension data artifacts come from the
  workspace, and a reused result would drop them.
- A reused enrichment does not invoke the extension and adds no warning.
- A reused enrichment applies the same keyword merge and metadata rules as a fresh one.

### 2.4 Flags

- `--force` skips the lookup and invokes the extension for every document. Fresh results are still stored.
- The flag is valid on `ingest`, `rebuild` and `sync` only when an enricher is selected. Otherwise
  `INVALID_REQUEST`, exit `2`.

### 2.5 Failure

A timed-out, failed or malformed response is never stored. The previous enrichment, if any, stays in
place, and the warning rules of extension IPC §2.3 apply.

## 3. Testing

- Second run with an unchanged document does not invoke the extension.
- Changing the body, the enricher version or the enricher name invalidates the entry.
- `--force` invokes the extension and stores the new result.
- An enrichment that wrote workspace files is never reused.
- A failed response is not stored.

## 4. Acceptance Criteria

1. Re-running an unchanged ingest invokes no enrichment extension.
2. Output after a cached run is identical to a fresh run for the same inputs.

## Related Documents

- [Extension Subprocess IPC](extension-ipc.md)
- [Storage & Sync](storage-and-sync.md)
- [Incremental Sync](https://github.com/prulloac/weave/blob/main/docs/bdd/incremental-sync.md)
