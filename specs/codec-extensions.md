---
type: specification
title: "Codec Extensions Specification"
description: "zstd-only core compression with raw-byte weave-codec-<name> extensions for LZ4 and other algorithms."
tags:
  - "specification"
  - "compression"
  - "codecs"
  - "extensions"
  - "v1.1"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-03T00:00:00Z"
status: draft
---

# Specification: Codec Extensions

## 1. Overview

Core ships two codecs: `none` and `zstd`. Any other compression algorithm is provided by a
`weave-codec-<name>` extension. This spec defines discovery, the capability manifest, the raw-byte
transport, selection, error behavior and the first-party LZ4 extension.

## 2. Non-Goals

- Compression of text-readable content; text is always raw.
- Built-in LZ4 or other codecs.
- Long-lived codec daemons.
- Codec extensions writing the database or bundle.
- Encrypted blob compression in the first slice.
- Lossy compression, transcoding or encryption inside a codec.

## 3. Naming and Discovery

- Names match `[a-z0-9][a-z0-9-]*`; the binary is `weave-codec-<name>`.
- Resolution order:
  1. `<bundle-root>/.weave/bin/weave-codec-<name>`
  2. `$PATH` entries named `weave-codec-<name>`
- Bundle-local wins over `$PATH`.
- Non-executable files are skipped.
- Built-ins `none` and `zstd` are always available and cannot be shadowed by an extension.
- First-party extension: `weave-codec-lz4` provides `lz4`.
- `none` is a passthrough codec: `can_compress` is false because it never reduces size, but
  `--codec none` is a valid explicit selection and decompression is a no-op.

`weave codecs list [<path>] --json` returns:

```json
{
  "codecs": [
    {"name": "none", "source": "builtin", "can_compress": false, "can_decompress": true},
    {"name": "zstd", "source": "builtin", "can_compress": true, "can_decompress": true},
    {"name": "lz4", "source": "path", "path": "/usr/local/bin/weave-codec-lz4", "can_compress": true, "can_decompress": true}
  ]
}
```

## 4. Capability Manifest

```sh
weave-codec-lz4 --describe --json
```

```json
{
  "v": "weave.extension/v1",
  "name": "lz4",
  "kind": "codec",
  "version": "1.0.0",
  "directions": ["compress", "decompress"],
  "frame": true
}
```

- `name` must match the binary suffix.
- `directions` is a subset of `compress` and `decompress`.
- `frame` indicates the codec output is self-describing; core still stores `body_codec`.
- A malformed manifest makes the codec unavailable with `CODEC_PROTOCOL`.
- `--describe` without `--json` remains human-readable.

## 5. Raw Transport

```sh
weave-codec-<name> compress
weave-codec-<name> decompress
```

- Raw bytes are read from stdin and written to stdout.
- No JSON envelope, base64 or framing added by core.
- Diagnostics go to stderr; stdout must contain only codec bytes.
- Exit `0` on success; any other exit fails the operation.
- One process per operation.
- The runner uses the global extension timeout: 5 seconds by default, configurable with `--timeout`
  (see [Extension IPC](extension-ipc.md)).
- Input is bounded by the blob size limit; decompression output is bounded to prevent bombs.
- A codec must be deterministic for the same input, options and version.

## 6. Selection

### 6.1 Text-readable content

- `content_kind=document` and text-readable blobs always use `body_raw`.
- `body_compressed` and `body_codec` are NULL for text-readable content.
- `--codec` is ignored for text-readable content with one warning.
- No codec extension is invoked for text-readable content.

### 6.2 Binary blobs

- Default codec: `zstd`.
- `--codec zstd` uses built-in zstd.
- `--codec none` is an explicit opt-out and stores raw bytes.
- `--codec <name>` resolves to `weave-codec-<name>`.
- If the codec is missing, the command fails before writing with `CODEC_NOT_FOUND`, exit `2`.
- If the codec fails or times out, the transaction aborts with `CODEC_FAILED` or `CODEC_TIMEOUT`,
  exit `1`.
- No silent fallback to zstd.

### 6.3 Existing rows

- `sync` preserves a row's codec unless `--codec` is provided.
- `rebuild --codec` re-encodes binary rows.
- Text rows always use `body_raw` with NULL `body_codec` on rebuild.
- An LZ4 binary row requires `weave-codec-lz4` for reads until rebuilt.

## 7. Storage and Read Path

- `body_codec` stores `none`, `zstd`, `lz4` or another extension name for `body_compressed` rows.
- Text rows use `body_raw` and leave `body_codec` NULL; `body_compressed` is NULL.
- `show --out`, MCP blob reads and export resolve the codec before decoding.
- A missing stored codec is `CODEC_UNAVAILABLE` and the read fails; it is not treated as an empty
  body.
- Corrupt codec output is `BODY_DECODE_FAILED`; no partial plaintext is returned.
- `weave audit` reports `CODEC_MISSING` for stored codecs that are not installed.

## 8. LZ4 Extension

- `weave-codec-lz4` is a first-party extension implementing `compress` and `decompress`.
- Core no longer depends on `github.com/pierrec/lz4/v4`.
- `--codec lz4` fails with `CODEC_NOT_FOUND` when the extension is absent.
- Release order: publish `weave-codec-lz4` before releasing a core that requires it for existing LZ4
  databases.

## 9. Security

- Codec extensions are trusted executables and inherit the process environment.
- They never receive the database path, bundle writes or key material.
- They are not sandboxed or signature-verified.
- The runner bounds input, output, stderr and time.
- A decompression bomb is a `CODEC_FAILED` with no partial output.
- Codec extensions must not log input bytes.

## 10. Errors

| Code | Meaning |
| --- | --- |
| `CODEC_NOT_FOUND` | Explicit `--codec` has no built-in or extension |
| `CODEC_UNAVAILABLE` | Stored `body_codec` cannot be resolved on read |
| `CODEC_FAILED` | Extension exited non-zero or produced invalid output |
| `CODEC_TIMEOUT` | Extension exceeded the timeout |
| `CODEC_PROTOCOL` | Invalid manifest or stdout/stderr protocol |
| `BODY_DECODE_FAILED` | Stored bytes cannot be decoded (corrupt/truncated) |

## 11. Testing

- Discovery order, built-in shadowing, invalid names.
- Manifest validation and `weave codecs list --json`.
- Raw compress/decompress round-trip for a custom codec.
- LZ4 extension round-trip; core without LZ4 fails `--codec lz4` with `CODEC_NOT_FOUND`.
- Text content stays in `body_raw` with NULL `body_codec`, with or without `--codec`.
- Binary default is zstd; zstd output larger than input is still stored.
- Missing stored codec fails reads with `CODEC_UNAVAILABLE`.
- Corrupt/truncated output fails with `BODY_DECODE_FAILED`.
- Timeout, non-zero exit, invalid manifest and oversized output.
- Mixed codecs in one bundle; `show --out` round-trips each.
- `rebuild --codec` and `sync` preserve/change codecs as specified.
- Migration decompresses text rows; missing LZ4 aborts without changing `user_version`.
- Full gate, race suite, six static targets.

Behavior scenarios: [codec-extensions.md](https://github.com/prulloac/weave/blob/main/docs/bdd/codec-extensions.md).
Body compression scenarios live in [compression.md](https://github.com/prulloac/weave/blob/main/docs/bdd/compression.md).

## 12. Acceptance Criteria

1. Core ships only `none` and `zstd`; LZ4 is an extension.
2. Text-readable content is stored in `body_raw` with NULL `body_codec`.
3. Binary blobs default to zstd, even when the result is larger.
4. `--codec lz4` uses `weave-codec-lz4`; missing codec fails before write.
5. `body_codec` is per compressed row and retrieval resolves the exact codec.
6. Missing stored codecs fail with `CODEC_UNAVAILABLE`, not empty data.
7. Codec extensions use raw stdin/stdout and never access the database.
8. Mixed codecs round-trip and `weave codecs list` is accurate.

## Related Documents

- [ADR 0006: Codec Extensions and zstd-only Core](../architecture/adr/0006-codec-extensions-and-zstd-only-core.md)
- [Compression](compression.md)
- [Generic Blob Assets](blob-assets.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [Storage & Sync](storage-and-sync.md)
- [ROADMAP](../ROADMAP.md)
