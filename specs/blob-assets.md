---
type: specification
title: "Generic Blob Assets Specification"
description: "Core-owned opaque blob documents with content_kind, media_type, versioned content_metadata and generic retrieval."
tags:
  - "specification"
  - "blobs"
  - "assets"
  - "storage"
  - "extensions"
  - "v1.1"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-03T00:00:00Z"
status: draft
---

# Specification: Generic Blob Assets

## 1. Overview

Weave stores Markdown documents and opaque blob documents in one document model. A blob document has
a title, description, keywords and one primary blob. Core does not interpret the blob; an extension
supplies searchable text and kind-specific attributes.

An image is the first blob consumer, but core contains no image logic. Video, audio, PDF and future
formats use the same path by declaring different media types.

## 2. Non-Goals

- Native parsing, rendering, OCR, transcription, MIME-specific validation or transcoding.
- Multiple primary blobs per document in the first slice.
- Automatic ingestion of every non-Markdown file in a bundle.
- Extension-created tables or direct database access.
- Semantic/vector search; that is [Embeddings](embeddings.md).
- Encrypted export of opaque blob bytes in the first slice.

## 3. Data Model

### 3.1 Document additions

Schema version 7 adds:

```sql
content_kind TEXT NOT NULL DEFAULT 'document', -- document | blob
media_type TEXT NOT NULL DEFAULT 'text/markdown',
content_metadata TEXT NOT NULL DEFAULT '{}'
```

- Existing rows migrate to `content_kind='document'` and `media_type='text/markdown'`.
- Blob rows use `content_kind='blob'`.
- `media_type` is a lowercase MIME type without parameters.
- `body_compressed` stores the primary blob bytes.
- `body_codec` is the per-row compression algorithm: `none`, `zstd` or `lz4`.
- `content_hash` is SHA-256 over the original blob bytes, not the compressed bytes.
- `doc_type` may carry an extension-provided label (`Image`, `Video`, `PDF`); core never branches on
  it.

### 3.2 `content_metadata` envelope

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

| Field | Required | Rules |
| --- | --- | --- |
| `v` | yes | integer; `1` in this slice |
| `text` | no | UTF-8 string, at most 1 MiB |
| `text_source` | no | 1–64 bytes; opaque label (`ocr`, `transcript`, `pdf-text`, ...) |
| `attributes` | no | JSON object, at most 256 KiB; opaque keys and values |

- Total serialized `content_metadata` is limited to 2 MiB.
- Core validates the envelope and size; unknown attributes are preserved.
- Core does not interpret `text_source` or any attribute key.
- Invalid metadata fails the enrichment with a warning; the document remains with empty metadata.
- Core never writes blob bytes into `content_metadata`.

### 3.3 Searchable text

- FTS `body` is populated from `content_metadata.text`, never from `body_compressed`.
- A blob with no text remains searchable by title, description and keywords.
- `weave search` snippets come from the extracted text.
- `weave explain` reports the FTS field as `body`; the spec does not add a media-specific field.

### 3.4 Per-row compression

- Compression is recorded per document row in `body_codec`; there is no bundle-wide or media-wide
  assumption.
- Different rows in the same bundle may use different codecs.
- `none` is the default for already-compressed media such as JPEG and PNG.
- `zstd` or `lz4` may be used for text-like blobs or formats where compression reduces size.
- `--codec` is a preference for new writes, not a global guarantee; the stored `body_codec` is
  authoritative.
- If the requested codec does not reduce size, core stores `none` and records `none`.
- `body_codec` is core-owned; extensions cannot set or override it.
- `show --out`, MCP blob reads and export decode using the stored codec.
- `show --json` reports `body_codec` and the original and stored sizes.
- `content_metadata` is plain JSON and is not compressed by the body codec; it is separately
  size-limited.

## 4. Discovery and Ingestion

### 4.1 Explicit asset types

```sh
weave ingest ~/notes --assets --asset-types image/jpeg,image/png,application/pdf
```

- `--assets` enables blob scanning; without it, images and other non-Markdown files are ignored as
  before.
- `--asset-types` accepts comma-separated MIME types and suffix wildcards such as `image/*`.
- `--assets` without `--asset-types` and without an extension capability exits `2` with
  `ASSET_TYPES_REQUIRED`.
- Blob ingestion requires persistent storage; `--no-db` with `--assets` exits with
  `BLOBS_REQUIRE_DB`.
- Files are matched by detected media type, not by hardcoded core extensions.

### 4.2 Extension capability declaration

An extension may expose a machine-readable description:

```sh
weave-image --describe --json
```

```json
{
  "v": "weave.extension/v1",
  "name": "image",
  "asset_types": ["image/jpeg", "image/png", "image/webp", "image/gif"],
  "requires": [
    {"name": "weave", "min_version": "1.1.0"},
    {"name": "weave-ai", "min_version": "1.1.0"}
  ]
}
```

- When `--asset-types` is absent and `--with-enricher <name>` is set, core uses the extension's
  `asset_types`.
- When both are present, `--asset-types` wins.
- `requires` is informational for core and authoritative for the extension installer/runtime.
- The human `--describe` output remains valid; `--json` is the machine contract.

### 4.3 Media type detection

- Core maps known extensions and magic bytes to a MIME type.
- Unknown binaries use `application/octet-stream`.
- A mismatch between extension and magic bytes is a warning; the detected type is stored.
- Core does not reject a type merely because it does not understand it; the asset filter and
  extension decide.

### 4.4 Limits

| Limit | Value | Behavior |
| --- | --- | --- |
| Single blob | 32 MiB | Warning and skip; `--strict` fails |
| Blob per bundle | 1 GiB | Warning and skip; `--strict` fails |
| `content_metadata` | 2 MiB | Warning; metadata discarded, document kept |
| `text` | 1 MiB | Truncated or rejected by the extension |

Symlinks that escape the bundle and non-regular files are rejected. `.git` and `node_modules` are
ignored, as in the Markdown parser.

### 4.5 Blob document shape

- `id` and `file_path` are the bundle-relative path.
- `title` starts empty; `weave list`/`show` fall back to the filename when empty.
- `description` and `keywords` start empty.
- `content_metadata` starts `{"v":1}`.
- `body_codec` records the actual codec used for that row.
- `doc_type` may be set by the extension.
- The title/description/keywords precedence is defined in §5.

## 5. Enrichment

### 5.1 Request additions

The enrichment request adds an optional `media_type`:

```json
{
  "v": "weave.cli/v1",
  "type": "enrichment_request",
  "media_type": "image/png",
  "doc_id": "photos/cat.png",
  "doc_path": "photos/cat.png",
  "bundle_root": "/home/user/notes",
  "title": "",
  "frontmatter": {"type": "Image"},
  "body": ""
}
```

The extension reads the blob from `bundle_root`/`doc_path`; core does not send blob bytes over IPC.

### 5.2 Response additions

```json
{
  "v": "weave.cli/v1",
  "inferred_title": "Cat on a windowsill",
  "inferred_description": "A tabby cat resting in afternoon sun.",
  "inferred_text": "Adopt me",
  "inferred_text_source": "ocr",
  "inferred_content_metadata": {
    "v": 1,
    "text": "Adopt me",
    "text_source": "ocr",
    "attributes": {"width": 1280, "height": 960}
  },
  "inferred_keywords": ["cat", "windowsill"],
  "custom_metadata": {"provider": "ollama"}
}
```

Rules:

- `inferred_title` fills the title only when it is empty.
- `inferred_description` fills the description only when it is empty.
- `inferred_keywords` appends to declared keywords, de-duplicated case-insensitively.
- `inferred_text` and `inferred_text_source` populate `content_metadata.text` only when no text is
  already present.
- `inferred_content_metadata` merges into `content_metadata`; `v` is core-owned and cannot change.
  Existing `attributes` keys are preserved; new keys are added.
- `custom_metadata` is stored in the existing `enrichments.data_json` table, keyed by extension and
  document.
- Extensions cannot set `content_kind`, `media_type`, `content_hash`, `body_compressed`, `body_codec`
  or `file_path`.
- A failed or malformed response keeps the previous metadata and adds one warning.

### 5.3 Text precedence

- Extension-local OCR/extraction text wins over AI transcription.
- If the document already has `content_metadata.text`, later extensions do not overwrite it unless
  the user explicitly rebuilds with a different enricher.
- If no text exists, the extension may use `inferred_text`.
- If a description is empty and text exists, `weave show`/search may display a short text excerpt;
  the stored description remains empty unless the extension provides one.

## 6. Retrieval

### 6.1 CLI

```sh
weave show ~/notes photos/cat.png --out cat.png --db ~/.weave/index.db
weave show ~/notes photos/cat.png --json --db ~/.weave/index.db
weave list ~/notes --type Image --json
```

- `--out` writes the decoded primary blob; an existing file is rejected unless `--force` is used.
- `--json` returns metadata, `content_kind`, `media_type`, `content_hash`, `body_codec`, original and
  stored sizes, `doc_type` and `content_metadata`; it never embeds bytes.
- Without `--out` and with `--json`, the command succeeds with metadata only.
- Human output prints metadata and the path hint; it never prints binary data.

### 6.2 MCP

- Single source: `weave://blob/<doc-id>`.
- Multi-source: `weave://source/<alias>/blob/<doc-id>`.
- `resources/read` returns MCP `blob` content with the stored MIME type.
- `weave_show` includes the resource URI and metadata; it does not embed bytes.
- Missing blobs return the existing resource-not-found error.

### 6.3 Search and list

- Search hits gain optional `content_kind` and `media_type` fields.
- List results gain the same fields and may filter by `media_type` or `doc_type`.
- No search result contains blob bytes.
- Ranking behavior is unchanged; only the FTS body source changes for blobs.

## 7. Export

- Raw export writes the decoded primary blob at its original bundle-relative path and includes
  `content_kind`, `media_type`, `body_codec`, `content_metadata`, hash and original/stored sizes in
  the manifest.
- Encrypted export excludes blob documents in the first slice and emits one warning per skipped
  blob; opaque blob encryption is deferred.
- A missing blob is an export error; Weave never silently drops a blob.
- `--no-db` cannot export blob documents; they are not in the in-memory index.

## 8. Privacy and Security

- Blob bytes are untrusted; core never executes, renders or interprets them.
- Extensions are trusted code and inherit the process environment.
- Core does not send blobs to AI; only extensions do, under their own configuration.
- EXIF and other metadata are extension-owned attributes; core stores them as opaque JSON.
- Blob size and bundle quotas bound resource use.
- Symlink escape and non-regular files are rejected.
- `content_metadata` is validated before storage; oversized or malformed metadata is discarded with
  a warning.

## 9. Contract Additions

| Type | Field | Meaning |
| --- | --- | --- |
| `OkfConcept` | `content_kind` | `document` or `blob` |
| `OkfConcept` | `media_type` | Stored MIME type |
| `OkfConcept` | `content_metadata` | Versioned JSON envelope |
| `ShowResult` | `content_kind`, `media_type`, `content_metadata`, `body_codec`, `size`, `stored_size`, `content_hash` | Blob metadata |
| `ListResult` | `content_kind`, `media_type`, `doc_type` | Blob listing metadata |
| Search hits | `content_kind`, `media_type` | Optional result fields |
| `EnrichmentRequest` | `media_type` | Optional media type |
| `EnrichmentResponse` | `inferred_title`, `inferred_description`, `inferred_text`, `inferred_text_source`, `inferred_content_metadata` | Additive fields |
| CLI | `--assets`, `--asset-types`, `show --out`, `list --type` | Blob commands |
| MCP | `weave://blob/<id>`, `weave://source/<alias>/blob/<id>` | Blob resources |
| Extension manifest | `weave.extension/v1` with `asset_types`, `requires` | Capability declaration |

All schema changes are additive inside v1. Goldens and schema baselines update in the same change.

## 10. Testing

- Content-kind migration and defaults.
- `content_metadata` envelope validation, size limits and unknown attributes.
- Media type detection, mismatch warnings and unknown binaries.
- Opt-in discovery, `--asset-types`, extension `asset_types`, ignored directories and symlink escape.
- Blob ingest with image, PDF-like and arbitrary binary fixtures; no image-specific core behavior.
- FTS body from `content_metadata.text`; empty text remains searchable by metadata.
- Enrichment precedence: declared wins, inferred fills empty, keywords append, OCR text wins.
- `show --out`, `--force`, JSON metadata and MCP blob bytes.
- Mixed per-row codecs: `none` and `zstd` blobs round-trip in one bundle; codec metadata is exposed.
- Search/list fields, raw export, encrypted-export warning.
- Delete/sync cascade and size quotas.
- Full gate, race suite and calibration unchanged.

Behavior scenarios: [blob-assets.md](https://github.com/prulloac/weave/blob/main/docs/bdd/blob-assets.md).

## 11. Acceptance Criteria

1. A non-Markdown file matching an allowed media type becomes a blob document with a title,
   description, keywords, metadata and one primary blob.
2. Core contains no image, video, audio or PDF branches.
3. `content_metadata.text` is indexed and searchable; the blob is never indexed as text.
4. `show --out` and MCP return the exact original bytes after decoding the stored per-row codec.
5. `--assets` is required; existing bundles without it are unchanged.
6. AI/extension metadata fills empty fields only; declared metadata always wins.
7. Raw export includes blobs; encrypted export warns and excludes them in the first slice.
8. `--no-db` rejects blob ingestion, ingestion failures preserve the previous state, and quotas are
   enforced.

## Related Documents

- [ADR 0004: Generic Blob Assets and Content Metadata](../architecture/adr/0004-generic-blob-assets-and-content-metadata.md)
- [Weave Image Extension](weave-image.md)
- [Embeddings](embeddings.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [Storage & Sync](storage-and-sync.md)
- [Bundle Export](bundle-export.md)
- [MCP Server](mcp-server.md)
- [ROADMAP](../ROADMAP.md)
