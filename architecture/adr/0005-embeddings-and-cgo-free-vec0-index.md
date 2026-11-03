---
type: Architecture Decision Record
title: "ADR 0005: Embeddings and CGo-Free vec0 Index"
description: "Makes embeddings first-class with a durable embeddings table, a per-space vec0 index using modernc.org/sqlite/vec, and semantic search without CGO."
tags:
  - "architecture"
  - "adr"
  - "embeddings"
  - "semantic-search"
  - "sqlite"
  - "extensions"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-03T00:00:00Z"
status: accepted
---

# ADR 0005: Embeddings and CGo-Free vec0 Index

## Status

Accepted on 2026-11-03. It complements [ADR 0004](0004-generic-blob-assets-and-content-metadata.md)
and the [Embeddings specification](../../specs/embeddings.md).

## Context

Weave v1.0 search is keyword, fuzzy, hybrid and BM25. It has no semantic or vector search.
`weave-ai` is text-only and has no embedding request. SQLite has no native vector type or vector
index. The obvious extension, `sqlite-vec`, is a C library; loading it as a native SQLite extension
would require CGO or a different SQLite driver and would break the static, CGO-free release model.

At the same time, the project has zero external users and the schema can be shaped correctly now.
Deferring the vector index would force a later migration of stored embeddings and search behavior.

## Decision Summary

| ID | Decision |
| --- | --- |
| D1 | Embeddings are first-class core data, not extension sidecars |
| D2 | A durable `document_embeddings` table is the source of truth |
| D3 | `embedding_indexes` records each embedding space and its `vec0` table |
| D4 | One `vec0` table per `(model, dim, metric, element_type)` embedding space |
| D5 | Use `modernc.org/sqlite/vec`, not a native C extension or WASM driver |
| D6 | `vec0` rows use `doc_key` as a global primary key, `bundle_root` as partition, and metadata for `doc_id`/`content_hash` |
| D7 | Writes and deletes maintain both the source table and the `vec0` index in one transaction |
| D8 | `weave-ai` gains an embedding request; `weave search --mode semantic` uses it |
| D9 | Text embeddings ship first; image, video and audio spaces use the same model later |

## D1 — First-class embeddings

### Decision

Core stores embeddings for documents. Extensions request or provide them; they do not own vector
tables or query the database directly.

### Rationale

Embeddings are expensive derived data used by core search and future related-document features.
Keeping them in extension sidecars would make search, lifecycle, export and model migration
extension-specific.

## D2 — Durable source table

### Decision

```sql
CREATE TABLE document_embeddings (
    bundle_root TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    model TEXT NOT NULL,
    dim INTEGER NOT NULL,
    vector BLOB NOT NULL,          -- float32 little-endian, normalized
    content_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    PRIMARY KEY (bundle_root, doc_id, model),
    FOREIGN KEY (bundle_root, doc_id)
        REFERENCES documents(bundle_root, id) ON DELETE CASCADE
);
```

### Rationale

The table is the durable record. It supports multiple models per document, cascades on document
delete, lets us rebuild the vector index, and keeps a copy if `vec0` changes or is corrupted.

## D3 — Space registry

### Decision

```sql
CREATE TABLE embedding_indexes (
    model TEXT NOT NULL,
    dim INTEGER NOT NULL,
    metric TEXT NOT NULL,          -- cosine in the first slice
    element_type TEXT NOT NULL,    -- float32 in the first slice
    table_name TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL,
    PRIMARY KEY (model, dim, metric, element_type)
);
```

### Rationale

The registry maps a model/dimension/metric to one `vec0` table and lets core discover, activate or
retire embedding spaces without guessing from table names.

## D4 — One `vec0` table per embedding space

### Decision

```sql
CREATE VIRTUAL TABLE vec_embeddings_<modelhash>_<dim> USING vec0(
    bundle_root TEXT PARTITION KEY,
    doc_key TEXT PRIMARY KEY,      -- bundle_root + '/' + doc_id
    doc_id TEXT,
    content_hash TEXT,
    embedding float[<dim>] distance_metric=cosine
);
```

The table is created by core when a new `(model, dim, metric, element_type)` is first stored.

### Rationale

A `vec0` vector column has a fixed dimension. Different models and dimensions are not comparable,
so they need separate KNN indexes. The same model/dimension can serve multiple document types if
the vectors share one semantic space.

## D5 — CGo-free vector extension

### Decision

Import `_ "modernc.org/sqlite/vec"`. Do not use `mattn/go-sqlite3`, native `.so`/`.dylib`/`.dll`
extensions, or the WASM driver.

### Rationale

`modernc.org/sqlite` v1.61.0 bundles sqlite-vec v0.1.9 as transpiled Go. Verified in this workspace:

- all six release targets have the vec package;
- `CGO_ENABLED=0` builds;
- `vec_version()` and `vec0` KNN work;
- binary growth is about 328 KiB;
- `UPDATE`, `DELETE`, parameterized `k`, cosine metric and transactional rollback work.

A native C extension would break the pure-Go, static release invariant and the existing installers.

## D6 — Global key and partition

### Decision

`vec0` primary keys are global, not partition-scoped. Use:

```text
doc_key = bundle_root + "/" + doc_id
```

`bundle_root` is the partition key, while `doc_id` and `content_hash` are metadata columns for joins
and staleness checks.

### Rationale

Verified behavior: the same `doc_id` in two bundles otherwise collides. Metadata columns must be
supplied on insert; they cannot be omitted or NULL.

## D7 — Transactional lifecycle

### Decision

- Insert/update the `documents` row, `document_embeddings` row and matching `vec0` row in one
  transaction.
- Delete both the source row and the `vec0` row explicitly; `vec0` has no foreign-key cascade.
- `vec0` does not honor `INSERT OR REPLACE`; use delete + insert or an explicit update.
- If the vector write fails, the document write rolls back.

### Rationale

A vector index that drifts from the document table is worse than no index. Verified rollback
includes `vec0` rows.

## D8 — AI embedding request and semantic search

### Decision

`weave-ai` adds:

- `embedding_request` with text, optional media type and model;
- `embedding_response` with model, dimension and base64 float32 vector;
- an embedder role selected by `--with-embedder ai`.

`weave search --mode semantic` embeds the query through the configured embedder, queries the active
space, and joins results back to documents. Missing embedder or index is a clear error; existing
search modes are unchanged.

### Rationale

The query and documents must be embedded by the same model. A generic embedder role keeps
`weave-ai` first-class without hardcoding AI in core search.

## D9 — Text first, other spaces later

### Decision

The first release embeds `content_metadata.text` (OCR, transcripts, PDF text), title and description
as text. Image-pixel or other multimodal embeddings use a later model and a separate space; the
schema supports them from day one.

### Rationale

Text embeddings deliver semantic image knowledge immediately because image metadata and OCR are
text. Multimodal embedding models can be added without schema changes.

## Consequences

- Schema version 7 adds `document_embeddings` and `embedding_indexes`; `vec0` tables are created
  dynamically by core.
- `weave` imports `modernc.org/sqlite/vec`; release binaries grow slightly, but remain CGO-free.
- sqlite-vec is pre-v1; the durable source table allows a rebuild if its format changes.
- A third-party notice is required for sqlite-vec.
- `vec0` tables require the extension; the `weave` binary always loads it, but plain `sqlite3` tools
  may need sqlite-vec for vector tables.
- Semantic search requires persistent storage and an embedder; `--no-db` does not support it.
- Text embeddings are not exported as bundle content; they are derived and can be rebuilt.

## Rejected Alternatives

| Alternative | Why rejected |
| --- | --- |
| Native C `sqlite-vec` | Requires CGO, breaks static cross-compiled releases and installers |
| WASM `ncruces/go-sqlite3` | Different driver, WASM memory overhead, unnecessary migration |
| No vector index; Go cosine only | Works small, but with zero users this is the moment to build the index |
| `vec0` as the only storage | Fixed dimension, no cascade, pre-v1 format, no durable rebuild source |
| One table with a `model` filter | Scores from different models are not comparable; dimensions may differ |
| Cross-model score averaging | Different spaces are not comparable; use rank fusion later |
| External vector database | Violates local-first and single-binary operation |

## Related Documents

- [Embeddings specification](../../specs/embeddings.md)
- [Generic Blob Assets specification](../../specs/blob-assets.md)
- [ADR 0004: Generic Blob Assets and Content Metadata](0004-generic-blob-assets-and-content-metadata.md)
- [Extension Subprocess IPC specification](../../specs/extension-ipc.md)
- [Weave AI Extension specification](../../specs/weave-ai-plugin.md)
- [Storage & Sync specification](../../specs/storage-and-sync.md)
- [ROADMAP](../../ROADMAP.md)
