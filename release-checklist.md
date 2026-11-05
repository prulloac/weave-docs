# Release Checklist

This checklist records the release state. Tag and publish steps are owner actions.

# v1.0.0

## Complete

- [x] Feature register shipped, with optimization marked post-GA stretch.
- [x] ADR 0004, 0005 and 0006 accepted; media and embedding specs/BDD approved.
- [x] `weave-ai` vision and embedding requests, provider payloads, 32 MiB stdin and 20 MiB image cap
  covered by tests.
- [x] Core schema v7 body split: text bodies stay raw, binary bodies use `body_compressed` with zstd
  by default.
- [x] Blob ingestion and retrieval, MCP blob resources and raw export implemented and tested.
- [x] Codec extension resolution, manifest validation and round-trip tests implemented.
- [x] Durable embeddings with per-space `vec0`, semantic search, audit findings and re-embedding
  implemented and tested.
- [x] Enrichment persists title, description, text, metadata and warnings; extension warnings are
  counted without discarding local metadata.
- [x] `weave-image` repository with OCR, EXIF, dimensions, `weave-ai` vision, best-effort fallbacks,
  installers, CI and tests.
- [x] `weave-codec-lz4` repository with the raw codec protocol, manifest, installers, CI and tests.
- [x] Version floors aligned: `weave-image` requires `weave >= 1.0.0` and `weave-ai >= 1.0.0`.
- [x] Real vision validated with `weave-ai` and Ollama `qwen2.5vl:3b`; title and description stored
  with zero warnings.
- [x] Real embeddings validated with Ollama `embeddinggemma-2:latest`; semantic search returned the
  expected document.
- [x] Release dry run built six static targets and verified checksums for `weave-ai`,
  `weave-codec-lz4`, `weave` and `weave-image` at `v1.0.0`.
- [x] Installers validated for the previous `weave` and `weave-ai` v1.0.0 assets (shell and
  PowerShell); `weave-image` and `weave-codec-lz4` shell installers validated against local
  release-base overrides, and their PowerShell installers pass parser checks.
- [x] Repository gates pass locally: `weave`, `weave-image` and `weave-codec-lz4` `verify.sh`.
- [x] CI on `main` passed before the version-floor alignment: `weave-ai` (`41754981087`),
  `weave` (`41955725462`), `weave-image` (`41955463694`), `weave-codec-lz4` (`41955463584`).
- [ ] CI on `main` rerun after the version-floor alignment.

## Release actions

- [ ] Remove the previous `weave` and `weave-ai` `v1.0.0` releases and tags.
- [ ] Tag the current `main` heads as `v1.0.0` in all four repositories and push the tags.
- [ ] Review the four draft releases, then publish in order: `weave-ai`, `weave-codec-lz4`,
  `weave`, `weave-image`.
- [ ] After `weave-ai` is published, run the `weave-image` installer without `--no-ai` to exercise
  the automatic `weave-ai >= 1.0.0` dependency install.
- [ ] Verify all four installers against the published assets on Linux and Windows.

## Notes

- This release supersedes the earlier v1.0.0 artifacts. The previous `weave` and `weave-ai` releases
  and tags are removed before re-tagging.
- `weave-image` requires `weave >= 1.0.0` and `weave-ai >= 1.0.0`.
- Publish `weave-ai` before running the `weave-image` installer so the dependency install resolves.
- Publishing remains manual; a tag push only creates a draft release.
- The performance optimization program is a post-GA stretch goal and does not block this tag.
