---
type: specification
title: "Body Compression Specification"
description: "Text-readable bodies stay raw; binary blobs use zstd by default; other codecs are weave-codec-<name> extensions."
tags:
  - "specification"
  - "compression"
  - "storage"
  - "codecs"
  - "v1.1"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-10-28T00:00:00Z"
status: draft
---

# Specification: Body Compression

## 1. Overview

Body compression is a per-row storage contract. Text-readable content is stored raw; binary blobs
use zstd by default. Other compression algorithms are provided by `weave-codec-<name>` extensions.
The stored `body_codec` is authoritative and is read with every body.

This spec owns the body compression policy. The codec extension protocol is owned by
[Codec Extensions](codec-extensions.md).

## 2. Goals and Non-Goals

### Goals

- Store text-readable content without compression, so stored bodies remain directly readable.
- Compress binary blobs with zstd by default.
- Record the exact codec per row.
- Make alternative codecs extension-provided and independently installable.
- Never corrupt, truncate or silently drop content.

### Non-Goals

- Compressing Markdown, source code or other text-readable content.
- Built-in LZ4 or other codecs beyond `none` and `zstd`.
- Query-time codec selection.
- Lossy compression or transcoding.
- Codec extensions writing the database.
- Posting compression; SQLite FTS5 owns its storage format.
- Encrypted binary blob export in the first slice.

## 3. Classification

### 3.1 Text-readable

The following are stored raw with `body_codec = 'none'`:

- every `content_kind = 'document'` (Markdown);
- blobs whose media type is text-like: `text/*`, `application/json`, `application/xml`,
  `application/javascript`, `application/x-yaml`, `application/toml`, and similar application types;
- blobs that pass the generic text heuristic: valid UTF-8, no NUL, high printable-character ratio.

The heuristic covers source code, configuration and future languages without an extension allowlist.
A PDF, archive, image, audio or video file remains binary because of its header/control bytes.

### 3.2 Binary

Everything else is a binary blob. Binary blobs use `body_codec = 'zstd'` by default, always, even
when zstd output is larger than the input.

## 4. Schema

The `documents` table already has `body_compressed` and `body_codec`; no new column is added:

```sql
body_compressed BLOB NOT NULL,
body_codec TEXT NOT NULL DEFAULT 'none'
```

- `body_compressed` holds the encoded bytes; for text rows it holds raw UTF-8 bytes and the name is
  historical.
- `body_codec` is `none`, `zstd`, `lz4`, or another codec extension name.
- The codec is per row; no bundle-wide or media-wide assumption is valid.
- `content_hash` and `size` are over the original bytes.

## 5. Selection Rules

| Content | Default | `--codec` |
| --- | --- | --- |
| Markdown / document | `none` | Ignored with a warning |
| Text-readable blob | `none` | Ignored with a warning |
| Binary blob | `zstd` | `zstd`, `none`, or `lz4`/extension name |
| Encrypted text body | `none` | Ignored; ciphertext is never double-compressed |

- `--codec none` explicitly stores binary bytes raw.
- `--codec zstd` is the built-in default.
- `--codec lz4` requires `weave-codec-lz4`.
- Any other codec requires a matching `weave-codec-<name>` extension.
- An explicit missing codec fails before writing with `CODEC_NOT_FOUND`, exit `2`; there is no silent
  fallback.
- Text-readable content always uses `none`; a `--codec` request adds one warning.

## 6. Write Path

```sh
weave ingest <path> [--codec zstd|none|lz4|<name>] [--strict|--permissive] --json
weave rebuild <path> [--codec zstd|none|lz4|<name>] [--strict|--permissive] --json
weave sync <path> [--codec zstd|none|lz4|<name>] [--strict|--permissive] --json
```

- `ingest` and `rebuild` apply the codec to binary blobs; text rows are always `none`.
- `sync` writes new binary blobs with zstd. Updated binary rows keep their stored codec unless
  `--codec` is provided. Text rows always remain `none`.
- `rebuild --codec` re-encodes binary rows and leaves text rows raw.
- Compression runs inside the write transaction; a codec failure aborts it.
- Text rows are never compressed, including when `--codec` is supplied.

## 7. Read Path

- `LoadBundle`, `show`, search, snippets, `explain`, list and MCP decode using `body_codec`.
- `show --out` and MCP blob reads return the exact original bytes.
- A missing codec extension fails with `CODEC_UNAVAILABLE`; it is not treated as an empty body.
- A corrupt or truncated body fails with `BODY_DECODE_FAILED`; no partial plaintext is returned.
- Text rows with `none` are read directly.
- Queries never crash on corrupt bodies; the error is surfaced as a warning or command error according
  to the command.

## 8. Migration

Schema v7 migration:

1. Decompress existing text-readable Markdown rows to `none`.
2. Keep existing zstd binary rows as `zstd`.
3. Existing LZ4 rows require `weave-codec-lz4`; without it they remain unreadable until the extension
   is installed or the bundle is rebuilt.
4. New binary rows use zstd unless `--codec` selects another codec.

The migration is core-owned. Extensions never run migrations.

## 9. Privacy

- Encrypted whole-body text documents always use `none`; ciphertext is not double-compressed.
- Tokenized, hashed and mixed text bodies are text-readable and therefore stored raw.
- Binary blob encryption is out of scope for the first slice.
- Codec extensions never receive key material or the database path.

## 10. Validation and Errors

| Condition | Behavior |
| --- | --- |
| `--codec` unknown/missing | `CODEC_NOT_FOUND`, exit `2`, before write |
| Codec extension failure | `CODEC_FAILED`, transaction aborts, exit `1` |
| Codec timeout | `CODEC_TIMEOUT`, transaction aborts |
| Stored codec missing on read | `CODEC_UNAVAILABLE`, read fails |
| Corrupt/truncated body | `BODY_DECODE_FAILED`, no partial plaintext |
| Text row with `--codec` | Stored `none`, one warning |
| Binary blob with zstd | Stored `zstd`, even if larger |
| Encrypted text | Stored `none` |

## 11. Testing

- Markdown, `.txt`, JSON, XML, CSV and source-code fixtures store `none` and round-trip unchanged.
- Binary PDF/archive fixtures store `zstd`; `show --out` round-trips.
- Text with `--codec zstd` stays `none` and emits a warning.
- Binary `--codec none` stores raw; `--codec zstd` stores zstd.
- `--codec lz4` fails with `CODEC_NOT_FOUND` without `weave-codec-lz4`; succeeds with it.
- Custom codec extension round-trip, failure, timeout, missing codec.
- Mixed codecs in one bundle; per-row codec is reported by `show --json`.
- Missing stored codec fails with `CODEC_UNAVAILABLE`.
- Corrupt/truncated body fails with `BODY_DECODE_FAILED`.
- Migration decompresses text rows; LZ4 rows behave as specified.
- `rebuild --codec` and `sync` preserve/change codecs as specified.
- Search, explain and calibration are unchanged.

Behavior scenarios: [compression.md](https://github.com/prulloac/weave/blob/main/docs/bdd/compression.md)
and [codec-extensions.md](https://github.com/prulloac/weave/blob/main/docs/bdd/codec-extensions.md).

## 12. Acceptance Criteria

1. Text-readable content is stored raw with `none`.
2. Binary blobs are stored with `zstd` by default.
3. `body_codec` is per row and is used by every read.
4. LZ4 and other codecs are extension-provided; core has only `none` and `zstd`.
5. Explicit missing codecs fail before write; stored missing codecs fail reads with
   `CODEC_UNAVAILABLE`.
6. Corrupt bodies never crash queries and never emit partial plaintext.
7. Compression is deterministic for a given codec and version.
8. `rebuild --codec` and `sync` handle codecs as specified; text stays raw.
9. Full verification gate and calibration remain green.

## Related Documents

- [Codec Extensions](codec-extensions.md)
- [ADR 0006: Codec Extensions and zstd-only Core](../architecture/adr/0006-codec-extensions-and-zstd-only-core.md)
- [Storage & Sync](storage-and-sync.md)
- [Generic Blob Assets](blob-assets.md)
- [Privacy Directives](privacy-directives.md)
- [ROADMAP](../ROADMAP.md)
