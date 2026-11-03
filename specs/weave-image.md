---
type: specification
title: "Weave Image Extension Specification"
description: "First generic blob consumer: image OCR, EXIF, dimensions, weave-ai vision metadata and a user-level installer dependency on weave-ai."
tags:
  - "specification"
  - "extension"
  - "image"
  - "ocr"
  - "vision"
  - "v1.1"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-11-03T00:00:00Z"
status: draft
---

# Specification: Weave Image Extension

## 1. Overview

`weave-image` is the first consumer of Weave’s generic blob assets. It enriches image documents with
OCR text, EXIF, dimensions, title, description and keywords. It treats images as opaque blobs; core
does not know what an image is.

`weave-image` depends on `weave-ai` for vision and is installed as a standalone `weave-<name>`
extension. It never writes the database and never creates tables.

## 2. Scope

In scope:

- image media types: `image/jpeg`, `image/png`, `image/webp`, `image/gif`;
- local OCR when available;
- EXIF extraction and dimensions;
- vision-based title, description, keywords and text fallback;
- metadata precedence and failure fallback;
- installer/runtime dependency on `weave-ai >= 1.1.0` and `weave >= 1.1.0`.

Non-goals:

- image editing, thumbnails, OCR training, object detection or face recognition;
- raw image embeddings in the first slice (the embedding schema supports them later);
- core image parsing or image-specific branches;
- a separate database, cache or sidecar store;
- encrypted blob export.

## 3. Capability Contract

`weave-image --describe --json` returns:

```json
{
  "v": "weave.extension/v1",
  "name": "image",
  "asset_types": ["image/jpeg", "image/png", "image/webp", "image/gif"],
  "requires": [
    {"name": "weave", "min_version": "1.1.0"},
    {"name": "weave-ai", "min_version": "1.1.0"}
  ],
  "capabilities": ["vision", "ocr", "exif"]
}
```

- Core uses `asset_types` when `--asset-types` is absent.
- `requires` is informational for core and authoritative for the installer and runtime check.
- The human `--describe` output remains available and includes provider/vision information without
  secrets.

## 4. Ingest Flow

1. Core discovers a file whose media type matches `asset_types`.
2. Core creates a blob document and invokes `weave-image` as the enricher.
3. `weave-image` reads the image from `bundle_root`/`doc_path`.
4. It verifies the media type and magic bytes.
5. It tries local OCR, then extracts EXIF and dimensions.
6. It calls `weave-ai` with the image, OCR text and EXIF context.
7. It returns `inferred_title`, `inferred_description`, `inferred_text`,
   `inferred_text_source`, `inferred_content_metadata`, `inferred_keywords` and
   `custom_metadata`.
8. Core persists metadata and the image blob in the same transaction.

The extension does not receive or send the blob through core IPC; it reads the source file directly.

## 5. OCR

- If a local OCR backend is available (Tesseract), it runs first.
- If local OCR is unavailable or returns no text, `weave-ai` is asked to transcribe.
- Local OCR text takes precedence over AI transcription.
- `text_source` is `ocr` for local OCR and `vision` for AI transcription.
- OCR language is configurable with `--ocr-lang`; default `eng`.
- OCR text is stored in `content_metadata.text` and indexed as the FTS body.
- If no OCR text exists, the document remains searchable by title, description and keywords.
- A description is always AI-generated; if AI returns none and OCR text exists, a short OCR excerpt
  may be used as the display fallback, but the stored description stays empty.

## 6. EXIF and Dimensions

- Extract EXIF for JPEG/TIFF and available metadata for PNG/WebP/GIF.
- Store the normalized object in `content_metadata.attributes.exif`.
- Store `width` and `height` in `content_metadata.attributes`.
- Always send EXIF to `weave-ai` alongside the image, as context for title/description/keywords.
- EXIF may contain GPS, camera and timestamp data. The provider is selected by `weave-ai` config; no
  separate image consent flag is added.
- `weave-image --describe` must state that EXIF is sent to the configured AI provider.
- Store the original image bytes; do not re-encode for storage.
- AI payload preparation may strip nothing; EXIF is intentionally included.

## 7. AI Vision

### 7.1 Extension-to-extension request

`weave-image` invokes `weave-ai` with:

```json
{
  "v": "weave.cli/v1",
  "type": "vision_request",
  "media_type": "image/jpeg",
  "image": "<base64>",
  "text": "OCR text, if any",
  "exif": {"Make": "Apple", "Model": "iPhone 15"},
  "prompt": "Return JSON with title, description, keywords and optional text."
}
```

`weave-ai` returns:

```json
{
  "v": "weave.cli/v1",
  "title": "Cat on a windowsill",
  "description": "A tabby cat resting in afternoon sun.",
  "text": "Adopt me",
  "keywords": ["cat", "windowsill", "sunlight"]
}
```

- `weave-image` validates the response shape and size.
- `weave-ai` must use a vision-capable model; `weave-ai --describe` reports `vision: true`.
- Provider payloads are defined in the AI extension spec.
- Image size sent to AI is capped at 20 MiB after base64 decoding; larger images fail with
  `IMAGE_TOO_LARGE`.
- The runner timeout applies; document `weave ingest --timeout 60s` for slow local vision models.

### 7.2 Precedence

- Declared title/description wins.
- AI title/description fills empty fields only.
- AI keywords append to declared keywords.
- OCR text wins over AI transcription.
- EXIF is always stored; AI may use it but cannot replace it.
- `custom_metadata` stores provider, model, source (`ocr`, `vision`, `mixed`), confidence and raw
  timing; it is persisted in `enrichments.data_json`.

### 7.3 Failure fallback

| Condition | Behavior |
| --- | --- |
| `weave-ai` missing or too old | Warning; image still ingested with OCR/EXIF/dimensions |
| Provider timeout/non-2xx | Warning; keep OCR/EXIF/dimensions |
| Malformed AI response | Warning; keep valid local metadata |
| OCR backend missing | Use `weave-ai` transcription |
| OCR and AI text empty | Blob remains searchable by metadata |
| Unsupported image format | Skip with warning; no blob document |

A failed extension never aborts the document write.

## 8. Formats and Limits

| Item | Rule |
| --- | --- |
| JPEG | `image/jpeg` |
| PNG | `image/png` |
| WebP | `image/webp` |
| GIF | `image/gif` |
| Maximum blob | 32 MiB |
| Maximum AI payload | 20 MiB |
| OCR text | 1 MiB |
| EXIF JSON | 256 KiB |
| Dimensions | Positive integers; omit if unknown |

- MIME detection uses extension plus magic bytes.
- A mismatch is a warning; `weave-image` rejects unsupported media types with
  `UNSUPPORTED_IMAGE`.
- Animated GIF/WebP are stored as-is; only the first frame is used for vision/OCR.
- HEIC/AVIF are not supported in the first slice.

## 9. Dependency and Installation

`weave-image` requires:

- `weave >= 1.1.0` for generic blob assets;
- `weave-ai >= 1.1.0` for vision.

The installer:

- installs `weave-image` to the user-level bin directory;
- checks for `weave-ai` and installs it into the same directory if missing;
- verifies `weave-ai --version` and the minimum version;
- supports `--no-ai` to skip automatic installation;
- prints actionable errors when `weave` is too old or missing.

At runtime:

- `weave-image` locates `weave-ai` on `PATH` or in the bundle’s `.weave/bin/`;
- missing or old `weave-ai` yields `MISSING_DEPENDENCY` with the install command;
- `weave-image --describe` reports the exact requirements.

Homebrew/Scoop dependencies are a later delivery concern; `go install` users install both binaries
and receive the runtime check.

## 10. Retrieval and Search

All retrieval is generic core behavior:

- `weave show <id> --out image.ext` writes the original image;
- `weave show --json` returns metadata, media type, hash, size, EXIF, dimensions and OCR text;
- MCP returns `weave://blob/<id>` or `weave://source/<alias>/blob/<id>` as a blob;
- search uses OCR text as FTS body and title/description/keywords from AI;
- no image-specific search or retrieval in core.

## 11. Testing

- OCR precedence: local OCR text wins over vision transcription.
- No OCR: vision text is used.
- No OCR and no vision text: metadata-only search works.
- EXIF stored and sent to `weave-ai`.
- AI fills only empty title/description; declared metadata wins.
- JPEG, PNG, WebP, GIF fixtures; unsupported format warning.
- AI missing, timeout, malformed response and missing model fallbacks.
- Installer installs `weave-ai` and enforces the minimum version.
- `weave-image --describe --json` capability shape.
- Full gate, race suite and no network in unit tests.

Behavior scenarios are planned in `weave-image/docs/bdd/image.md`; the core blob scenarios stay in
`weave/docs/bdd/blob-assets.md`.

## 12. Acceptance Criteria

1. `weave ingest --assets --with-enricher image` ingests supported images into blob documents.
2. OCR text is stored in `content_metadata.text` and is searchable.
3. EXIF and dimensions are stored and EXIF is sent to the configured AI provider.
4. AI fills empty title/description and appends keywords; declared values win.
5. `show --out` and MCP return the exact image bytes.
6. `weave-image` never writes the database or creates tables.
7. The installer installs a vision-capable `weave-ai` and runtime checks the version.
8. Failed AI/OCR leaves a usable image document with warnings.
9. Core has no image-specific branches.

## Related Documents

- [Generic Blob Assets](blob-assets.md)
- [ADR 0004: Generic Blob Assets and Content Metadata](../architecture/adr/0004-generic-blob-assets-and-content-metadata.md)
- [Weave AI Extension](weave-ai-plugin.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [Embeddings](embeddings.md)
- [ROADMAP](../ROADMAP.md)
