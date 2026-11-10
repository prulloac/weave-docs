---
type: specification
title: "Embeddings and Semantic Search Specification"
description: "First-class document embeddings, dynamic per-space vec0 indexes and weave-ai-backed semantic search without CGO."
tags:
  - "specification"
  - "embeddings"
  - "semantic-search"
  - "sqlite"
  - "vec0"
  - "0.7"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-03T00:00:00Z"
status: stable
---

# Specification: Embeddings and Semantic Search

## 1. Overview

Weave stores document embeddings in a durable table and indexes them in one `vec0` virtual table per
embedding space. `weave-ai` provides embedding requests for documents and queries. `weave search
--mode semantic` uses cosine KNN, joins results back to documents and returns ordinary search hits.

The index is CGo-free. `modernc.org/sqlite/vec` bundles sqlite-vec v0.1.9 inside the existing
pure-Go SQLite module.

## 2. Non-Goals

- External vector databases, ANN clusters or HNSW/IVF indexes in the first slice.
- Cross-model score averaging; different spaces are not comparable.
- Embeddings without persistent storage; `--no-db` does not support semantic search.
- Native C `sqlite-vec` loading or a different SQLite driver.
- Multimodal image/audio/video embeddings in the first release; the schema supports them later.
- Encrypted embeddings or exported embeddings in the first slice.

## 3. Data Model

Schema version 7 adds:

```sql
CREATE TABLE document_embeddings (
    bundle_root TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    model TEXT NOT NULL,
    dim INTEGER NOT NULL,
    vector BLOB NOT NULL,          -- float32 little-endian, normalized
    content_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    PRIMARY KEY (bundle_root, doc_id, model, dim),
    FOREIGN KEY (bundle_root, doc_id)
        REFERENCES documents(bundle_root, id) ON DELETE CASCADE
);

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

- `document_embeddings` is the source of truth and supports multiple models per document; the same
  model at two dimensions yields two source rows and two spaces.
- `vector` is normalized float32 little-endian; `dim` must match its length exactly.
- `content_hash` detects embeddings produced from an older document version.
- `embedding_indexes` maps a space tuple to one `vec0` table.

## 4. Embedding Spaces

An embedding space is:

```text
(model, dim, metric, element_type)
```

- Different dimensions require separate tables.
- Different models are separate spaces even at the same dimension; their scores are not comparable.
- The same model/dimension can serve multiple document types if the vectors are semantically aligned.
- The first slice uses `metric=cosine` and `element_type=float32`.
- A CLIP-style model may serve text and image vectors in one space; otherwise text, image, audio and
  video embeddings use separate spaces.

### 4.1 `vec0` table

Core creates one table per space:

```sql
CREATE VIRTUAL TABLE vec_embeddings_<modelhash>_<dim> USING vec0(
    bundle_root TEXT PARTITION KEY,
    doc_key TEXT PRIMARY KEY,      -- bundle_root + '/' + doc_id
    doc_id TEXT,
    content_hash TEXT,
    embedding float[<dim>] distance_metric=cosine
);
```

- `doc_key` is globally unique; `vec0` primary keys are not partition-scoped.
- `bundle_root` is the partition key.
- `doc_id` and `content_hash` are metadata columns and must be supplied on every insert.
- Table names use a hash of the space tuple, never the raw model string.
- Creation is core-owned DDL; extensions never create tables.

### 4.2 Dynamic creation

1. An embedder returns `{model, dim, metric, element_type}`.
2. Core looks up `embedding_indexes`.
3. If the space is absent, core creates the `vec0` table with `CREATE VIRTUAL TABLE IF NOT EXISTS`,
   inserts the registry row, and optionally backfills from `document_embeddings`.
4. Search never creates a table. A missing space is a clear error or fallback.

Concurrent creators are serialized by SQLite; `IF NOT EXISTS` and the registry primary key make the
operation idempotent. `SQLITE_BUSY` retries are bounded.

## 5. Embedder Role

### 5.1 CLI

```sh
weave ingest ~/notes --with-embedder ai --db ~/.weave/index.db
weave sync ~/notes --with-embedder ai --db ~/.weave/index.db
weave rebuild ~/notes --with-embedder ai --db ~/.weave/index.db
weave search ~/notes "token rotation" --mode semantic --db ~/.weave/index.db
```

- `--with-embedder <name>` selects a `weave-<name>` extension with an embedding role and applies to
  `ingest`, `rebuild` and `sync`.
- Without `--with-embedder`, updated documents keep their old embedding; the `content_hash` mismatch
  marks it stale until a run with the embedder refreshes it.
- The embedder is invoked after text/metadata enrichment. Its text input is `body_raw` when present;
  otherwise it is `content_metadata.text` for binary blobs, plus title and description. The text is
  truncated to 8 KiB before the request.
- `weave-ai` is the reference embedder; other embedders use the same protocol.

### 5.2 Embedding request

```json
{
  "v": "weave.cli/v1",
  "type": "embedding_request",
  "text": "Searchable text or query",
  "media_type": "text/plain",
  "model": "configured model"
}
```

Response:

```json
{
  "v": "weave.cli/v1",
  "model": "nomic-embed-text",
  "dim": 768,
  "vector": "<base64 float32 little-endian>"
}
```

- Core validates `model`, `dim`, vector length and finite values; it normalizes the vector before
  storage.
- The response `model` must match the request. The response `dim`, validated against the vector
  length, identifies the space.
- A malformed or oversized response fails the embedding for that document with a warning.
- A failed embedding does not fail the document write.

### 5.3 Write lifecycle

- Insert/update the document, `document_embeddings` row and `vec0` row in one transaction.
- If the source row already exists, replace it and update the index.
- `vec0` does not honor `INSERT OR REPLACE`; use delete + insert or an explicit update.
- On document delete, delete the source row (cascade) and every `vec0` row for the document.
- If the index write fails, roll back the whole write.
- `content_hash` mismatch means the embedding is stale; re-embed or mark it inactive.

## 6. Search

```sh
weave search ~/notes "a red bicycle beside water" --mode semantic --db ~/.weave/index.db
weave search ~/notes "a red bicycle" --mode semantic --embedder ai --json
```

- Core embeds the query with the selected embedder/model.
- It chooses the matching `vec0` table from `embedding_indexes`.
- KNN query:

```sql
SELECT doc_id, content_hash, distance
FROM vec_embeddings_<modelhash>_<dim>
WHERE embedding MATCH vec_f32(?)
  AND bundle_root = ?
  AND k = ?
```

- `k` is the requested top-K, validated and inlined/bound by core.
- Cosine distance is converted to a score: `score = 1 - distance`.
- Results join `documents` on `(bundle_root, doc_id)` for title, description, type and media type.
- Results carry `semantic_score` and the model/dimension used.
- If the query embedder or active index is missing, semantic mode fails with an actionable error;
  keyword, fuzzy, hybrid and BM25 are unchanged.
- Hybrid semantic+BM25 blending and cross-space rank fusion are deferred.

## 7. Model and Dimension Changes

1. Create the new space table.
2. Backfill from `document_embeddings` when the model is compatible; otherwise re-embed.
3. Mark the new registry row active.
4. Keep the old table until validation completes; then drop it.

`weave embeddings` maintenance commands:

```sh
weave embeddings list ~/notes --json
weave embeddings rebuild ~/notes --model <model> [--with-embedder <name>] --db ~/.weave/index.db
weave embeddings drop ~/notes --model <model> --db ~/.weave/index.db
```

- `list` reports model, dim, metric, element type, table name, active state and the bundle's row
  count.
- `rebuild` re-derives the bundle's rows from `document_embeddings`: it deletes the bundle partition,
  re-inserts it and creates the table if absent. Other bundles in the shared table are untouched.
  When source vectors for the model are absent, it re-embeds with `--with-embedder`; without an
  embedder the command fails with an actionable error.
- `drop` deletes the bundle's `document_embeddings` rows and `vec0` partition. It drops the table and
  registry row only when no bundle still has source rows for that space. `--keep-source` keeps the
  durable source rows, removes only the index rows and therefore keeps the space registered.
- `weave audit` reports `EMBEDDING_STALE` and `EMBEDDING_INDEX_MISMATCH` findings.

## 8. Performance and Limits

- `vec0` is optimized brute-force KNN, not HNSW or IVF. It is suitable for local bundles; benchmark
  against the 10k corpus before claiming large-scale behavior.
- No ANN index is promised in this slice.
- A 768-dimension float32 vector is ~3 KiB; the durable table duplicates the vector in `vec0`.
- Embedding input is truncated to 8 KiB of text; tokenization and provider limits beyond that are the
  embedder's responsibility.
- `modernc.org/sqlite/vec` adds about 328 KiB to a minimal static binary; all six release targets
  compile without CGO.
- `sqlite-vec` is v0.1.9 and pre-v1; pin `modernc.org/sqlite` and add regression tests around vec SQL.
- Importing `modernc.org/sqlite/vec` rules out `RegisterPageCache`; Weave does not use it today.
- A third-party notice for sqlite-vec (MIT/Apache-2.0) ships with the repository and release archive.
- Databases containing `vec0` tables require the extension; the `weave` binary loads it, but plain
  `sqlite3` tools may need sqlite-vec to query vector tables.

## 9. Privacy and Export

- Embeddings are derived from document text and are stored locally.
- Sending text/OCR/EXIF to `weave-ai` follows its provider configuration; core does not call a
  provider directly.
- Embeddings are not part of raw or encrypted bundle export; they are rebuildable derived data.
- A database backup includes `document_embeddings` and `vec0` tables.
- Deleting a document cascades the durable embedding row and explicitly deletes index rows.

## 10. Contract Additions

| Type | Field | Meaning |
| --- | --- | --- |
| `document_embeddings` | `model`, `dim`, `vector`, `content_hash` | Durable embedding |
| `embedding_indexes` | `model`, `dim`, `metric`, `element_type`, `table_name`, `active` | Space registry |
| Search hits | `semantic_score`, `embedding_model`, `embedding_dim` | Optional semantic fields |
| CLI | `--with-embedder`, `--mode semantic`, `weave embeddings list/rebuild/drop` | Commands |
| Extension IPC | `embedding_request`, `embedding_response` | Embedder contract |
| `weave-ai` | vision/embedding capabilities and models | AI extension amendment |

Schemas and goldens update additively within v1.

## 11. Testing

- `vec0` text primary key, partition key, metadata columns, cosine metric, update/delete.
- Global `doc_key` collision across bundles.
- Parameterized `bundle_root` and `k`; parameterized query vector.
- Transaction insert and rollback include `vec0` rows.
- Dynamic creation idempotence and concurrent create retry.
- Source-table cascade and explicit index delete.
- Model/dim change, backfill, rebuild, drop and stale `content_hash`.
- Semantic search result joining, score conversion and fallback errors.
- Existing keyword/fuzzy/hybrid/BM25 tests and calibration unchanged.
- 10k benchmark and binary size check.
- All six targets build with `CGO_ENABLED=0`.
- Third-party license notice.

Behavior scenarios: [embeddings.md](https://github.com/prulloac/weave/blob/main/docs/bdd/embeddings.md).

## 12. Acceptance Criteria

1. A document can have embeddings from multiple models; each model uses its own `vec0` space.
2. `document_embeddings` is the durable source; `vec0` is rebuildable.
3. Text embeddings of OCR/description make image documents semantically searchable.
4. `weave search --mode semantic` returns document metadata with cosine scores.
5. Model and dimension changes do not corrupt existing spaces.
6. Deletes and sync keep source rows and `vec0` rows consistent.
7. No native C extension, CGO or new release matrix is required.
8. Existing search modes, calibration and `--no-db` behavior remain unchanged.

## Related Documents

- [ADR 0005: Embeddings and CGo-Free vec0 Index](../architecture/adr/0005-embeddings-and-cgo-free-vec0-index.md)
- [Generic Blob Assets](blob-assets.md)
- [Weave Image Extension](weave-image.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [Weave AI Extension](weave-ai-plugin.md)
- [Storage & Sync](storage-and-sync.md)
- [ROADMAP](../ROADMAP.md)
