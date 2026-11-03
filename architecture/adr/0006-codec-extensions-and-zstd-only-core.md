---
type: Architecture Decision Record
title: "ADR 0006: Codec Extensions and zstd-only Core"
description: "Keeps zstd as the only built-in compression codec for binary blobs, moves LZ4 to a codec extension, and defines raw-byte codec extensions for other algorithms."
tags:
  - "architecture"
  - "adr"
  - "compression"
  - "extensions"
  - "codecs"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-03T00:00:00Z"
status: proposed
---

# ADR 0006: Codec Extensions and zstd-only Core

## Status

Proposed on 2026-11-03. It complements [ADR 0004](0004-generic-blob-assets-and-content-metadata.md)
and the [Compression specification](../../specs/compression.md).

## Context

The corrected storage policy is:

- text-readable content (Markdown, `.txt`, JSON, XML, CSV and source code) is stored uncompressed;
- binary blobs are compressed with zstd by default;
- `--codec` may select another compression algorithm.

The v1.0 core ships both zstd and LZ4. The project now wants only zstd built in and wants other codecs,
including LZ4, to come from the extension mechanism. Codec code must remain out of core, and a
database row must record which codec produced its bytes.

## Decision Summary

| ID | Decision |
| --- | --- |
| D1 | Text-readable content is stored in `body_raw` with NULL `body_codec` |
| D2 | Binary blobs use zstd by default, always |
| D3 | `none` and `zstd` are the only built-in codecs |
| D4 | LZ4 moves to the first-party `weave-codec-lz4` extension |
| D5 | Codec extensions are `weave-codec-<name>` subprocesses with raw byte pipes |
| D6 | `weave codecs list` reports built-in and extension codecs |
| D7 | `body_codec` stores the codec name per compressed row; retrieval requires that codec |
| D8 | Explicit missing codecs fail before write; stored missing codecs fail reads with `CODEC_UNAVAILABLE` |
| D9 | Codec extensions are trusted, bounded and never access the database |
| D10 | Schema v7 migration decompresses existing text rows into `body_raw`; LZ4 rows require the LZ4 codec or a rebuild |

## D1 — Text-readable content is raw

### Decision

Markdown documents and text-readable blobs are stored in `body_raw` with NULL
`body_compressed`/`body_codec`. This includes Markdown, `.txt`, JSON, XML, CSV and source code in any
language.

Classification is generic:

1. `content_kind = document` is always text-readable.
2. A blob with a text MIME type (`text/*`, `application/json`, `application/xml`,
   `application/javascript`, `application/x-yaml`, `application/toml`, ...) is text-readable.
3. Otherwise core samples the bytes: valid UTF-8, no NUL, and a high printable-character ratio means
   text-readable.
4. Everything else is binary.

### Rationale

A language-extension allowlist would age badly. The UTF-8/printable heuristic covers source code,
configuration and future languages without core knowing them.

## D2 — Binary blobs use zstd by default

### Decision

A binary blob is compressed with zstd on write, even if the result is not smaller than the input.
`body_codec = zstd` is recorded.

### Rationale

The policy is explicit and predictable. It also keeps one default codec instead of a codec-selection
heuristic. The cost is that already-compressed images or video may grow; `--codec none` remains an
explicit opt-out and `--codec <extension>` selects another algorithm.

## D3 — Only `none` and `zstd` are built in

### Decision

Core ships `none` and `zstd`. It does not ship LZ4 or any other codec.

### Rationale

The extension mechanism is now the owner of alternative codecs. Keeping LZ4 in core would leave two
codec paths with different lifecycle, discovery and error behavior.

## D4 — LZ4 becomes `weave-codec-lz4`

### Decision

Create a first-party `weave-codec-lz4` extension. `--codec lz4` resolves only when that extension is
installed. Core drops `github.com/pierrec/lz4/v4`.

### Rationale

LZ4 is the smallest real test of the codec extension contract: it is known, useful and already
tested. It proves that a codec can move out of core without changing storage semantics.

## D5 — Raw byte-pipe codec extensions

### Decision

`weave-codec-<name>` is a subprocess with two modes:

```sh
weave-codec-<name> compress
weave-codec-<name> decompress
```

- Raw bytes on stdin, raw bytes on stdout.
- Diagnostics on stderr.
- Exit `0` on success; any other exit is a codec failure.
- `weave-codec-<name> --describe --json` returns the capability manifest.
- One process per operation, like other extensions.

### Rationale

JSON/base64 would inflate large blobs and add unnecessary decoding. A raw pipe is the natural codec
transport.

## D6 — Codec discovery

### Decision

- Codec extensions are discovered in `<bundle>/.weave/bin/` and `$PATH`, with bundle-local precedence.
- `weave codecs list [<path>] --json` returns built-ins and extensions.
- `--codec <name>` resolves `none`/`zstd` first, then `weave-codec-<name>`.
- Text-readable content ignores `--codec` with a warning; text is always raw.

### Rationale

Codec availability must be inspectable. A user who opens a foreign database needs to know which codec
extensions are required.

## D7 — Per-row codec and read dependency

### Decision

`body_codec` stores the codec name for `body_compressed` rows: `none`, `zstd`, `lz4`, or another
extension name. Text rows use `body_raw` and leave `body_codec` NULL. `show --out`, MCP reads and
export must resolve the codec for compressed rows. A missing codec is `CODEC_UNAVAILABLE`, not an
empty body or silent failure.

### Rationale

A database is not portable if a row's codec cannot be identified. The name is part of the storage
contract, not an implementation detail.

## D8 — Error behavior

| Condition | Behavior |
| --- | --- |
| `--codec` unknown or missing | Usage error before write, `CODEC_NOT_FOUND`, exit `2` |
| Codec extension fails/times out | `CODEC_FAILED`/`CODEC_TIMEOUT`, transaction aborts |
| Stored codec missing on read | `CODEC_UNAVAILABLE`, read fails with a clear error |
| Stored codec corrupt/truncated | `BODY_DECODE_FAILED`, no partial plaintext |
| Text row with `--codec` | Warning; stored in `body_raw`, `body_codec` NULL |

## D9 — Security and limits

- Codec extensions are trusted executables with the caller's environment.
- They never receive the database path or write access.
- The runner bounds stdin/stdout/time; codec timeouts default to 30 seconds and are configurable.
- Blob size limits from [ADR 0004](0004-generic-blob-assets-and-content-metadata.md) apply before the
  codec runs.
- Decompression output is bounded to prevent decompression bombs.

## D10 — Migration

Schema v7 migration:

1. Decompress existing text-readable rows into `body_raw`; leave `body_compressed`/`body_codec`
   NULL.
2. Keep existing `zstd` binary rows as `zstd`.
3. Existing LZ4 rows require `weave-codec-lz4`; without it they remain unreadable until the extension
   is installed or the bundle is rebuilt.
4. New binary rows use `zstd` unless `--codec` selects another codec.

## Consequences

- Core drops the LZ4 dependency and the `lz4` built-in.
- A first-party `weave-codec-lz4` repository/extension is required.
- A database with extension-codec rows depends on those codecs; `weave codecs list` and `audit`
  surface missing codecs.
- Text bodies grow because they are no longer compressed. Binary blobs may grow if zstd cannot help.
- Compression spec, storage spec, BDD, roadmap and release notes change.
- Release order: zstd-only core + LZ4 extension before databases containing LZ4 are expected to open.

## Rejected Alternatives

| Alternative | Why rejected |
| --- | --- |
| Keep LZ4 built in | Two built-in codec paths; weakens the extension contract |
| Go plugins for codecs | Platform/CGO burden and incompatible with subprocess isolation |
| JSON/base64 codec IPC | Large overhead and unnecessary encoding |
| Silent fallback to zstd when a codec is missing | User explicitly selected a codec; data format must be deterministic |
| Store codec only in metadata JSON | Decoding must not require interpreting media metadata |
| Compress text with zstd | The corrected policy requires text-readable content raw |

## Related Documents

- [Compression specification](../../specs/compression.md)
- [Codec Extensions specification](../../specs/codec-extensions.md)
- [ADR 0004: Generic Blob Assets and Content Metadata](0004-generic-blob-assets-and-content-metadata.md)
- [Extension Subprocess IPC specification](../../specs/extension-ipc.md)
- [Storage & Sync specification](../../specs/storage-and-sync.md)
- [ROADMAP](../../ROADMAP.md)
