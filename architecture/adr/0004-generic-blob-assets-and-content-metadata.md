---
type: Architecture Decision Record
title: "ADR 0004: Generic Blob Assets and Content Metadata"
description: "Adds generic opaque blob documents to core, with content_kind, media_type, versioned content_metadata and a per-row body codec, leaving media semantics to extensions."
tags:
  - "architecture"
  - "adr"
  - "blobs"
  - "assets"
  - "storage"
  - "extensions"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-03T00:00:00Z"
status: proposed
---

# ADR 0004: Generic Blob Assets and Content Metadata

## Status

Proposed on 2026-11-03. It supersedes the “No native asset ingestion” limitation in the
[ROADMAP](../../ROADMAP.md) and complements [ADR 0005](0005-embeddings-and-cgo-free-vec0-index.md).

## Context

Weave v1.0 ingests Markdown only. The parser walks `.md` files, and a document body is text that is
compressed, indexed and returned by `show`. The extension data API stores opaque bytes, but it binds
them to a Markdown document and stores them in a sidecar store; it deliberately does not create
native documents or replace the document body.

Users need to search and retrieve knowledge from images, and later video, audio, PDF and other
opaque artifacts. A pure `weave-<name>` extension cannot provide that: extensions cannot create
documents, write the database or replace `body_compressed`. Core must gain a generic blob primitive,
but it must not learn image, video, audio or PDF semantics.

## Decision Summary

| ID | Decision |
| --- | --- |
| D1 | Core supports a first-class generic blob document |
| D2 | `content_kind` is `document` or `blob`; `media_type` is an arbitrary MIME label |
| D3 | `content_metadata` is a versioned JSON envelope owned by core |
| D4 | `body_raw` stores text-readable bodies; `body_compressed` stores binary blobs; exactly one is non-null |
| D5 | Blob discovery is opt-in and filtered by media types, not by hardcoded extensions |
| D6 | Media semantics belong to extensions; core never branches on `media_type` |
| D7 | Retrieval is generic: `show --out` and an MCP blob resource |
| D8 | Image is the first consumer through `weave-image`, not a core special case |
| D9 | One primary blob per document in the first slice; derived artifacts are deferred |

## D1 — Generic blob documents

### Decision

A document may represent either Markdown or one opaque blob. Blob documents are stored in the same
`documents` table as Markdown documents and participate in the same lifecycle: ingest, sync, delete,
search metadata, audit and export.

### Rationale

A separate document model would duplicate IDs, sync, graph and search code. The storage shape is
already blob-capable at the SQLite level; the missing pieces are a content kind, a media type and a
generic metadata envelope.

## D2 — Storage kind, not semantic kind

### Decision

- `content_kind` is `document` or `blob`.
- `media_type` is a lowercase MIME type such as `text/markdown`, `image/jpeg`, `video/mp4`,
  `audio/mpeg` or `application/pdf`.
- `doc_type` remains an optional extension-provided label (`Image`, `Video`, `PDF`, ...). Core never
  branches on it.

`content_kind` describes how core stores and retrieves the document. It does not name the media.

### Rationale

If core stores `content_kind = image`, it will eventually grow `if image`, then `if video`, then
`if pdf`. Keeping the storage kind generic forces media behavior into extensions and keeps future
formats additive.

## D3 — `content_metadata` envelope

### Decision

Add a versioned JSON column with this envelope:

```json
{
  "v": 1,
  "text": "Searchable extracted text",
  "text_source": "ocr",
  "attributes": {
    "width": 4032,
    "height": 3024
  }
}
```

- `v` is the envelope version.
- `text` is optional searchable text extracted by an extension.
- `text_source` is an opaque label such as `ocr`, `transcript` or `pdf-text`.
- `attributes` is an opaque object for kind-specific data: EXIF, dimensions, duration, pages, codecs.

Core validates the envelope and the `text`/`attributes` size limits. It preserves unknown
attributes. It does not interpret `text_source` or any attribute key.

### Rationale

New media kinds need new metadata fields. A generic envelope avoids a schema migration for every
image, video or PDF attribute while keeping the searchable text in a known location.

## D4 — Raw and compressed body columns

### Decision

The `documents` table stores exactly one body form per row:

```sql
body_raw TEXT,                    -- text-readable bodies, or NULL
body_compressed BLOB,             -- binary blob bodies, or NULL
body_codec TEXT,                  -- codec for body_compressed, or NULL
CHECK ((body_raw IS NULL) != (body_compressed IS NULL))
CHECK ((body_raw IS NOT NULL AND body_codec IS NULL)
    OR (body_compressed IS NOT NULL AND body_codec IS NOT NULL))
```

- Text-readable content uses `body_raw` and leaves `body_compressed` and `body_codec` NULL:
  Markdown, `.txt`, JSON, XML, CSV and source code. Classification uses `content_kind`, text MIME
  types and a generic UTF-8/printable heuristic; there is no language-extension allowlist.
- Binary blobs use `body_compressed` and leave `body_raw` NULL. `body_codec` is non-null and records
  `zstd`, `none` or an extension codec name such as `lz4`.
- The codec is recorded per compressed row and must not be inferred from the bundle, media type or a
  global CLI default. Different binary rows in the same bundle may use different codecs.
- Binary blobs use `zstd` by default, always, even when zstd output is larger than the input.
- `--codec` overrides the codec for binary blobs only. It can select `zstd`, `none`, or an extension
  codec. Text-readable content ignores `--codec` with a warning and stays raw.
- `none` and `zstd` are the only built-in codecs. LZ4 and other algorithms are
  `weave-codec-<name>` extensions; see [ADR 0006](0006-codec-extensions-and-zstd-only-core.md).
- `content_hash` and `size` are computed over the original bytes, not the stored bytes. A stored size
  may be recorded for diagnostics.
- `body_codec` is core-owned. Extensions cannot choose or override it directly.
- `show --out`, MCP reads and export write `body_raw` directly or decode `body_compressed` using its
  codec. A missing codec extension fails with `CODEC_UNAVAILABLE`, not an empty body.
- FTS `body` is `body_raw` when present; otherwise it is `content_metadata.text` for extracted text
  from a binary blob. Text documents never require JSON parsing to be indexed.
- `content_metadata` is plain JSON and separately size-limited; it is not compressed by the body
  codec. `content_metadata.text` is for extracted text from binary blobs (OCR, transcripts, PDF
  text), not for text-readable bodies.
- A binary blob with no extracted text remains searchable by title, keywords and description.

### Rationale

The two-column model makes the storage policy explicit: text-readable content is directly readable
and indexable, while binary blobs are the only rows with a codec. FTS no longer depends on a JSON
field for Markdown, and binary extraction remains possible through `content_metadata.text`. SQLite
CHECK constraints prevent both forms being present or absent.

### Consequences

Retrieval and export must branch on which body column is non-null. A global `--codec` flag is only a
preference; the stored actual codec is authoritative for compressed rows. `weave show --json` exposes
the body form and codec so operators can inspect a mixed bundle. A database containing an
extension-codec row depends on that codec extension being installed; `weave codecs list` and
`weave audit` surface missing codecs.

## D5 — Generic discovery

### Decision

Blob ingestion is opt-in and media-type driven:

- `weave ingest <path> --assets` enables blob scanning.
- `--asset-types image/jpeg,image/png,application/pdf` filters files.
- An extension may declare its supported `asset_types` through a machine-readable `--describe`
  capability; core uses those types when `--asset-types` is absent.
- Core never hardcodes `.jpg`, `.mp4` or `.pdf`.

The first slice scans regular files in the selected bundle, skips ignored directories, and rejects
symlinks that escape the bundle. Blob ingestion requires persistent storage.

### Rationale

A bundle can contain logos, fixtures, PDFs or media that the user did not ask to ingest. Automatic
scanner-wide blob ingestion would change existing behavior and indexes.

## D6 — Extension-owned semantics

### Decision

`weave-image`, `weave-video`, `weave-pdf` and future extensions own:

- media-type validation;
- text extraction and `text_source`;
- kind-specific `attributes`;
- AI/OCR/transcode calls;
- title, description and keyword generation.

Core only persists the result. Extensions never create tables, write the database or set
`content_kind`, `media_type`, `content_hash`, `body_raw`, `body_compressed` or `body_codec`.

### Rationale

The alternative is a core that understands every format. That is a permanently growing parser and a
security surface Weave does not need.

## D7 — Generic retrieval

### Decision

- `weave show <id> --out <file>` writes `body_raw` directly or decodes `body_compressed`; `--force`
  replaces an existing file.
- `weave show --json` returns metadata, `content_kind`, `media_type`, body form, `body_codec`, hash,
  size and `content_metadata`; never bytes.
- MCP exposes `weave://blob/<doc-id>` and, with sources, `weave://source/<alias>/blob/<doc-id>` as
  blob content with the stored MIME type.
- Search and list results include `content_kind` and `media_type`; they do not embed bytes.

### Rationale

Terminal JSON cannot safely carry binary data. A file output and MCP blob are the right transport
for opaque content, and they work for every media type.

## D8 — Image first, not image-specific

### Decision

`weave-image` is the first blob consumer. It declares image media types, performs OCR/EXIF/vision
enrichment and returns the generic envelope. Subsequent video, audio and PDF extensions reuse the
same core path.

### Rationale

The image use case validates the design without granting images a privileged place in core.

## D9 — One primary blob

### Decision

A document has one primary blob. Additional derived artifacts (video thumbnails, PDF page images,
audio waveforms) are deferred; they can use extension data or a future document-assets table.

### Rationale

The first slice stays small. Multiple blobs per document need ordering, roles and export semantics
that are not required to prove the model.

## Consequences

- Schema version 7 adds `content_kind`, `media_type` and `content_metadata`, and splits
  `body_compressed` into nullable `body_raw` and `body_compressed` columns with `body_codec` for
  compressed rows only. Existing text rows migrate to `body_raw`; existing rows default to
  `content_kind=document` and `media_type=text/markdown`.
- The parser gains a generic asset scanner, not image parsing.
- The extension IPC gains `media_type` on enrichment requests and generic metadata fields on
  responses.
- `show`, `list`, search hits, MCP and export gain additive content-kind fields.
- Blob ingestion requires persistence; `--no-db` cannot retrieve blobs.
- Encrypted export of blobs and per-media size limits need explicit specification. Raw export copies
  blobs; encrypted export policy is defined in the blob-assets spec.
- The previous “no native asset ingestion” limitation is retired; “no native media interpretation”
  replaces it.

## Rejected Alternatives

| Alternative | Why rejected |
| --- | --- |
| Extension data only | Binds blobs to Markdown sidecars; no native blob document, no body replacement |
| Image-specific core model | Creates a new special case for every future media type |
| Separate asset table per media type | Duplicates document lifecycle and search metadata |
| Ingest every non-Markdown file | Changes existing bundles and can ingest unrelated fixtures |
| Store extracted text in the blob | Corrupts the blob and prevents original retrieval |
| Extension-run schema changes | Breaks migrations, transactions, export and multi-process safety |

## Related Documents

- [Generic Blob Assets specification](../../specs/blob-assets.md)
- [Weave Image Extension specification](../../specs/weave-image.md)
- [Compression specification](../../specs/compression.md)
- [Codec Extensions specification](../../specs/codec-extensions.md)
- [Embeddings specification](../../specs/embeddings.md)
- [ADR 0005: Embeddings and CGo-Free vec0 Index](0005-embeddings-and-cgo-free-vec0-index.md)
- [ADR 0006: Codec Extensions and zstd-only Core](0006-codec-extensions-and-zstd-only-core.md)
- [Extension Subprocess IPC specification](../../specs/extension-ipc.md)
- [Storage & Sync specification](../../specs/storage-and-sync.md)
- [ROADMAP](../../ROADMAP.md)
