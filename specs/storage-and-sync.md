---
type: specification
title: "Storage, Persistence & Incremental Sync"
description: "Persistent SQLite storage, sha256 incremental sync, cascading graph updates and compressed in-memory indexes."
tags:
  - "specification"
  - "storage"
  - "sqlite"
  - "sync"
  - "v1"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-10-27T00:00:00Z"
status: draft
---

# Weave: Storage, Persistence & Incremental Sync Specification

---

## 1. Overview

Weave v1.0 transitions the storage engine from a transient, in-memory parser to an incremental, persistent SQLite database. The goals are:

1. **Sub-10ms CLI cold starts:** Querying a 10,000-document repository without re-parsing files.
2. **Zero-CGO static compilation:** Utilizing pure-Go SQLite (`modernc.org/sqlite`).
3. **Deterministic upsert synchronization:** Efficient diffing via content hashes (`sha256`) instead of unreliable filesystem timestamps.
4. **Cascading graph integrity:** Recomputing backlinks, degree counts, and paths when files are added, modified, or deleted.

---

## 2. SQLite Schema Design

The default SQLite database lives at `~/.weave/index.db` and stores multiple bundles, keyed by the
absolute normalized `bundle_root`. It is configured with `PRAGMA journal_mode=WAL;` and
`PRAGMA foreign_keys=ON;`. The `~/.weave` directory is created with mode `0700` when missing.

The database records its own schema version with `PRAGMA user_version` (starting at `1`). Schema
migrations bump this number independently of the product version and `weave.contract/v1`; a binary
refuses to open a database with a newer `user_version`.

Current schema is **7**. Version 4 adds `search_tokens` (`bundle_root`, `field`, `token`,
`postings` BLOB) for the persistent fuzzy/hybrid path. Version 5 adds `search_vocabulary`
(`bundle_root`, `field`, `token`) so fuzzy queries only load postings for candidate tokens. Version
6 adds `extension_data`; version 7 adds generic blob metadata, the `body_raw`/`body_compressed`
split, the per-bundle asset filter, durable embeddings and the embedding space registry. Older
databases migrate automatically; new tables start empty, and fuzzy/hybrid search falls back to the
in-memory engine until the next ingest, rebuild or sync populates them.

```sql
-- 0. Bundle Registry
CREATE TABLE IF NOT EXISTS bundles (
    bundle_root TEXT PRIMARY KEY,        -- Absolute normalized bundle root
    mode TEXT NOT NULL DEFAULT 'strict', -- strict | permissive
    okf_version TEXT,
    index_json TEXT NOT NULL,            -- Serialized []IndexEntry
    validation_json TEXT NOT NULL,       -- Serialized Validation
    asset_types_json TEXT NOT NULL DEFAULT '[]', -- Resolved blob filter; [] = Markdown-only
    updated_at INTEGER NOT NULL
);

-- 1. Document Registry
CREATE TABLE IF NOT EXISTS documents (
    bundle_root TEXT NOT NULL,
    id TEXT NOT NULL,                    -- Relative path or explicit bundle ID
    file_path TEXT NOT NULL,             -- Path relative to bundle root
    content_hash TEXT NOT NULL,          -- SHA-256 of raw file content
    title TEXT NOT NULL,
    description TEXT,
    doc_type TEXT,                       -- OKF type (e.g. runbook, spec, adr)
    keywords_json TEXT NOT NULL,         -- Serialized []string
    frontmatter_json TEXT NOT NULL,      -- Serialized map[string]any
    tags_json TEXT NOT NULL,             -- Serialized []string
    status TEXT,                         -- draft | stable | deprecated
    links_json TEXT NOT NULL,            -- Serialized []OkfLink
    content_kind TEXT NOT NULL DEFAULT 'document', -- document | blob
    media_type TEXT NOT NULL DEFAULT 'text/markdown',
    content_metadata TEXT NOT NULL DEFAULT '{}',   -- Versioned JSON envelope
    body_raw TEXT,                       -- Text-readable body, or NULL
    body_compressed BLOB,                -- Binary blob body, or NULL
    body_codec TEXT,                     -- Codec for body_compressed, or NULL
    size INTEGER NOT NULL DEFAULT 0,     -- Original body bytes
    stored_size INTEGER NOT NULL DEFAULT 0, -- Stored body bytes
    privacy_policy TEXT DEFAULT 'none',  -- none | encrypt | tokenize | hash | mixed
    updated_at INTEGER NOT NULL,         -- Unix timestamp of sync
    CHECK ((body_raw IS NULL) != (body_compressed IS NULL)),
    CHECK ((body_raw IS NOT NULL AND body_codec IS NULL)
        OR (body_compressed IS NOT NULL AND body_codec IS NOT NULL)),
    PRIMARY KEY (bundle_root, id),
    UNIQUE (bundle_root, file_path),
    FOREIGN KEY (bundle_root) REFERENCES bundles(bundle_root) ON DELETE CASCADE
);

-- 2. Graph Edges
CREATE TABLE IF NOT EXISTS edges (
    bundle_root TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,             -- link | related
    dangling INTEGER DEFAULT 0,          -- 1 if target does not resolve
    PRIMARY KEY (bundle_root, source_id, target_id, edge_type),
    FOREIGN KEY (bundle_root, source_id)
        REFERENCES documents(bundle_root, id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_edges_bundle_target
    ON edges(bundle_root, target_id);

-- 3. Full-Text Search (FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS fts_documents USING fts5 (
    bundle_root UNINDEXED,
    id UNINDEXED,
    title,
    description,
    keywords,
    body,
    tokenize = 'porter unicode61'
);

-- 4. Trigram Index for Substring / Typo Matching
CREATE VIRTUAL TABLE IF NOT EXISTS fts_trigrams USING fts5 (
    bundle_root UNINDEXED,
    id UNINDEXED,
    field UNINDEXED,                     -- title | description | body
    token,
    tokenize = 'trigram'
);

-- 5. Extension Enrichments (Key-Value Keyed by Provider)
CREATE TABLE IF NOT EXISTS enrichments (
    bundle_root TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    enricher_id TEXT NOT NULL,           -- e.g. weave-ai/embeddings-v1
    data_json TEXT NOT NULL,             -- Structured payload returned by plugin
    PRIMARY KEY (bundle_root, doc_id, enricher_id),
    FOREIGN KEY (bundle_root, doc_id)
        REFERENCES documents(bundle_root, id) ON DELETE CASCADE
);

-- 6. Durable Embeddings (v7)
CREATE TABLE IF NOT EXISTS document_embeddings (
    bundle_root TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    model TEXT NOT NULL,
    dim INTEGER NOT NULL,
    vector BLOB NOT NULL,                -- float32 little-endian, normalized
    content_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    PRIMARY KEY (bundle_root, doc_id, model, dim),
    FOREIGN KEY (bundle_root, doc_id)
        REFERENCES documents(bundle_root, id) ON DELETE CASCADE
);

-- 7. Embedding Space Registry (v7)
CREATE TABLE IF NOT EXISTS embedding_indexes (
    model TEXT NOT NULL,
    dim INTEGER NOT NULL,
    metric TEXT NOT NULL,                -- cosine
    element_type TEXT NOT NULL,          -- float32
    table_name TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL,
    PRIMARY KEY (model, dim, metric, element_type)
);
```

Each embedding space also has a dynamically created `vec0` virtual table. Its schema, lifecycle and
search contract live in [Embeddings](embeddings.md); it is derived from `document_embeddings` and
can be rebuilt.

---

## 3. Incremental Sync Workflow (`weave sync`)

Syncing avoids parsing unchanged files by maintaining a hash registry. Every statement is scoped by
`bundle_root`, so syncing one bundle never touches another bundle in the shared database.

```text
Filesystem Scan (*.md + bundle asset filter)
         │
         ▼
Compute SHA-256 of file content
         │
         ├── Hash matches DB? ─────────► Skip (No-op)
         │
         ├── Hash differs from DB? ────► Re-parse AST & Update
         │
         └── File removed from disk? ──► Delete & Cascade
```

### Cascade Rules on Modification / Deletion

1. **Delete / Prune:**
   - Removing `Doc A` triggers `ON DELETE CASCADE`, removing its outgoing edges from `edges` and its entries in `fts_documents` and `fts_trigrams`.
   - Incoming edges targeting `Doc A` are marked as `dangling = 1`.
2. **Update:**
   - If `Doc A` changes, its outgoing links are re-extracted. Old edges are deleted; new edges inserted.
   - Any edges where `Doc A` was previously marked as dangling are reconciled (`dangling = 0`).

---

## 4. Memory & Storage Compression Strategy

Compression is a storage implementation detail with its own contract. Summary:

- **Index Memory (Postings):** document IDs in transient postings are delta-encoded with
  variable-byte (`varint`) encoding.
- **Body Blobs:** text-readable bodies (Markdown, `.txt`, JSON, XML, CSV, source code) are stored in
  `body_raw` with NULL `body_compressed`/`body_codec`. Binary blobs use `body_compressed` with zstd
  by default; `body_codec` is non-null. Exactly one body column is non-null. LZ4 and other algorithms
  are `weave-codec-<name>` extensions.

Authoritative rules — text classification, binary zstd, codec extensions, ciphertext handling,
corruption recovery and rebuild behavior — are in [Compression](compression.md) and
[Codec Extensions](codec-extensions.md).

## 5. Storage Foundation Contract

The storage foundation is the first delivery slice. It provides `ingest`, `rebuild` and explicit
database-backed reads. Incremental `sync`, watch mode, FTS5 ranking, compression activation and
enrichments follow in later slices.

### 5.1 Commands

```text
weave ingest <path> [--db <file>] [--strict|--permissive] [--assets|--no-assets] [--asset-types <mime,...>] [--json] [--no-cache]
weave rebuild <path> [--db <file>] [--strict|--permissive] [--assets|--no-assets] [--asset-types <mime,...>] [--json] [--no-cache]
weave sync <path> [--db <file>] [--strict|--permissive] [--assets|--no-assets] [--asset-types <mime,...>] [--json] [--no-cache]

weave parse <path> ... [--db <file> | --no-db]
weave graph <path> ... [--db <file> | --no-db]
weave search <path> ... [--db <file> | --no-db]
weave list <path> ... [--db <file> | --no-db]
weave show <path> ... [--db <file> | --no-db]
weave backlinks <path> ... [--db <file> | --no-db]
weave path <path> ... [--db <file> | --no-db]
weave audit <path> ... [--db <file> | --no-db]
weave relate <path> ... [--db <file> | --no-db]
weave explain <path> ... [--db <file> | --no-db]
```

- The default database is `~/.weave/index.db`; `~` is expanded from the user home directory.
- **Persistence is on by default for bundle-reading commands.** `--no-db` opts out and uses the
  transient in-memory parser. `--db <file>` selects a different database.
- `--db` and `--no-db` are mutually exclusive.
- `ingest`, `rebuild` and `sync` always require a database; `--no-db` is a usage error for them.
- With persistence enabled, read commands load the bundle from SQLite and do not read Markdown
  sources. `<path>` is still required as the logical bundle root.
- A missing database file is `INVALID_REQUEST` with exit `2`.
- An existing database that does not contain `<path>` is `BUNDLE_NOT_INDEXED` with exit `1`; the
  diagnostic tells the user to run `weave ingest <path>`.
- `ingest` replaces only the rows for `<path>` in one transaction. It never touches other bundles
  in the shared database.
- `rebuild` deletes only that bundle's rows and re-ingests them. It does not drop other bundles.
- `sync` requires an indexed bundle. A missing database is `INVALID_REQUEST`; an unindexed bundle
  is `BUNDLE_NOT_INDEXED`.
- `sync` hashes raw file content with SHA-256, skips unchanged files, and reports added, updated,
  removed and skipped counts.
- Renames are treated as one removal plus one addition; no rename detection.
- Outgoing edges are replaced for updated documents. Incoming edges to deleted documents become
  dangling.
- `sync` uses the mode stored at ingest by default. Explicit `--strict` or `--permissive` overrides
  the mode for the sync and updates the stored mode.
- The resolved blob filter is stored per bundle. `ingest --assets` (or `--asset-types`) resolves and
  stores it; `rebuild` and `sync` reuse it when the flags are absent. `--no-assets` clears it and
  removes the bundle's blob rows on the next run.
- `--watch` belongs to [Watch Mode](watch-mode.md) and is not part of this slice.
- Source bundles are never modified.
- The `~/.weave` directory is created with mode `0700` when the database is first written.

### 5.2 Reports

`ingest` and `rebuild` emit:

```json
{
  "db": "/home/user/.weave/index.db",
  "bundle": "/notes",
  "mode": "strict",
  "documents": 42,
  "edges": 51,
  "synthetic": 0,
  "warnings": 0,
  "errors": 0
}
```

`sync` will emit:

```json
{
  "db": "/home/user/.weave/index.db",
  "bundle": "/notes",
  "mode": "strict",
  "documents": 42,
  "added": 0,
  "updated": 1,
  "removed": 0,
  "skipped": 41,
  "warnings": 0,
  "errors": 0
}
```

Exit codes:

- `0` — command completed.
- `1` — the bundle could not be indexed or is not indexed; details are in the report or diagnostics.
- `2` — usage, invalid root, missing database or unsupported schema version.
- `3` — permission denied.

### 5.3 Package API

`storage/sqlite` exposes:

```go
type Store struct { /* ... */ }

type IngestOptions struct {
    Mode string // strict | permissive
}

func Open(path string) (*Store, error)
func (s *Store) Ingest(ctx context.Context, bundle *contractv1.Bundle, options IngestOptions) (IngestReport, error)
func (s *Store) Rebuild(ctx context.Context, bundle *contractv1.Bundle, options IngestOptions) (IngestReport, error)
func (s *Store) HasBundle(ctx context.Context, bundleRoot string) (bool, error)
func (s *Store) LoadBundle(ctx context.Context, bundleRoot string) (*contractv1.Bundle, error)
func (s *Store) Sync(ctx context.Context, root string, options SyncOptions) (SyncReport, error)
func (s *Store) Close() error
```

- `Open` verifies `PRAGMA user_version` and configures WAL and foreign keys.
- `Ingest` and `Rebuild` run in one transaction scoped to `bundle.Root`.
- `HasBundle` checks whether a bundle is present before a database-backed read.
- `LoadBundle` reconstructs a `contractv1.Bundle` for the given root without reading source files.
- `Sync` lands with the incremental-sync slice.

### 5.4 Schema Version

- The current schema is `PRAGMA user_version = 7`.
- Older databases migrate automatically through each migration step.
- A binary refuses to open a database with a newer `user_version` and exits `2` with
  `INVALID_REQUEST`.
- Schema migrations are additive and core-owned; extensions never run DDL.

### 5.5 Query Parity

For the same bundle, database-backed reads return the same envelopes and payloads as in-memory
reads. Graph, search, navigation, audit, relate and explain build their in-memory views from the
loaded bundle; they must not read Markdown sources when persistence is enabled. `LoadBundle`
recomputes link resolution against the stored concept IDs so deleted targets become dangling
without rewriting unchanged source documents.

### 5.6 Acceptance Criteria

- `weave ingest` creates `~/.weave/index.db` by default and reports document and edge counts.
- Repeated `ingest` is idempotent for the same bundle.
- A read command with no `--db` works after the source Markdown files are removed.
- `--no-db` restores transient in-memory behavior.
- Two bundles can be ingested into the same database without overwriting each other.
- A read for an unindexed bundle fails with `BUNDLE_NOT_INDEXED` and exit `1`.
- Missing databases and unsupported schema versions fail with exit `2`.
- `ingest` never writes into the source bundle.
- Incremental sync is covered by its own slice below.

### 5.7 Incremental Sync Acceptance

- A second `sync` with no file changes reports every document as skipped.
- Touching a file without changing its content still reports it as skipped.
- Changing content reports exactly one update and updates stored concepts and search results.
- Adding a file reports exactly one addition.
- Removing a file reports exactly one removal.
- Renaming a file reports one addition and one removal.
- Deleting a link target leaves the source concept's link dangling and audit reports `BROKEN_LINK`.
- `sync` refuses to run on an unindexed bundle or a missing database.
- `sync --no-db` is a usage error.
- `sync` preserves the stored ingest mode unless explicitly overridden.

## Related Documents

- [Compression](compression.md)
- [Permissive Ingestion](permissive-ingestion.md)
- [Watch Mode](watch-mode.md)
- [BM25 Ranking](bm25-ranking.md)
- [Privacy & Extensions](../architecture/privacy-and-extensions.md)
- [Keyword + Fuzzy Search](keyword-fuzzy-search.md)
- [MCP Server](mcp-server.md)
- [ROADMAP](../ROADMAP.md)
